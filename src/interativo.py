import asyncio
import sys
import os

# Adicionar o diretório raiz ao path para permitir importações dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import processar_pergunta
from src.config_manager import ConfigManager
from src.logger import Logger
from src.error_handler import catch_async_errors, APIKeyError, APIConnectionError, ValidationError
from src.ui_utils import (
    exibir_cabecalho_sistema, 
    verificar_api_key, 
    processar_pergunta_padrao,
    verificar_comando_saida,
    verificar_pergunta_vazia
)

# Configurar logger específico para este módulo
logger = Logger.setup("interativo")

@catch_async_errors
async def main_interativo():
    """Função principal para interação com o usuário."""
    try:
        # Verifica se a chave de API da OpenAI está configurada
        if not verificar_api_key():
            return
    
        # Exibir cabeçalho do sistema usando a função do módulo ui_utils
        exibir_cabecalho_sistema(com_contexto=False)
        
        # Log adicional para API
        logger.info("API Key detectada e validada")
        
        # Usando exclusivamente a API Nova (Agents SDK)
        logger.info("Usando a API Nova (Agents SDK)")
    
        print("\nDigite 'sair' a qualquer momento para encerrar o programa.")
        
        while True:
            # Solicita a pergunta ao usuário
            pergunta = input("\nDigite sua pergunta: ")
            
            # Verifica se o usuário deseja sair
            if verificar_comando_saida(pergunta):
                break
            
            # Verificar se a pergunta não está vazia
            if verificar_pergunta_vazia(pergunta):
                continue
            
            # Criar uma função de processamento específica para este caso
            async def processar_com_api_nova(p):
                logger.debug("Usando API Nova (Agents SDK)")
                return await processar_pergunta(p)
            
            # Processar a pergunta usando a função padronizada
            sucesso, resultado = await processar_pergunta_padrao(pergunta, processar_com_api_nova)
            
            # Se o processamento foi bem-sucedido, exibir o resultado
            if sucesso:
                resposta, trace_id = resultado
                logger.info(f"Resposta obtida com sucesso, Trace ID: {trace_id}")
                # Exibe a resposta
                print(f"\nResposta:\n{resposta}")
                print(f"\n[TRACE] ID: {trace_id}")
                print("Você pode visualizar o trace completo no painel da OpenAI.")
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
