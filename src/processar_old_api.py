"""Módulo para processamento de perguntas usando a API antiga da OpenAI (Assistants API).

Este módulo implementa a interface para o processamento de perguntas usando a API antiga,
reutilizando as funções refatoradas do módulo old_API_OpenIA.py.

Utiliza os componentes centralizados de configuração, logging e tratamento de erros.
"""

import sys
import os.path
from src.config_manager import ConfigManager
from src.logger import Logger
from src.error_handler import catch_errors, APIKeyError, APIConnectionError, ValidationError

# Configurar logger específico para este módulo
logger = Logger.setup("processador_old_api")

# Adiciona o diretório atual ao path para permitir importações diretas
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa a função de processamento da API antiga
try:
    from old_api.processador import processar_pergunta
    logger.info("Módulo de processamento da API antiga importado com sucesso (nova estrutura)")
except ImportError:
    # Fallback para a importação antiga caso a nova estrutura não esteja disponível
    try:
        from old_API_OpenIA import processar_pergunta
        logger.info("Módulo de processamento da API antiga importado com sucesso (estrutura antiga)")
    except ImportError:
        logger.error("Falha ao importar o módulo de processamento da API antiga")
        print("ERRO: Não foi possível importar o módulo de processamento da API antiga.")

@catch_errors
def processar_pergunta_old_api(pergunta: str) -> str:
    """
    Processa uma pergunta usando a API antiga da OpenAI (threads e assistants).
    
    Esta função serve como interface para o módulo interativo.py, encapsulando
    a chamada para a função processar_pergunta do módulo old_API_OpenIA.py.
    
    Args:
        pergunta (str): A pergunta a ser processada.
        
    Returns:
        str: A resposta do agente especialista.
        
    Raises:
        ValidationError: Se a pergunta for inválida
        APIConnectionError: Se houver problemas de conexão com a API
        APIKeyError: Se a chave da API não estiver configurada
    """
    # Validar entrada
    if not pergunta or not isinstance(pergunta, str) or len(pergunta.strip()) == 0:
        logger.error("Tentativa de processar pergunta vazia")
        raise ValidationError("A pergunta não pode estar vazia")
    
    # Verificar se a chave de API da OpenAI está configurada
    if not ConfigManager.validate_api_key():
        logger.error("API Key não configurada. O sistema não pode funcionar corretamente.")
        raise APIKeyError("OPENAI_API_KEY não está configurada. Por favor, execute o script run.sh.")
    
    try:
        logger.info(f"Processando pergunta com API antiga: '{pergunta[:30]}{'...' if len(pergunta) > 30 else ''}'")
        # Utilizar a função refatorada do módulo old_API_OpenIA.py
        resposta = processar_pergunta(pergunta)
        logger.info("Resposta obtida com sucesso da API antiga")
        return resposta
    except Exception as e:
        # Capturar e registrar qualquer erro que ocorra durante o processamento
        logger.error(f"Erro ao processar pergunta com API antiga: {str(e)}", exc_info=True)
        raise APIConnectionError(f"Falha na comunicação com a API da OpenAI: {str(e)}")
