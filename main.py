import os
import traceback
import argparse
import platform

import lexico
from tabulate import tabulate
from nos import *
from analisador import Parser
from impressor import print_custom_ast
from semantico import SemanticAnalyzer, SemanticError
from gerador_assembly import AssemblyGenerator

def fase_lexica(codigo):
    print("\n--- FASE 1: Análise Léxica ---")
    tokens = lexico.lexical_analyzer(codigo)
    print("Tokens encontrados:")
    print(tabulate(tokens, headers=["Tipo", "Valor"])) 
    return tokens

def fase_sintatica(tokens):
    print("\n--- FASE 2: Análise Sintática ---")
    parser = Parser(tokens)
    ast = parser.parse_program()
    print("Árvore Sintática Abstrata (AST) gerada:")
    print_custom_ast(ast) 
    return ast

def fase_semantica(ast):
    print("\n--- FASE 3: Análise Semântica ---")
    analyzer = SemanticAnalyzer()
    return analyzer.analyze(ast) 

def fase_geracao_codigo(ast):
    print("\n--- FASE 4: Geração de Código Assembly ---")
    gerador = AssemblyGenerator()
    return gerador.generate(ast)

def analisar_codigo_c(caminho_arquivo, gerar_arquivo=True, imprimir_arvore=True):
    print(f"\n--- Analisando o arquivo '{caminho_arquivo}' ---")
    ast = None
    assembly_code = None
    
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            codigo = f.read()

        # Fases do compilador
        tokens = fase_lexica(codigo)
        ast = fase_sintatica(tokens)
        ast = fase_semantica(ast) 

    except FileNotFoundError:
        print(f"ERRO: Arquivo '{caminho_arquivo}' não encontrado.")
    except SyntaxError as e:
        print(f"\nERRO DE SINTAXE: {e}")
    except SemanticError as e:
        print(f"\nERRO SEMÂNTICO: {e}") 
        traceback.print_exc()
        print(f"\nERRO inesperado durante a análise: {e}")
    
    finally:
        if ast:
            print("\n--- FASE 4: Geração de Código Assembly ---")
            
            try:
                assembly_code = fase_geracao_codigo(ast)
                print("Código Assembly gerado:")
                print("="*40)
                print(assembly_code)
                print("="*40)

                if gerar_arquivo:
                    output_filename = os.path.splitext(caminho_arquivo)[0] + ".asm"
                    with open(output_filename, "w") as f:
                        f.write(assembly_code)
                    print(f"Código Assembly salvo em: '{output_filename}'")

            except Exception as gen_error:
                print(f"ERRO DURANTE A GERAÇÃO DE CÓDIGO: {gen_error}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compilador Simples para C subset")
    parser.add_argument("arquivo", nargs="?", help="Arquivo .c para compilar (ex: programa.c)")
    args = parser.parse_args()

    if args.arquivo:
        analisar_codigo_c(args.arquivo)
    else:
        exemplo_valido = "exemplo_valido.c"
        exemplo_invalido = "exemplo_invalido.c"

        c_code_valid = """
int main() {
    int x = 10;
    int y;
    int i;
    y = x + 5;

    if (x > y) {
        printf("maior");
    }

    for (i = 0; i < 3; i = i + 1) {
        y = y - 1;
    }

    return 0;
}
"""
        with open(exemplo_valido, "w", encoding="utf-8") as f:
            f.write(c_code_valid)
        analisar_codigo_c(exemplo_valido)

        print("\n" + "="*60 + "\n")

        c_code_invalid = """
int minhaFuncao() {
    return "um texto"; // ERRO: Espera int, retorna string
}
"""
        with open(exemplo_invalido, "w", encoding="utf-8") as f:
            f.write(c_code_invalid)
        analisar_codigo_c(exemplo_invalido)
