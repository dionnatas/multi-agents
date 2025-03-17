import asyncio
import sys
import os

# Adicionar o diretório raiz ao path para permitir importações dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import processar_pergunta
from src.config_manager import ConfigManager
from src.logger import Logger
from src.error_handler import catch_async_errors, APIKeyError, APIConnectionError, ValidationError

# Configurar logger específico para este módulo
logger = Logger.setup("interativo")

@catch_async_errors
async def main_interativo():
    """Função principal para interação com o usuário."""
    try:
        logger.info("Iniciando Sistema Educacional Multi-Agentes")
        
        # Verifica se a chave de API da OpenAI está configurada
        if not ConfigManager.validate_api_key():
            logger.error("API Key não configurada. O sistema não pode funcionar corretamente.")
            print("ERRO: OPENAI_API_KEY não está configurada.")
            print("Por favor, execute o script run.sh para configurar a variável de ambiente.")
            return
    
        print("=== Sistema Educacional de Perguntas e Respostas ===")
        print("Este sistema utiliza agentes especializados para responder suas perguntas.")
        print("Cada pergunta é classificada e encaminhada para o especialista adequado.")
        
        # Obter a chave da API de forma segura
        api_key = ConfigManager.get_api_key()
        if api_key:
            logger.info("API Key detectada e validada")
            print(f"\nAPI Key detectada: {api_key[:8]}...")
        
        # Usando exclusivamente a API Nova (Agents SDK)
        logger.info("Usando a API Nova (Agents SDK)")
    
        print("\nDigite 'sair' a qualquer momento para encerrar o programa.")
        
        while True:
            # Solicita a pergunta ao usuário
            pergunta = input("\nDigite sua pergunta: ")
            
            # Verifica se o usuário deseja sair
            if pergunta.lower() == 'sair':
                logger.info("Usuário solicitou encerramento do programa")
                print("Encerrando o programa...")
                break
            
            # Verificar se a pergunta não está vazia
            if not pergunta.strip():
                print("\nA pergunta não pode estar vazia. Por favor, tente novamente.")
                continue
            
            # Processa a pergunta usando a API Nova
            logger.info(f"Processando pergunta: '{pergunta[:30]}{'...' if len(pergunta) > 30 else ''}'") 
            print("\nProcessando sua pergunta, aguarde um momento...")
            
            try:
                # Usar a API nova (Agents SDK)
                logger.debug("Usando API Nova (Agents SDK)")
                resposta, trace_id = await processar_pergunta(pergunta)
                
                logger.info(f"Resposta obtida com sucesso, Trace ID: {trace_id}")
                # Exibe a resposta
                print(f"\nResposta:\n{resposta}")
                print(f"\n[TRACE] ID: {trace_id}")
                print("Você pode visualizar o trace completo no painel da OpenAI.")
                
            except ValidationError as e:
                logger.error(f"Erro de validação: {str(e)}")
                print(f"\nErro de validação: {str(e)}")
            except APIConnectionError as e:
                logger.error(f"Erro de conexão com a API: {str(e)}")
                print(f"\nErro de conexão: {str(e)}")
            except Exception as e:
                logger.error(f"Erro inesperado: {str(e)}", exc_info=True)
                print(f"\nErro ao processar a pergunta: {str(e)}")
                print(f"Detalhes do erro: {type(e).__name__}")
    except Exception as e:
        logger.critical(f"Erro fatal na execução do programa: {str(e)}", exc_info=True)
        print(f"\nErro fatal: {str(e)}")
        print("O programa será encerrado.")

if __name__ == "__main__":
    try:
        asyncio.run(main_interativo())
    except KeyboardInterrupt:
        logger.warning("Programa interrompido pelo usuário")
        print("\nPrograma interrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Erro fatal na execução do programa: {str(e)}", exc_info=True)
        print(f"\nErro fatal: {str(e)}")
        sys.exit(1)
