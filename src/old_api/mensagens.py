"""
Módulo para gerenciamento de mensagens na API antiga da OpenAI.

Este módulo contém funções para criar e recuperar mensagens de threads.
"""

from typing import Optional, List
from .client import client
from .config import TEMPO_ESPERA

def criar_mensagem(thread_id: str, conteudo: str) -> dict:
    """Cria uma nova mensagem no thread especificado.
    
    Args:
        thread_id: ID do thread onde a mensagem será criada.
        conteudo: Conteúdo da mensagem a ser enviada.
        
    Returns:
        Objeto da mensagem criada.
        
    Raises:
        Exception: Se ocorrer um erro ao criar a mensagem.
    """
    try:
        mensagem = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=conteudo
        )
        return mensagem
    except Exception as e:
        print(f"Erro ao criar mensagem: {e}")
        raise

def obter_ultima_resposta_assistente(thread_id: str) -> Optional[str]:
    """Obtém a resposta mais recente do assistente no thread.
    
    Args:
        thread_id: ID do thread de onde obter a resposta.
        
    Returns:
        O conteúdo da última mensagem do assistente, ou None se não encontrada.
    """
    try:
        # Listar mensagens do thread, ordenadas por data de criação (mais recentes primeiro)
        mensagens = client.beta.threads.messages.list(
            thread_id=thread_id,
            order="desc"
        )
        
        # Procurar pela mensagem mais recente do assistente
        for mensagem in mensagens.data:
            if mensagem.role == "assistant":
                # Extrair o conteúdo da mensagem
                conteudo = mensagem.content[0].text.value
                return conteudo
        
        return None
    except Exception as e:
        print(f"Erro ao obter resposta do assistente: {e}")
        return None
