"""
Utilitários de interface do usuário para o Sistema Educacional Multi-Agentes.
"""

import logging
from src.config_manager import ConfigManager

logger = logging.getLogger(__name__)

def exibir_cabecalho_sistema(com_contexto=False):
    """
    Exibe o cabeçalho do sistema com informações iniciais.
    
    Args:
        com_contexto (bool): Se True, exibe informação adicional sobre persistência de contexto
    """
    if com_contexto:
        logger.info("Iniciando o Sistema Educacional Multi-Agentes com contexto")
    else:
        logger.info("Iniciando o Sistema Educacional Multi-Agentes")
    
    print("=" * 50)
    print("      Sistema Educacional Multi-Agentes")
    print("=" * 50)
    print("Iniciando o sistema...")
    
    # Obter a chave da API de forma segura
    api_key = ConfigManager.get_api_key()
    if api_key:
        print(f"\nAPI Key detectada: {api_key[:8]}...")
    
    print("\n=== Sistema Educacional de Perguntas e Respostas ===")
    print("Este sistema utiliza agentes especializados para responder suas perguntas.")
    print("Cada pergunta é classificada e encaminhada para o especialista adequado.")
    
    if com_contexto:
        print("O sistema mantém o contexto da conversa entre perguntas.")

def verificar_api_key():
    """
    Verifica se a chave de API da OpenAI está configurada e exibe mensagem de erro se necessário.
    
    Returns:
        bool: True se a API Key está configurada, False caso contrário
    """
    if not ConfigManager.validate_api_key():
        logger.error("API Key não configurada. O sistema não pode funcionar corretamente.")
        print("ERRO: OPENAI_API_KEY não está configurada.")
        print("Por favor, execute o script run.sh para configurar a variável de ambiente.")
        return False
    return True

async def processar_pergunta_padrao(pergunta, processador_func):
    """
    Processa uma pergunta usando a função de processamento fornecida e trata erros de forma padronizada.
    
    Args:
        pergunta (str): A pergunta do usuário
        processador_func (callable): Função que processa a pergunta e retorna uma resposta
        
    Returns:
        tuple: (sucesso, resultado)
            - sucesso (bool): True se o processamento foi bem-sucedido, False caso contrário
            - resultado: Resultado do processamento ou mensagem de erro
    """
    try:
        logger.info(f"Processando pergunta: '{pergunta[:30]}{'...' if len(pergunta) > 30 else ''}'") 
        print("\nProcessando sua pergunta, aguarde um momento...")
        
        # Chamar a função de processamento
        resultado = await processador_func(pergunta)
        
        return True, resultado
    except ValidationError as e:
        logger.error(f"Erro de validação: {str(e)}")
        print(f"\nErro de validação: {str(e)}")
        return False, str(e)
    except APIConnectionError as e:
        logger.error(f"Erro de conexão com a API: {str(e)}")
        print(f"\nErro de conexão: {str(e)}")
        return False, str(e)
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
        print(f"\nOcorreu um erro inesperado: {str(e)}")
        return False, str(e)

def verificar_comando_saida(pergunta):
    """
    Verifica se o usuário digitou o comando para sair do programa.
    
    Args:
        pergunta (str): A entrada do usuário
        
    Returns:
        bool: True se o usuário deseja sair, False caso contrário
    """
    if pergunta.lower() == 'sair':
        logger.info("Usuário solicitou encerramento do programa")
        print("Encerrando o programa...")
        return True
    return False

def verificar_pergunta_vazia(pergunta):
    """
    Verifica se a pergunta está vazia.
    
    Args:
        pergunta (str): A pergunta do usuário
        
    Returns:
        bool: True se a pergunta está vazia, False caso contrário
    """
    if not pergunta.strip():
        print("\nA pergunta não pode estar vazia. Por favor, tente novamente.")
        return True
    return False
