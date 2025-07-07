# semantico.py

from nos import *

class SemanticError(Exception):
    """Classe para erros semânticos."""
    pass

class Symbol:
    def __init__(self, name, symbol_type, category='variable', params=None):
        self.name = name
        self.type = symbol_type
        self.category = category
        self.param_types = params if params else []
        self.is_used = False
        self.offset = None


class SymbolTable:
    def __init__(self):
        self.scopes = [{}]

    def push_scope(self):
        self.scopes.append({})

    def pop_scope(self):
        """Remove o escopo atual e verifica por variáveis não utilizadas."""
        last_scope = self.scopes.pop()
        for name, symbol in last_scope.items():
            # Desconsideramos funções por enquanto, focando em variáveis
            if not symbol.is_used:
                print(f"[AVISO SEMÂNTICO] Variável '{name}' foi declarada mas nunca utilizada.")

    def add_symbol(self, symbol):
        name = symbol.name
        if name in self.scopes[-1]:
            raise SemanticError(f"Erro: Símbolo '{name}' já declarado neste escopo.")
        print(f"[SEMANTICO] Declarando '{name}' com tipo '{symbol.type}' (categoria: {symbol.category})")
        self.scopes[-1][name] = symbol

    def lookup_symbol(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

class SemanticAnalyzer:
    """
    Percorre a AST (padrão Visitor) para realizar a análise semântica.
    """
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.current_function = None
        self._preload_symbols() # <-- ADICIONE ESTA LINHA

    def _preload_symbols(self):
        # Pré-carrega funções padrão da biblioteca C
        printf_symbol = Symbol(
            name='printf',
            symbol_type='int', # printf retorna um int (número de caracteres impressos)
            category='function',
            params=[] # Simplificação: não vamos checar os parâmetros por enquanto
        )
        self.symbol_table.add_symbol(printf_symbol)

    def visit(self, node):
        """Método dispatcher que chama o método 'visit_' apropriado."""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Visita os filhos de um nó genérico."""
        # Esta implementação genérica pode não ser necessária se todos os nós forem tratados.
        raise SemanticError(f"Nó não esperado na análise semântica: {type(node).__name__}")

    def analyze(self, ast_root):
        """Ponto de entrada para iniciar a análise."""
        print("\n--- Iniciando Análise Semântica ---")
        for node in ast_root:
            self.visit(node)
        print("--- Análise Semântica Concluída com Sucesso ---")
        return ast_root  # <-- ADICIONE ESTA LINHA
    
    def visit_list(self, node_list):
        for node in node_list:
            self.visit(node)

    def visit_FunctionDefinition(self, node):
        func_name = node.name
        return_type = node.return_type
        param_types = [] 

        func_symbol = Symbol(func_name, return_type, 'function', params=param_types)
        
        # A chamada agora está correta.
        self.symbol_table.add_symbol(func_symbol)
        
        self.current_function = func_symbol
        
        # CORREÇÃO 2: A criação do escopo foi removida daqui.
        # self.symbol_table.push_scope() <--- REMOVIDO
        
        self.visit(node.body)
        
        # self.symbol_table.pop_scope() <--- REMOVIDO
        self.current_function = None

        self.visit(node.body)
        
        self.symbol_table.pop_scope()
        self.current_function = None

    def visit_CompoundStatement(self, node):
        # CORREÇÃO 2: Este método agora é o único responsável por criar escopos para blocos.
        self.symbol_table.push_scope()
        for statement in node.statements:
            self.visit(statement)
        self.symbol_table.pop_scope()

    def visit_Declaration(self, node):
        # CORREÇÃO 1: Cria o objeto Symbol antes de adicionar.
        var_symbol = Symbol(node.name, node.var_type, 'variable')
        self.symbol_table.add_symbol(var_symbol)
        
        if node.initial_value:
            rhs_type = self.visit(node.initial_value)
            lhs_type = node.var_type
            if rhs_type != lhs_type:
                raise SemanticError(f"Erro: Tipo incompatível na declaração. Não se pode atribuir '{rhs_type}' à variável '{node.name}' do tipo '{lhs_type}'.")
    
    def visit_Assignment(self, node):
        # Verifica se a variável à esquerda foi declarada.
        symbol = self.symbol_table.lookup_symbol(node.lhs.name)
        if not symbol:
            raise SemanticError(f"Erro: Variável '{node.lhs.name}' não foi declarada.")
        
        # ## CORREÇÃO AQUI ##
        # A variável à esquerda (LHS) também está sendo usada.
        # Se não marcarmos aqui, uma variável que só recebe valores mas nunca é lida
        # seria incorretamente marcada como "não utilizada".
        symbol.is_used = True

        # Obtém o tipo do lado direito da atribuição.
        rhs_type = self.visit(node.rhs)
        lhs_type = symbol.type

        # Verifica se os tipos são compatíveis.
        if lhs_type != rhs_type:
            raise SemanticError(f"Erro: Atribuição de tipo incompatível. Não se pode atribuir '{rhs_type}' à variável '{symbol.name}' do tipo '{lhs_type}'.")

    def visit_BinaryOperation(self, node):
        left_type = self.visit(node.left)
        right_type = self.visit(node.right)

        if node.op in ['+', '-', '*', '/']:
            if not (left_type == 'int' and right_type == 'int'):
                raise SemanticError(f"Erro: Operação aritmética '{node.op}' requer operandos do tipo 'int'.")
            return 'int'
        
        elif node.op in ['<', '>', '<=', '>=', '==', '!=']:
            if left_type != right_type:
                raise SemanticError(f"Erro: Operação de comparação '{node.op}' requer operandos do mesmo tipo.")
            return 'bool'
            
        ## NOVO: Verificação para operadores lógicos ##
        elif node.op in ['&&', '||']:
            if not (left_type == 'bool' and right_type == 'bool'):
                 raise SemanticError(f"Erro: Operação lógica '{node.op}' requer operandos do tipo 'bool'.")
            return 'bool'
        
        else:
            raise SemanticError(f"Operador binário desconhecido ou não implementado: {node.op}")


    def visit_Identifier(self, node):
        symbol = self.symbol_table.lookup_symbol(node.name)
        if not symbol:
            raise SemanticError(f"Erro: Variável '{node.name}' não foi declarada.")
        
        # MARCAMOS O SÍMBOLO COMO USADO
        symbol.is_used = True
        
        return symbol.type

    def visit_Constant(self, node):
        # Retorna o tipo da constante.
        if node.const_type == 'string':
            return 'string'
        # Seu parser define 'int' para todos os números, o que é suficiente por agora.
        return 'int'

    def visit_IfStatement(self, node):
        ## MELHORADO: Verificação explícita da condição ##
        condition_type = self.visit(node.condition)
        if condition_type != 'bool':
            raise SemanticError(f"Erro: A condição de um 'if' deve ser do tipo 'bool', mas foi '{condition_type}'.")
        self.visit(node.true_body)
        if node.false_body:
            self.visit(node.false_body)
            
    def visit_ForStatement(self, node):
        self.symbol_table.push_scope()
        if node.init:
            self.visit(node.init)
        if node.cond:
            cond_type = self.visit(node.cond)
            if cond_type != 'bool':
                raise SemanticError(f"Erro: Condição do 'for' deve ser booleana, mas foi '{cond_type}'.")
        if node.incr:
            self.visit(node.incr)
        self.visit(node.body)
        self.symbol_table.pop_scope()

    def visit_WhileStatement(self, node):
        condition_type = self.visit(node.condition)
        if condition_type != 'bool':
            raise SemanticError(f"Erro: A condição de um 'while' deve ser do tipo 'bool', mas foi '{condition_type}'.")
        self.visit(node.body)

    def visit_DoWhileStatement(self, node):
        self.visit(node.body)
        condition_type = self.visit(node.condition)
        if condition_type != 'bool':
            raise SemanticError(f"Erro: Condição do 'do-while' deve ser booleana, mas foi '{condition_type}'.")

    def visit_FunctionCall(self, node):
        func_name = node.name.name

        # Condição especial para funções built-in como printf
        if func_name == 'printf':
            # Apenas visita os argumentos sem checar quantidade ou tipo
            for arg_node in node.args:
                self.visit(arg_node)
            return 'int' # Retorna o tipo de retorno de printf

        symbol = self.symbol_table.lookup_symbol(func_name)

        if not symbol:
            raise SemanticError(f"Erro: Função '{func_name}' não foi declarada.")
        if symbol.category != 'function':
            raise SemanticError(f"Erro: '{func_name}' não é uma função, é uma '{symbol.category}'.")

        expected_params_count = len(symbol.param_types)
        actual_args_count = len(node.args)
        if expected_params_count != actual_args_count:
            raise SemanticError(f"Erro: Função '{func_name}' espera {expected_params_count} argumentos, mas recebeu {actual_args_count}.")

        # Verificar tipo de cada argumento
        for i, arg_node in enumerate(node.args):
            actual_type = self.visit(arg_node)
            expected_type = symbol.param_types[i]
            if actual_type != expected_type:
                raise SemanticError(f"Erro: Argumento {i+1} da chamada da função '{func_name}' é do tipo incorreto. Esperado '{expected_type}', mas foi '{actual_type}'.")

        return symbol.type
    
    def visit_ReturnStatement(self, node):
        ## NOVO: Verificação completa do tipo de retorno ##
        if not self.current_function:
            raise SemanticError("Erro: Declaração 'return' encontrada fora de uma função.")
        
        expected_type = self.current_function.type
        
        if node.value is None: # Caso: return;
            if expected_type != 'void':
                raise SemanticError(f"Erro: A função '{self.current_function.name}' deve retornar um valor do tipo '{expected_type}', mas retornou vazio.")
        else: # Caso: return <expressao>;
            if expected_type == 'void':
                raise SemanticError(f"Erro: Uma função 'void' ('{self.current_function.name}') não pode retornar um valor.")
            
            actual_type = self.visit(node.value)
            if actual_type != expected_type:
                raise SemanticError(f"Erro: Tipo de retorno incompatível na função '{self.current_function.name}'. Esperado '{expected_type}', mas encontrado '{actual_type}'.")