"""
Cliente para a API antiga da OpenAI.

Este módulo contém a inicialização do cliente OpenAI e funções relacionadas.
"""

import os
from openai import OpenAI

def verificar_api_key():
    """Verifica se a chave da API da OpenAI está configurada.
    
    Returns:
        bool: True se a chave está configurada, False caso contrário.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERRO: OPENAI_API_KEY não está configurada.")
        print("Por favor, execute o script run.sh para configurar a variável de ambiente.")
        return False
    
    # Exibe os primeiros caracteres da chave para confirmação
    print(f"API Key detectada: {api_key[:8]}...")
    return True

# Inicialização do cliente OpenAI
try:
    client = OpenAI()
except Exception as e:
    print(f"Erro ao inicializar o cliente OpenAI: {e}")
    client = None
