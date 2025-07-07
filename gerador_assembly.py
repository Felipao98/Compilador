# gerador_assembly.py

from nos import *
from semantico import SymbolTable # Precisamos da tabela para encontrar as variáveis

class AssemblyGenerator:
    def __init__(self): #symbol_table
        self.code = []
        self.variable_offsets_stack = [{}]
        self.current_offset = 0
        self.label_counter = 0

    def push_scope(self):
        """Inicia um novo escopo para offsets."""
        self.variable_offsets_stack.append({})

    def pop_scope(self):
        """Finaliza o escopo atual."""
        self.variable_offsets_stack.pop()

    def add_variable(self, name):
        """Aloca espaço para uma variável na pilha e armazena seu offset."""
        self.current_offset -= 4  # Aloca 4 bytes (tamanho de um int)
        self.variable_offsets_stack[-1][name] = self.current_offset

    def get_variable_offset(self, name):
        """Busca o offset de uma variável, do escopo local para o global."""
        for scope in reversed(self.variable_offsets_stack):
            if name in scope:
                return scope[name]
        # Este erro não deve ocorrer se o analisador semântico fez seu trabalho
        raise NameError(f"Erro de Geração: Offset para a variável '{name}' não encontrado.")

    # def generate(self, ast_root):
    #     self.assembly_code.append("section .text")
    #     self.assembly_code.append("global _start")
    #     for node in ast_root:
    #         self.visit(node)
    #     return "\n".join(self.assembly_code)
    
    def generate(self, ast_root):
        self.code.append("section .text")
        for node in ast_root:
            self.visit(node)
        return "\n".join(self.code)

    # def visit(self, node):
    #     method_name = f'visit_{type(node).__name__}'
    #     visitor = getattr(self, method_name, self.generic_visit)
    #     return visitor(node)

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"Nenhum método visit_{type(node).__name__} encontrado")

    # def visit_FunctionDefinition(self, node):
    #     # Assumindo que a primeira função é o ponto de entrada '_start'
    #     self.assembly_code.append(f"\n_start:")
    #     self.assembly_code.append("  ; Prólogo da função")
    #     self.assembly_code.append("  push ebp")
    #     self.assembly_code.append("  mov ebp, esp")
        
    #     # Visita o corpo da função para gerar seu código
    #     self.visit(node.body)

        # O retorno já lida com o epílogo

    def visit_FunctionDefinition(self, node):
        # ## CORRIGIDO: Gera código para uma função C padrão (ex: 'main') ##
        self.code.append(f"global {node.name}")
        self.code.append(f"\n{node.name}:")
        self.code.append("  ; Prólogo da função")
        self.code.append("  push ebp")
        self.code.append("  mov ebp, esp")
        
        # Inicia o escopo da função para o layout de memória
        self.push_scope()
        self.visit(node.body)
        self.pop_scope()

    # def visit_CompoundStatement(self, node):
    #     for statement in node.statements:
    #         self.visit(statement)
    
    def visit_CompoundStatement(self, node):
        # ## CORRIGIDO: Gerencia escopos para blocos aninhados ##
        self.push_scope()
        for statement in node.statements:
            self.visit(statement)
        self.pop_scope()

    # def visit_Declaration(self, node):
    #     # Aloca espaço para a variável na pilha
    #     self.current_stack_offset -= 4 # Assumindo variáveis de 4 bytes (int)
    #     symbol = self.symbol_table.lookup_symbol(node.name)
    #     symbol.offset = self.current_stack_offset
    #     self.assembly_code.append(f"  sub esp, 4 ; Aloca espaço para '{node.name}' no offset {symbol.offset}")
        
    #     # Se houver valor inicial, gera o código de atribuição
    #     if node.initial_value:
    #         # Cria um nó de atribuição temporário e visita-o
    #         assignment_node = Assignment(Identifier(node.name), node.initial_value)
    #         self.visit(assignment_node)
    
    def visit_Declaration(self, node):
        # ## CORRIGIDO: Adiciona a variável ao seu próprio controle de offsets ##
        self.add_variable(node.name)
        self.code.append(f"  sub esp, 4 ; Aloca espaço para '{node.name}' no offset {self.get_variable_offset(node.name)}")
        if node.initial_value:
            assignment_node = Assignment(Identifier(node.name), node.initial_value)
            self.visit(assignment_node)

    # def visit_Assignment(self, node):
    #     # Calcula o valor do lado direito e o deixa em EAX
    #     self.visit(node.rhs)
        
    #     # Armazena o valor de EAX na posição da variável na pilha
    #     symbol = self.symbol_table.lookup_symbol(node.lhs.name)
    #     if not symbol or symbol.offset is None:
    #         raise Exception(f"Símbolo ou offset não encontrado para {node.lhs.name}")
        
    #     self.assembly_code.append(f"  mov [ebp{symbol.offset}], eax ; Atribui a '{node.lhs.name}'")
    
    def visit_Assignment(self, node):
        self.visit(node.rhs) # Resultado do lado direito vai para EAX
        
        # ## CORRIGIDO: Busca o offset em sua própria estrutura de dados ##
        offset = self.get_variable_offset(node.lhs.name)
        self.code.append(f"  mov [ebp{offset}], eax ; Atribui a '{node.lhs.name}'")

    # def visit_BinaryOperation(self, node):
    #     # Calcula o lado direito, o resultado vai para EAX. Salva na pilha.
    #     self.visit(node.right)
    #     self.assembly_code.append("  push eax")

    #     # Calcula o lado esquerdo, o resultado vai para EAX.
    #     self.visit(node.left)
        
    #     # Tira o resultado direito da pilha para EBX
    #     self.assembly_code.append("  pop ebx")

    #     # Realiza a operação
    #     if node.op == '+':
    #         self.assembly_code.append("  add eax, ebx ; EAX = EAX + EBX")
    #     elif node.op == '-':
    #         self.assembly_code.append("  sub eax, ebx ; EAX = EAX - EBX")
        # Adicionar outras operações (mul, div, etc.) aqui
        
    def visit_BinaryOperation(self, node):
        self.visit(node.right)
        self.code.append("  push eax")
        self.visit(node.left)
        self.code.append("  pop ebx")
        
        op_map = {'+': 'add', '-': 'sub', '*': 'imul'}
        if node.op in op_map:
            self.code.append(f"  {op_map[node.op]} eax, ebx ; EAX = EAX {node.op} EBX")
        elif node.op == '/':
            self.code.append("  cdq") # Necessário para divisão de sinal
            self.code.append("  idiv ebx")
        # Adicione aqui o tratamento para operadores de comparação se necessári

    # def visit_Identifier(self, node):
    #     # Carrega o valor da variável da pilha para EAX
    #     symbol = self.symbol_table.lookup_symbol(node.name)
    #     self.assembly_code.append(f"  mov eax, [ebp{symbol.offset}] ; Carrega '{node.name}'")
    
    def visit_Identifier(self, node):
        # ## CORRIGIDO: Busca o offset em sua própria estrutura de dados ##
        offset = self.get_variable_offset(node.name)
        self.code.append(f"  mov eax, [ebp{offset}] ; Carrega '{node.name}'")

    def visit_Constant(self, node):
        # Carrega um valor constante para EAX
        self.code.append(f"  mov eax, {node.value}")
        
    # def visit_ReturnStatement(self, node):
    #     # Calcula o valor de retorno e o coloca em EAX
    #     self.visit(node.value)
        
    #     # Epílogo da função
    #     self.assembly_code.append("\n  ; Epílogo da função e saída do programa")
    #     self.assembly_code.append("  mov ebx, eax ; Código de saída do programa")
    #     self.assembly_code.append("  mov eax, 1   ; Chamada de sistema para exit")
    #     self.assembly_code.append("  int 0x80     ; Interrupção do kernel")
    
    def visit_ReturnStatement(self, node):
        self.visit(node.value) # O valor de retorno estará em EAX
        
        # ## CORRIGIDO: Gera um epílogo de função padrão C ##
        self.code.append("\n  ; Epílogo da função")
        self.code.append("  mov esp, ebp")
        self.code.append("  pop ebp")
        self.code.append("  ret")
        
    def visit_IfStatement(self, node):
        label_else = f".Lelse{self.label_counter}"
        label_end = f".Lend_if{self.label_counter}"
        self.label_counter += 1

        self.visit(node.condition)
        self.code.append("  cmp eax, 0")
        self.code.append(f"  je {label_else}")
        self.visit(node.true_body)
        self.code.append(f"  jmp {label_end}")
        self.code.append(f"{label_else}:")
        if node.false_body:
            self.visit(node.false_body)
        self.code.append(f"{label_end}:")
        
    def visit_WhileStatement(self, node):
        label_start = f".Lwhile{self.label_counter}"
        label_end = f".Lend_while{self.label_counter}"
        self.label_counter += 1

        self.code.append(f"{label_start}:")
        self.visit(node.condition)
        self.code.append("  cmp eax, 0")
        self.code.append(f"  je {label_end}")
        self.visit(node.body)
        self.code.append(f"  jmp {label_start}")
        self.code.append(f"{label_end}:")

        
    