# FASE 1: DEFINIÇÃO DAS CLASSES DA ARVOREAST 
# Estas classes representam os nós da árvore.

# nó generico, garante as subclasses sejam tratadas
class Node:
    pass

# definição de função
class FunctionDefinition(Node):
    def __init__(self, name, return_type, body):
        self.name = name
        self.return_type = return_type
        self.body = body

# declaração de variável
class Declaration(Node):
    def __init__(self, var_type, name, initial_value=None):
        self.var_type = var_type
        self.name = name
        self.initial_value = initial_value

# atribuição de valor
class Assignment(Node):
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs

# operação binaria
class BinaryOperation(Node):
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right

class UnaryOperation(Node):
    def __init__(self, op, operand, is_postfix=True):
        self.op = op
        self.operand = operand
        self.is_postfix = is_postfix

# condicional IF
class IfStatement(Node):
    def __init__(self, condition, true_body, false_body=None):
        self.condition = condition
        self.true_body = true_body
        self.false_body = false_body

# loop FOR
class ForStatement(Node):
    def __init__(self, init, cond, incr, body):
        self.init = init
        self.cond = cond
        self.incr = incr
        self.body = body

# loop WHILE
class WhileStatement(Node):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

# loop DO ... WHILE
class DoWhileStatement(Node):
    def __init__(self, body, condition):
        self.body = body
        self.condition = condition

# chamada de função
class FunctionCall(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args

# retorno de função
class ReturnStatement(Node):
    def __init__(self, value):
        self.value = value

# bloco de código
class CompoundStatement(Node):
    def __init__(self, statements):
        self.statements = statements

# identificador
class Identifier(Node):
    def __init__(self, name):
        self.name = name

# constante
class Constant(Node):
    def __init__(self, value, const_type):
        self.value = value
        self.const_type = const_type