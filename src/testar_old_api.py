#!/usr/bin/env python3
"""
Script para testar a API antiga da OpenAI após a refatoração.

Este script testa a funcionalidade básica da API antiga refatorada.
"""

import os
import sys

# Adiciona o diretório atual ao path para permitir importações diretas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa a função de processamento da API antiga
from old_api.processador import processar_pergunta

def main():
    """Função principal para testar a API antiga."""
    # Verifica se a chave da API está configurada
    if "OPENAI_API_KEY" not in os.environ:
        print("ERRO: OPENAI_API_KEY não está configurada.")
        print("Por favor, execute o script run.sh para configurar a variável de ambiente.")
        return 1
    
    # Pergunta de teste
    pergunta = "Qual é a capital do Brasil?"
    print(f"\nProcessando pergunta: '{pergunta}'")
    
    # Processa a pergunta
    resposta = processar_pergunta(pergunta)
    
    # Exibe a resposta
    print("\n=== Resposta ===")
    print(resposta)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
