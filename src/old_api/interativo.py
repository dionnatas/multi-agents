"""
Módulo interativo para a API antiga da OpenAI (Assistants API).

Este módulo fornece uma interface interativa de linha de comando para
o usuário fazer perguntas usando a API antiga da OpenAI.
"""

import os
import sys
from ..processar_old_api import processar_pergunta_old_api

def main_interativo_old_api():
    """
    Função principal que implementa a interface interativa para a API antiga.
    
    Permite ao usuário fazer perguntas continuamente até digitar 'sair'.
    """
    print("\n=== Sistema Educacional de Perguntas e Respostas ===")
    print("=== Usando a API Antiga (Assistants API) ===")
    print("Digite 'sair' a qualquer momento para encerrar o programa.")
    print("------------------------------------------------------")
    
    # Verificar se a variável de ambiente OPENAI_API_KEY está configurada
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERRO: OPENAI_API_KEY não está configurada. Por favor, execute o script run.sh.")
        return
    
    while True:
        # Solicitar pergunta ao usuário
        pergunta = input("\nDigite sua pergunta: ")
        
        # Verificar se o usuário deseja sair
        if pergunta.lower() in ['sair', 'exit', 'quit']:
            print("Encerrando o programa. Até logo!")
            break
        
        # Ignorar perguntas vazias
        if not pergunta.strip():
            print("Por favor, digite uma pergunta válida.")
            continue
        
        try:
            # Processar a pergunta usando a API antiga
            print("\nProcessando sua pergunta...")
            resposta = processar_pergunta_old_api(pergunta)
            
            # Exibir a resposta
            print("\n=== Resposta ===")
            print(resposta)
            print("================")
            
        except Exception as e:
            print(f"\nErro ao processar a pergunta: {str(e)}")
            print("Por favor, tente novamente.")

if __name__ == "__main__":
    main_interativo_old_api()
