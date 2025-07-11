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
        last_scope = self.scopes.pop()
        for name, symbol in last_scope.items():
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
        self._preload_symbols() 

    def _preload_symbols(self):
        printf_symbol = Symbol(
            name='printf',
            symbol_type='int', 
            category='function',
            params=[] 
        )
        self.symbol_table.add_symbol(printf_symbol)

    def visit(self, node):
        """Método dispatcher que chama o método 'visit_' apropriado."""
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        """Visita os filhos de um nó genérico."""
        raise SemanticError(f"Nó não esperado na análise semântica: {type(node).__name__}")

    def analyze(self, ast_root):
        """Ponto de entrada para iniciar a análise."""
        print("\n--- Iniciando Análise Semântica ---")
        self.visit(ast_root)
        print("--- Análise Semântica Concluída com Sucesso ---")
        return ast_root 
    
    def visit_list(self, node_list):
        for node in node_list:
            self.visit(node)

    def visit_FunctionDefinition(self, node):
        func_symbol = Symbol(node.name, node.return_type, 'function')
        self.symbol_table.add_symbol(func_symbol)
        self.current_function = func_symbol
        self.visit(node.body)
        self.current_function = None

    def visit_CompoundStatement(self, node):
        self.symbol_table.push_scope()
        for statement in node.statements:
            self.visit(statement)
        self.symbol_table.pop_scope()

    def visit_Declaration(self, node):
        var_symbol = Symbol(node.name, node.var_type, 'variable')
        self.symbol_table.add_symbol(var_symbol)
        if node.initial_value:
            rhs_type = self.visit(node.initial_value)
            # lhs_type = node.var_type
            if rhs_type != node.var_type: 
                raise SemanticError(f"Erro: Tipo incompatível na declaração. Não se pode atribuir '{rhs_type}' à variável '{node.name}'.") # do tipo '{lhs_type}'
    
    def visit_Assignment(self, node):
        # Verifica se a variável à esquerda foi declarada.
        symbol = self.symbol_table.lookup_symbol(node.lhs.name)
        if not symbol:
            raise SemanticError(f"Erro: Variável '{node.lhs.name}' não foi declarada.")
        
        symbol.is_used = True

        rhs_type = self.visit(node.rhs)
        if symbol.type != rhs_type:
            raise SemanticError(f"Atribuição de tipo incompatível para '{symbol.name}'.")

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
        
        symbol.is_used = True
        
        return symbol.type

    def visit_Constant(self, node):
        return node.const_type

    def visit_IfStatement(self, node):
        if self.visit(node.condition) != 'bool':
            raise SemanticError("Condição do 'if' deve ser booleana.")
        self.visit(node.true_body)
        if node.false_body: 
            self.visit(node.false_body)
            
    def visit_ForStatement(self, node):
        self.symbol_table.push_scope()
        if node.init: 
            self.visit(node.init)
        if node.cond and self.visit(node.cond) != 'bool':
            raise SemanticError("Condição do 'for' deve ser booleana.")
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

        if func_name == 'printf':
            for arg_node in node.args:
                self.visit(arg_node)
            return 'int'

        symbol = self.symbol_table.lookup_symbol(func_name)

        if not symbol or symbol.category != 'function':
            raise SemanticError(f"Erro: Função '{func_name}' não foi declarada.")
        
        return symbol.type
    
    def visit_ReturnStatement(self, node):
        if not self.current_function:
            raise SemanticError("Erro: Declaração 'return' encontrada fora de uma função.")
        
        expected = self.current_function.type
        
        actual = self.visit(node.value) if node.value else 'void'
        if actual != expected:
            raise SemanticError(f"Tipo de retorno incompatível em '{self.current_function.name}'.")
