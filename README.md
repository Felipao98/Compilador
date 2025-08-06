# 🚀 Compilador Didático de C para Assembly x86

![Linguagem](https://img.shields.io/badge/Linguagem-Python-blue.svg)
![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow.svg)
![Licença](https://img.shields.io/badge/Licen%C3%A7a-MIT-green.svg)

## 📖 Sobre o Projeto

Este repositório contém a implementação de um compilador completo, embora simplificado, para um subconjunto da linguagem C. O projeto foi desenvolvido em Python puro, com o objetivo de aplicar e demonstrar na prática as etapas fundamentais do processo de compilação: da análise de texto à geração de código de máquina.

O compilador pega um arquivo `.c` como entrada, processa-o através de quatro fases distintas e gera um arquivo `.asm` com código Assembly (sintaxe NASM) como saída.

---

## ✨ Funcionalidades Implementadas

A linguagem C suportada por este compilador inclui:
-   ✅ **Funções**: Definição de `int main()` e outras funções sem parâmetros.
-   ✅ **Variáveis**: Declaração e inicialização de variáveis do tipo `int`.
-   ✅ **Operadores**:
    -   Aritméticos: `+`, `-`, `*`, `/`
    -   De Comparação: `>`, `<`, `==`, `!=`, `>=`, `<=`
-   ✅ **Estruturas de Controle**:
    -   Condicionais `if` e `if-else`.
    -   Laços de repetição `for` e `while`.
-   ✅ **Chamadas de Sistema**: Suporte à função `printf` para impressão de strings.
-   ✅ **Controle de Fluxo**: Instrução `return` para finalizar a execução da função.

---

## 🏗️ Arquitetura do Compilador

O projeto é dividido em módulos que representam as fases clássicas da compilação, garantindo um código organizado e de fácil manutenção.

### Fase 1: Análise Léxica (`lexico.py`)
O "Lexer" lê o código-fonte e o divide em uma lista de **tokens**. Cada token é uma unidade fundamental da linguagem, como uma palavra-chave (`int`), um identificador (`x`), um número (`10`) ou um operador (`=`).

### Fase 2: Análise Sintática (`analisador.py`)
O "Parser" recebe os tokens e verifica se eles formam uma estrutura gramaticalmente válida. Se a sintaxe estiver correta, ele organiza os tokens em uma **Árvore Sintática Abstrata (AST)**. A AST é uma representação hierárquica do código, essencial para as próximas fases.

### Fase 3: Análise Semântica (`semantico.py`)
Com a estrutura sintática validada, esta fase verifica se o código faz sentido. Utilizando uma **Tabela de Símbolos** para rastrear variáveis e seus tipos, ela impõe regras como:
-   Toda variável deve ser declarada antes do uso.
-   Não é permitido somar um número com um texto.
-   O tipo de retorno de uma função deve ser respeitado.

### Fase 4: Geração de Código (`gerador_assembly.py`)
A fase final percorre a AST já validada e a traduz, instrução por instrução, para código Assembly x86. Ela gerencia a pilha (stack) para alocação de variáveis locais e utiliza registradores (`eax`, `ebx`) para realizar cálculos.

---

## 🛠️ Como Usar

### Pré-requisitos
-   Python 3.8+
-   [NASM](https://www.nasm.us/) (para montar o código Assembly)
-   [GCC](https://gcc.gnu.org/) (ou outro linker, para criar o executável)

### Instalação
1.  Clone o repositório:
    ```bash
    git clone [https://coderefinery.github.io/github-without-command-line/doi/](https://coderefinery.github.io/github-without-command-line/doi/)
    cd [nome-do-repositorio]
    ```
2.  Instale a dependência Python:
    ```bash
    pip install tabulate
    ```

### Executando o Compilador
Para compilar um arquivo, execute o `main.py`:
```bash
python main.py seu_codigo.c
```
Isso gerará um arquivo `seu_codigo.asm`.

### Montando e Linkando o Assembly (Exemplo para Linux)
```bash
# Montar o arquivo .asm para criar um arquivo objeto .o
nasm -f elf32 seu_codigo.asm -o seu_codigo.o

# Linkar o arquivo objeto com a biblioteca C (para usar printf) e criar o executável
gcc -m32 seu_codigo.o -o seu_programa

# Executar!
./seu_programa
```

---

## 📁 Estrutura do Repositório
```
.
├── main.py                # Orquestrador principal do compilador
├── lexico.py              # Fase 1: Analisador Léxico
├── analisador.py          # Fase 2: Analisador Sintático (Parser)
├── nos.py                 # Definição das classes dos nós da AST
├── semantico.py           # Fase 3: Analisador Semântico
├── gerador_assembly.py    # Fase 4: Gerador de Código Assembly
├── impressor.py           # Utilitário para imprimir a AST de forma hierárquica
├── exemplo_valido.c       # Código de exemplo que compila com sucesso
└── exemplo_invalido.c     # Código de exemplo com erro semântico
```

---

## 🚀 Próximos Passos
-   [ ] Suporte a mais tipos de dados (`float`, `char`).
-   [ ] Implementação de ponteiros e arrays.
-   [ ] Otimizações simples no código Assembly gerado.
-   [ ] Melhorar o tratamento de erros e mensagens.
