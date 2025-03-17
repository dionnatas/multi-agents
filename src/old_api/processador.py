"""
Módulo principal para processamento de perguntas na API antiga da OpenAI.

Este módulo integra as funcionalidades dos outros módulos para processar perguntas.
"""

import re
import time
from typing import Optional
import sys
import os

# Adicionar o diretório raiz ao path para permitir importações dos módulos principais
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.config_manager import ConfigManager
from src.logger import Logger
from src.error_handler import catch_errors, APIKeyError, APIConnectionError, ValidationError

# Importações internas do módulo old_api
from .client import verificar_api_key
from .mensagens import criar_mensagem, obter_ultima_resposta_assistente
from .runs import criar_run, aguardar_run, submeter_resposta_ferramenta, cancelar_run
from .tools import extrair_tool_call_info
from .config import THREAD_ID, ORQUESTRADOR_ID, ESPECIALISTAS

# Configurar logger específico para este módulo
logger = Logger.setup("old_api.processador")

@catch_errors
def extrair_run_id_de_erro(mensagem_erro: str) -> str:
    """Extrai o ID do run de uma mensagem de erro da OpenAI.
    
    Args:
        mensagem_erro: A mensagem de erro contendo o ID do run.
        
    Returns:
        O ID do run ou None se não for encontrado.
        
    Raises:
        ValidationError: Se a mensagem de erro for inválida ou vazia
    """
    # Validar entrada
    if not mensagem_erro or not isinstance(mensagem_erro, str):
        logger.error("Mensagem de erro inválida ou vazia")
        raise ValidationError("Mensagem de erro inválida ou vazia")
    
    logger.debug(f"Extraindo ID do run da mensagem de erro: '{mensagem_erro[:50]}...'")
    
    # Padrão para encontrar o ID do run na mensagem de erro
    padrao = r"run ([a-zA-Z0-9_]+) is active"
    
    # Procurar o padrão na mensagem de erro
    match = re.search(padrao, mensagem_erro)
    
    if match:
        run_id = match.group(1)  # Retorna o ID do run
        logger.info(f"ID do run extraído com sucesso: {run_id}")
        return run_id
    
    logger.warning(f"Não foi possível extrair o ID do run da mensagem: '{mensagem_erro[:50]}...'")
    return None


@catch_errors
def processar_pergunta(pergunta: str) -> str:
    """Processa uma pergunta usando a API antiga da OpenAI.
    
    Este é o ponto de entrada principal para processar perguntas.
    A função coordena todo o fluxo de comunicação com a API.
    
    Args:
        pergunta: A pergunta a ser processada.
        
    Returns:
        A resposta do assistente especialista.
        
    Raises:
        ValidationError: Se a pergunta for inválida
        APIKeyError: Se a chave da API não estiver configurada
        APIConnectionError: Se houver problemas de conexão com a API
    """
    # Validar entrada
    if not pergunta or not isinstance(pergunta, str) or len(pergunta.strip()) == 0:
        logger.error("Tentativa de processar pergunta vazia")
        raise ValidationError("A pergunta não pode estar vazia")
    
    # Verificar se a chave de API da OpenAI está configurada
    if not ConfigManager.validate_api_key():
        logger.error("API Key não configurada. O sistema não pode funcionar corretamente.")
        raise APIKeyError("OPENAI_API_KEY não está configurada. Por favor, execute o script run.sh.")
    
    # Criar nova mensagem no thread
    logger.info(f"Enviando pergunta: '{pergunta[:50]}{'...' if len(pergunta) > 50 else ''}'")
    print(f"\nEnviando pergunta: '{pergunta}'")
    
    try:
        criar_mensagem(THREAD_ID, pergunta)
        logger.debug("Mensagem criada com sucesso no thread")
    except Exception as e:
        # Verificar se o erro é devido a um run ativo
        erro_str = str(e)
        logger.warning(f"Erro ao criar mensagem: {erro_str}")
        print(f"Erro ao criar mensagem: {erro_str}")
        
        if "while a run" in erro_str and "is active" in erro_str:
            # Extrair o ID do run da mensagem de erro
            run_id = extrair_run_id_de_erro(erro_str)
            
            if run_id:
                logger.info(f"Detectado run ativo: {run_id}. Tentando cancelar...")
                print(f"\nDetectado run ativo: {run_id}. Tentando cancelar...")
                
                try:
                    cancelar_run(THREAD_ID, run_id)
                    logger.info(f"Run {run_id} cancelado com sucesso")
                    print("Aguardando alguns segundos para garantir que o cancelamento seja processado...")
                    time.sleep(3)
                    
                    # Tentar criar a mensagem novamente
                    logger.info("Tentando enviar a mensagem novamente...")
                    print("Tentando enviar a mensagem novamente...")
                    criar_mensagem(THREAD_ID, pergunta)
                    logger.debug("Mensagem criada com sucesso após cancelamento do run")
                except Exception as cancel_error:
                    logger.error(f"Erro ao cancelar run: {str(cancel_error)}", exc_info=True)
                    raise APIConnectionError(f"Erro ao cancelar run: {str(cancel_error)}")
            else:
                logger.error(f"Não foi possível extrair o ID do run da mensagem de erro: {erro_str}")
                raise APIConnectionError(f"Não foi possível extrair o ID do run da mensagem de erro: {erro_str}")
        else:
            logger.error(f"Erro ao criar mensagem: {erro_str}")
            raise APIConnectionError(f"Erro ao criar mensagem: {erro_str}")
        
    # Criar novo run com o orquestrador
    logger.info("Iniciando processamento com o orquestrador...")
    print("\nIniciando processamento com o orquestrador...")
    
    try:
        run = criar_run(THREAD_ID, ORQUESTRADOR_ID)
        logger.debug(f"Run criado com sucesso. Run ID: {run.id}")
        print(f"Run ID: {run.id}")
        
        # Aguardar até que o run requeira ação ou seja concluído
        logger.info(f"Aguardando processamento do run {run.id}...")
        run = aguardar_run(THREAD_ID, run.id)
        logger.debug(f"Run {run.id} atualizado para status: {run.status}")
        
        # Verificar o resultado do run
        if run.status == "completed":
            # Caso raro: o orquestrador respondeu diretamente
            logger.info("Run completado diretamente pelo orquestrador")
            resposta = obter_ultima_resposta_assistente(THREAD_ID)
            if resposta:
                logger.info("Resposta obtida com sucesso do orquestrador")
                return resposta
            else:
                logger.error("Não foi possível obter a resposta do orquestrador")
                raise APIConnectionError("Não foi possível obter a resposta do orquestrador")
        
        elif run.status == "requires_action":
            # Extrair informações da chamada de ferramenta
            logger.info("Run requer ação. Extraindo informações da chamada de ferramenta...")
            tool_call_id, nome_assistente, ferramenta = extrair_tool_call_info(run)
            
            if not tool_call_id:
                logger.error("Não foi possível extrair o ID da chamada de ferramenta")
                raise APIConnectionError("Não foi possível extrair o ID da chamada de ferramenta")
            
            logger.info(f"Ferramenta chamada: {ferramenta}, Especialista: {nome_assistente}")
            
            # Submeter resposta para a chamada de ferramenta
            logger.info("Encaminhando para o especialista...")
            print("\nEncaminhando para o especialista...")
            
            try:
                submeter_resposta_ferramenta(THREAD_ID, run.id, tool_call_id)
                logger.debug("Resposta da ferramenta submetida com sucesso")
                
                # Aguardar a conclusão do run atual
                logger.info(f"Aguardando conclusão do run {run.id}...")
                run = aguardar_run(THREAD_ID, run.id, aguardar_conclusao=True)
                logger.debug(f"Run {run.id} concluído com status: {run.status}")
                
                # Verificar se temos um especialista válido
                if not nome_assistente or nome_assistente not in ESPECIALISTAS:
                    logger.error(f"Especialista inválido: {nome_assistente}")
                    raise ValidationError(f"Especialista não identificado ou inválido: {nome_assistente}")
                
                # Criar run para o agente especialista
                logger.info(f"Consultando o especialista: {nome_assistente}")
                print(f"\nConsultando o especialista: {nome_assistente}")
                
                run_especialista = criar_run(THREAD_ID, ESPECIALISTAS[nome_assistente])
                logger.debug(f"Run do especialista criado. Run ID: {run_especialista.id}")
                
                # Aguardar a resposta do especialista
                logger.info(f"Aguardando resposta do especialista {nome_assistente}...")
                aguardar_run(THREAD_ID, run_especialista.id, aguardar_conclusao=True)
                logger.debug("Run do especialista concluído")
                
                # Obter a resposta final
                logger.info("Obtendo resposta final do especialista...")
                resposta = obter_ultima_resposta_assistente(THREAD_ID)
                
                if resposta:
                    logger.info("Resposta obtida com sucesso do especialista")
                    return resposta
                else:
                    logger.error("Não foi possível obter a resposta do especialista")
                    raise APIConnectionError("Não foi possível obter a resposta do especialista")
                    
            except Exception as e:
                logger.error(f"Erro ao processar com o especialista: {str(e)}", exc_info=True)
                raise APIConnectionError(f"Erro ao processar com o especialista: {str(e)}")
        
        else:
            logger.error(f"O run terminou com status inesperado: {run.status}")
            raise APIConnectionError(f"O run terminou com status inesperado: {run.status}")
    
    except Exception as e:
        # Capturar e registrar qualquer erro que ocorra durante o processamento
        logger.error(f"Erro inesperado ao processar a pergunta: {str(e)}", exc_info=True)
        raise APIConnectionError(f"Erro ao processar a pergunta: {str(e)}")
