"""
Módulo para processamento de perguntas usando a SDK de Agentes da OpenAI com persistência de contexto.

Este módulo implementa uma solução para manter o contexto das conversas entre sessões,
similar ao THREAD_ID da API antiga, utilizando um sistema de armazenamento local.
"""

from agents import Agent, InputGuardrail, GuardrailFunctionOutput, Runner, trace, RunConfig
from pydantic import BaseModel
import asyncio
import uuid
import os
import sys
from openai import OpenAI

# Adicionar o diretório raiz ao path para permitir importações dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conversation_store import ConversationStore
from src.config_manager import ConfigManager
from src.logger import Logger
from src.error_handler import catch_async_errors, APIKeyError, APIConnectionError, ValidationError

# Configurar logger específico para este módulo
logger = Logger.setup("processador_contexto")

# Verificar se a chave de API da OpenAI está configurada
if not ConfigManager.validate_api_key():
    logger.error("API Key não configurada. O sistema não pode funcionar corretamente.")
    raise APIKeyError("OPENAI_API_KEY não está configurada")

# Importar os agentes do arquivo main.py
from src.main import triage_agent, math_tutor_agent, history_tutor_agent, guardrail_agent

@catch_async_errors
async def processar_pergunta_com_contexto(pergunta: str, conversation_id: str = None) -> tuple[str, str]:
    """
    Processa uma pergunta usando o agente de triagem e retorna a resposta,
    mantendo o contexto da conversa entre sessões.
    
    Args:
        pergunta (str): A pergunta a ser processada.
        conversation_id (str, opcional): ID da conversa existente. Se None, cria uma nova conversa.
        
    Returns:
        tuple[str, str]: (resposta do agente especialista, ID da conversa)
    
    Raises:
        ValidationError: Se a pergunta for inválida
        APIConnectionError: Se houver problemas de conexão com a API
        APIKeyError: Se a chave da API não estiver configurada
    """
    # Validar entrada
    if not pergunta or not isinstance(pergunta, str) or len(pergunta.strip()) == 0:
        raise ValidationError("A pergunta não pode estar vazia")
    
    # Se não foi fornecido um ID de conversa, cria uma nova
    if not conversation_id:
        # Note que a criação da conversa com nome é feita na interface do usuário (interativo_com_contexto.py)
        # Aqui apenas criamos uma conversa sem nome caso não tenha sido criada antes
        conversation_id = ConversationStore.create_conversation()
        logger.info(f"Nova conversa criada com ID: {conversation_id}")
    else:
        logger.info(f"Usando conversa existente com ID: {conversation_id}")
    
    # Adicionar a pergunta do usuário à conversa
    ConversationStore.add_message(conversation_id, "user", pergunta)
    
    # Recuperar o histórico de mensagens para usar como contexto
    mensagens_anteriores = ConversationStore.get_messages_as_input_list(conversation_id)
    
    # Implementar janela deslizante para limitar o tamanho do contexto
    # Obter o valor da configuração
    max_context_messages = ConfigManager.get_config("nova", "max_context_messages")
    
    if len(mensagens_anteriores) > max_context_messages:
        logger.info(f"Limitando contexto para as últimas {max_context_messages} mensagens (de {len(mensagens_anteriores)} totais)")
        mensagens_anteriores = mensagens_anteriores[-max_context_messages:]
    
    # Gerar ID único para o trace
    trace_id = f"trace_{uuid.uuid4().hex}"
    group_id = ConfigManager.get_config("nova", "trace_group_id")
    workflow_name = ConfigManager.get_config("nova", "trace_workflow_name")
    
    # Configurar o rastreamento
    run_config = RunConfig(
        trace_id=trace_id,
        workflow_name=workflow_name,
        group_id=group_id,
        trace_include_sensitive_data=True
    )
    
    logger.info(f"Trace ID: {trace_id}")
    logger.info(f"Histórico da conversa: {len(mensagens_anteriores)} mensagens")
    
    try:
        # Executar a pergunta com trace e histórico de mensagens
        with trace(run_config.workflow_name):
            # Se temos histórico, usamos ele como input
            if len(mensagens_anteriores) > 1:  # Mais de uma mensagem (não apenas a pergunta atual)
                logger.debug("Processando com histórico completo")
                result = await Runner.run(
                    triage_agent, 
                    mensagens_anteriores,  # Passamos o histórico completo
                    run_config=run_config
                )
            else:
                # Para a primeira mensagem, usamos apenas a pergunta
                logger.debug("Processando primeira mensagem sem histórico")
                result = await Runner.run(
                    triage_agent, 
                    pergunta,
                    run_config=run_config
                )
    except Exception as e:
        logger.error(f"Erro ao processar pergunta: {str(e)}")
        raise APIConnectionError(f"Falha na comunicação com a API da OpenAI: {str(e)}")
    
    # Adicionar a resposta do assistente à conversa
    resposta = result.final_output
    ConversationStore.add_message(conversation_id, "assistant", resposta)
    
    # Retornar a resposta e o ID da conversa
    return resposta, conversation_id

async def main():
    """Função principal para testar o processamento com contexto."""
    # Testar o processamento com uma nova conversa
    resposta1, conversation_id = await processar_pergunta_com_contexto("Qual é a capital do Brasil?")
    print(f"\nResposta 1: {resposta1}")
    
    # Testar o processamento com a mesma conversa (mantendo contexto)
    resposta2, _ = await processar_pergunta_com_contexto("Qual é a população dessa cidade?", conversation_id)
    print(f"\nResposta 2: {resposta2}")
    
    # Testar o processamento com a mesma conversa (mantendo contexto)
    resposta3, _ = await processar_pergunta_com_contexto("Quem foi o fundador dessa cidade?", conversation_id)
    print(f"\nResposta 3: {resposta3}")

if __name__ == "__main__":
    asyncio.run(main())
