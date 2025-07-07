import re
from tabulate import tabulate

# Palavras-chave
KEYWORDS = {
    'auto', 'break', 'case', 'char', 'const', 'continue', 'default',
    'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto',
    'if', 'else', 'int', 'long', 'register', 'return', 'short', 'signed',
    'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
    'unsigned', 'void', 'volatile', 'while', 'printf', 'scanf'
}

def lexical_analyzer(code):
    # Realiza a análise léxica do código C e retorna uma lista de tokens.
    token_specification = [
        ('COMMENT',      r'//.*|/\*[\s\S]*?\*/'),
        ('STRING',       r'"([^"\\]|\\.)*"'),
        ('NUMBER',       r'\b\d+(\.\d+)?\b'),
        ('IDENTIFIER',   r'\b[a-zA-Z_][a-zA-Z_0-9]*\b'),
        ('OPERATOR',     r'==|!=|<=|>=|&&|\|\||[+\-*/=<>!]'),
        ('DELIMITER',    r'[(){};,]'),
        ('NEWLINE',      r'\n'),
        ('SKIP',         r'[ \t]+'),
        ('MISMATCH',     r'.'),
    ]

    tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
    tokens = []
    
    for match in re.finditer(tok_regex, code):
        kind = match.lastgroup
        value = match.group()

        if kind == 'IDENTIFIER' and value in KEYWORDS:
            kind = 'KEYWORD'
        elif kind in {'SKIP', 'COMMENT', 'NEWLINE'}:
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'Token inválido: {value}')
        
        tokens.append((kind, value))
    
    return tokens

# Exemplo de uso
if __name__ == '__main__':
    c_code = '''
    int main() {
        int x = 10;
        int y;

        if (x > 5) {
            y = 20;
            printf("x e maior que 5\n");
        }

        for (int i = 0; i < 3; i = i + 1) {
            printf("loop");
        }

        return 0;
    }
    '''
    tokens = lexical_analyzer(c_code)
    print(tabulate(tokens, headers=["Tipo", "Token"]))
