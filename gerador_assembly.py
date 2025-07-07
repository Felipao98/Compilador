from nos import *
from semantico import SymbolTable 

class AssemblyGenerator:
    def __init__(self): 
        self.code = []
        self.text_section = []
        self.data_section = []
        self.string_counter = 0
        self.variable_offsets_stack = [{}]
        self.current_offset = 0
        self.label_counter = 0

    def push_scope(self):
        self.variable_offsets_stack.append({})

    def pop_scope(self):
        self.variable_offsets_stack.pop()

    def add_variable(self, name):
        self.current_offset -= 4
        self.variable_offsets_stack[-1][name] = self.current_offset

    def get_variable_offset(self, name):
        for scope in reversed(self.variable_offsets_stack):
            if name in scope:
                return scope[name]
        # Este erro não deve ocorrer se o analisador semântico fez seu trabalho
        raise NameError(f"Erro de Geração: Offset para a variável '{name}' não encontrado.")

    def generate(self, ast_root):
        header = ["section .data"]
        header.extend(self.data_section)
        header.append("\nsection .text")
        header.append("extern printf")
        self.text_section = header
        
        self.visit(ast_root)
        return "\n".join(self.text_section)

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name,self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        raise Exception(f"Nenhum método visit_{type(node).__name__} encontrado")

    def visit_list(self, node_list):
        for node in node_list:
            self.visit(node)

    def visit_FunctionDefinition(self, node):
        self.text_section.append(f"global {node.name}")
        self.text_section.append(f"\n{node.name}:")
        self.text_section.append("  push ebp")
        self.text_section.append("  mov ebp, esp")
        self.visit(node.body)
    
    def visit_CompoundStatement(self, node):
        self.push_scope()
        for statement in node.statements:
            self.visit(statement)
        self.pop_scope()
    
    def visit_Declaration(self, node):
        self.add_variable(node.name)
        self.code.append(f"  sub esp, 4 ; Aloca espaço para '{node.name}'")  #no offset {self.get_variable_offset(node.name)}")
        if node.initial_value:
            self.visit(Assignment(Identifier(node.name), node.initial_value))
    
    def visit_Assignment(self, node):
        self.visit(node.rhs) # Resultado do lado direito vai para EAX
        
        offset = self.get_variable_offset(node.lhs.name)
        self.code.append(f"  mov [ebp{offset}], eax") # Atribui a 'node.lhs.name'
    
    def visit_BinaryOperation(self, node):
        self.visit(node.right)
        self.text_section.append("  push eax")
        self.visit(node.left)
        self.text_section.append("  pop ebx")
        op_map = {'+': 'add', '-': 'sub', '*': 'imul', '<': 'jl', '>': 'jg', '==': 'je', '!=': 'jne'}
        if node.op in ['+', '-', '*', '/']:
            if node.op == '/':
                self.text_section.append("  cdq")
                self.text_section.append("  idiv ebx")
            else:
                self.text_section.append(f"  {op_map[node.op]} eax, ebx")
        elif node.op in op_map: # Para operadores de comparação
            true_label = f".Ltrue{self.label_counter}"
            end_label = f".Lend_cmp{self.label_counter}"
            self.label_counter += 1
            self.text_section.append("  cmp eax, ebx")
            self.text_section.append(f"  {op_map[node.op]} {true_label}")
            self.text_section.append("  mov eax, 0 ; False")
            self.text_section.append(f"  jmp {end_label}")
            self.text_section.append(f"{true_label}:")
            self.text_section.append("  mov eax, 1 ; True")
            self.text_section.append(f"{end_label}:")
        
    def visit_Identifier(self, node):
        offset = self.get_variable_offset(node.name)
        self.code.append(f"  mov eax, [ebp{offset}]") # ; Carrega '{node.name}'

    def visit_Constant(self, node):
        # Carrega um valor constante para EAX
        self.code.append(f"  mov eax, {node.value}")
    
    def visit_ReturnStatement(self, node):
        if node.value:
            self.visit(node.value)
        self.text_section.append("  mov esp, ebp")
        self.text_section.append("  pop ebp")
        self.text_section.append("  ret")
        
    def visit_IfStatement(self, node):
        else_label = f".Lelse{self.label_counter}"
        end_label = f".Lend_if{self.label_counter}"
        self.label_counter += 1
        self.visit(node.condition)
        self.text_section.append("  cmp eax, 0")
        self.text_section.append(f"  je {else_label if node.false_body else end_label}")
        self.visit(node.true_body)
        if node.false_body:
            self.text_section.append(f"  jmp {end_label}")
            self.text_section.append(f"{else_label}:")
            self.visit(node.false_body)
        self.text_section.append(f"{end_label}:")
        
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

    def visit_ForStatement(self, node):
        start_label = f".Lfor_start{self.label_counter}"
        end_label = f".Lfor_end{self.label_counter}"
        self.label_counter += 1
        if node.init: self.visit(node.init)
        self.text_section.append(f"{start_label}:")
        if node.cond:
            self.visit(node.cond)
            self.text_section.append("  cmp eax, 0")
            self.text_section.append(f"  je {end_label}")
        self.visit(node.body)
        if node.incr: self.visit(node.incr)
        self.text_section.append(f"  jmp {start_label}")
        self.text_section.append(f"{end_label}:")

    def visit_FunctionCall(self, node):
        if node.name.name == 'printf':
            string_label = f'S{self.string_counter}'
            self.string_counter += 1
            # Adiciona a string na seção de dados
            self.data_section.append(f'  {string_label} db {node.args[0].value}, 10, 0')
            # Gera o código da chamada
            self.text_section.append(f"  push {string_label}")
            self.text_section.append("  call printf")
            self.text_section.append("  add esp, 4")