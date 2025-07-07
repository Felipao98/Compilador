from nos import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def advance(self):
        self.pos += 1
        self.current_token = self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, token_type, value=None):
        if self.current_token and self.current_token[0] == token_type:
            if value is None or self.current_token[1] == value:
                token = self.current_token
                self.advance()
                return token
        raise SyntaxError(f"Esperado token {token_type} ('{value}') mas encontrou {self.current_token}")

    def parse_program(self):
        nodes = []
        while self.current_token:
            nodes.append(self.parse_function_definition())
        return nodes

    def parse_function_definition(self):
        return_type = self.eat('KEYWORD')[1]
        name = self.eat('IDENTIFIER')[1]
        self.eat('DELIMITER', '(')
        self.eat('DELIMITER', ')')
        body = self.parse_compound_statement()
        return FunctionDefinition(name=name, return_type=return_type, body=body)

    def parse_compound_statement(self):
        self.eat('DELIMITER', '{')
        statements = []
        while self.current_token and self.current_token[1] != '}':
            statements.append(self.parse_statement())
        self.eat('DELIMITER', '}')
        return CompoundStatement(statements)

    def parse_statement(self):
        # Analisa uma única instrução.
        if not self.current_token:
            raise SyntaxError("Fim inesperado da entrada durante análise de instrução.")

        token_type, token_value = self.current_token

        # Declaração de variável
        if token_type == 'KEYWORD' and token_value in ['int', 'char', 'float']:
            return self.parse_declaration()

        # Condicional IF
        elif token_type == 'KEYWORD' and token_value == 'if':
            return self.parse_if_statement()

        # Laço FOR
        elif token_type == 'KEYWORD' and token_value == 'for':
            return self.parse_for_statement()

        # Laço WHILE
        elif token_type == 'KEYWORD' and token_value == 'while':
            return self.parse_while_statement()

        # Laço DO ... WHILE
        elif token_type == 'KEYWORD' and token_value == 'do':
            return self.parse_do_while_statement()

        # Retorno
        elif token_type == 'KEYWORD' and token_value == 'return':
            return self.parse_return_statement()

        # Chamada de função (ex: printf)
        elif token_type == 'KEYWORD' and token_value == 'printf':
            return self.parse_function_call()

        # Atribuição ou incremento (IDENTIFIER)
        elif token_type == 'IDENTIFIER':
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None

            # Atribuição tradicional: x = ...
            if next_token and next_token[0] == 'OPERATOR' and next_token[1] == '=':
                return self.parse_assignment()

            # Operadores de incremento simples: x++, x--
            elif next_token and next_token[0] == 'OPERATOR' and next_token[1] in ['++', '--']:
                lhs = Identifier(self.eat('IDENTIFIER')[1])
                op = self.eat('OPERATOR')[1]
                # Converte para uma atribuição implícita
                rhs = BinaryOperation(
                    op='+' if op == '++' else '-',
                    left=lhs,
                    right=Constant('1', 'int')
                )
                self.eat('DELIMITER', ';')
                return Assignment(lhs=lhs, rhs=rhs)

        # Se nenhum caso corresponde
        raise SyntaxError(f"Instrução inesperada iniciada com o token: {self.current_token}")


    def parse_declaration(self):
        var_type = self.eat('KEYWORD')[1]
        name = self.eat('IDENTIFIER')[1]
        initial_value = None
        if self.current_token and self.current_token[1] == '=':
            self.eat('OPERATOR', '=')
            initial_value = self.parse_expression()
        self.eat('DELIMITER', ';')
        return Declaration(var_type=var_type, name=name, initial_value=initial_value)

    def parse_assignment(self, for_header=False):
        lhs = Identifier(self.eat('IDENTIFIER')[1])

        if self.current_token[0] == 'OPERATOR' and self.current_token[1] == '=':
            self.eat('OPERATOR', '=')
            rhs = self.parse_expression()
            if not for_header:
                self.eat('DELIMITER', ';')
            return Assignment(lhs=lhs, rhs=rhs)
        elif self.current_token[0] == 'OPERATOR' and self.current_token[1] in ['++', '--']:
            op = self.eat('OPERATOR')[1]
            if not for_header:
                self.eat('DELIMITER', ';')
            return UnaryOperation(op=op, operand=lhs, is_postfix=True)
        else:
            raise SyntaxError(f"Esperado '=' ou '++/--' após identificador, mas encontrou {self.current_token}")

    def parse_if_statement(self):
        self.eat('KEYWORD', 'if')
        self.eat('DELIMITER', '(')
        condition = self.parse_expression()
        self.eat('DELIMITER', ')')
        true_body = self.parse_compound_statement()
        false_body = None
        if self.current_token and self.current_token[0] == 'KEYWORD' and self.current_token[1] == 'else':
            self.eat('KEYWORD', 'else')
            false_body = self.parse_compound_statement()
        return IfStatement(condition=condition, true_body=true_body, false_body=false_body)

    def parse_for_statement(self):
        self.eat('KEYWORD', 'for')
        self.eat('DELIMITER', '(')

        # init
        if self.current_token[0] == 'KEYWORD' and self.current_token[1] in ['int', 'char', 'float']:
            init = self.parse_declaration()
        elif self.current_token[0] == 'IDENTIFIER':
            init = self.parse_assignment(for_header=True)
            self.eat('DELIMITER', ';')
        elif self.current_token[0] == 'DELIMITER' and self.current_token[1] == ';':
            init = None
            self.eat('DELIMITER', ';')
        else:
            raise SyntaxError(f"Parte 'init' inválida no for: {self.current_token}")

        # cond
        if self.current_token[1] != ';':
            cond = self.parse_expression()
        else:
            cond = None
        self.eat('DELIMITER', ';')

        # incr
        if self.current_token[1] != ')':
            if self.current_token[0] == 'IDENTIFIER':
                incr = self.parse_assignment(for_header=True)
            else:
                incr = None
        else:
            incr = None
        self.eat('DELIMITER', ')')

        body = self.parse_compound_statement()

        return ForStatement(init=init, cond=cond, incr=incr, body=body)

    def parse_while_statement(self):
        self.eat('KEYWORD', 'while')
        self.eat('DELIMITER', '(')
        condition = self.parse_expression()
        self.eat('DELIMITER', ')')
        body = self.parse_compound_statement()
        return WhileStatement(condition=condition, body=body)

    def parse_do_while_statement(self):
        self.eat('KEYWORD', 'do')
        body = self.parse_compound_statement()
        self.eat('KEYWORD', 'while')
        self.eat('DELIMITER', '(')
        condition = self.parse_expression()
        self.eat('DELIMITER', ')')
        self.eat('DELIMITER', ';')
        return DoWhileStatement(body=body, condition=condition)

    def parse_return_statement(self):
        self.eat('KEYWORD', 'return')
        value = self.parse_expression()
        self.eat('DELIMITER', ';')
        return ReturnStatement(value)

    def parse_function_call(self):
        name = Identifier(self.eat('KEYWORD', 'printf')[1])
        self.eat('DELIMITER', '(')
        args = []
        if self.current_token[0] == 'STRING':
            args.append(Constant(self.current_token[1], 'string'))
            self.advance()
        self.eat('DELIMITER', ')')
        self.eat('DELIMITER', ';')
        return FunctionCall(name=name, args=args)

    def parse_expression(self):
        # CORREÇÃO: Removida a verificação inicial restritiva.
        # O trabalho de validar o token inicial é do parse_term.
        left = self.parse_term()
        while self.current_token and self.current_token[0] == 'OPERATOR':
            op = self.current_token[1]
            if op not in ['+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!=']:
                break
            self.eat('OPERATOR', op)
            right = self.parse_term()
            left = BinaryOperation(op=op, left=left, right=right)
        return left

    def parse_term(self):
        token_type, token_value = self.current_token
        if token_type == 'NUMBER':
            self.advance()
            return Constant(token_value, 'int')
        elif token_type == 'IDENTIFIER':
            self.advance()
            return Identifier(token_value)
        # CORREÇÃO: Adicionado suporte para strings como um termo.
        elif token_type == 'STRING':
            self.advance()
            return Constant(token_value, 'string')
        raise SyntaxError(f"Termo inesperado na expressão: {self.current_token}")