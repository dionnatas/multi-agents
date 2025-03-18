"""
Módulo interativo para a API antiga da OpenAI (Assistants API).

Este módulo fornece uma interface interativa de linha de comando para
o usuário fazer perguntas usando a API antiga da OpenAI.
"""

import os
import sys
import asyncio
from ..processar_old_api import processar_pergunta_old_api
from ..ui_utils import (
    exibir_cabecalho_sistema,
    verificar_api_key,
    processar_pergunta_padrao,
    verificar_comando_saida,
    verificar_pergunta_vazia
)

async def processar_pergunta_old_api_async(pergunta):
    """
    Wrapper assíncrono para a função síncrona processar_pergunta_old_api.
    
    Args:
        pergunta (str): A pergunta do usuário
        
    Returns:
        tuple: (resposta, None) - A resposta e None no lugar do trace_id que não existe na API antiga
    """
    # A função original é síncrona, mas precisamos retornar uma tupla para manter a interface consistente
    resposta = processar_pergunta_old_api(pergunta)
    return resposta, None

async def main_interativo_old_api_async():
    """
    Função principal assíncrona que implementa a interface interativa para a API antiga.
    
    Permite ao usuário fazer perguntas continuamente até digitar 'sair'.
    """
    try:
        # Exibir cabeçalho personalizado para a API antiga
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
            if verificar_comando_saida(pergunta):
                break
            
            # Verificar se a pergunta não está vazia
            if verificar_pergunta_vazia(pergunta):
                continue
            
            # Processar a pergunta usando a função padronizada
            sucesso, resultado = await processar_pergunta_padrao(pergunta, processar_pergunta_old_api_async)
            
            # Se o processamento foi bem-sucedido, exibir o resultado
            if sucesso:
                resposta, _ = resultado  # Ignoramos o segundo valor que seria o trace_id
                print("\n=== Resposta ===")
                print(resposta)
                print("================")
    except Exception as e:
        print(f"\nErro fatal: {str(e)}")
        print("O programa será encerrado.")

def main_interativo_old_api():
    """
    Função principal que implementa a interface interativa para a API antiga.
    Wrapper síncrono para a função assíncrona.
    """
    try:
        asyncio.run(main_interativo_old_api_async())
    except Exception as e:
        print(f"\nErro fatal: {str(e)}")
        print("O programa será encerrado.")

if __name__ == "__main__":
    main_interativo_old_api()
