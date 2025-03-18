"""
Módulo interativo para processamento de perguntas com persistência de contexto.

Este módulo implementa uma interface de linha de comando para interagir com o sistema
de processamento de perguntas, mantendo o contexto entre sessões.
"""

import asyncio
import sys
import os

# Adicionar o diretório raiz ao path para permitir importações dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.conversation_store import ConversationStore
from src.processar_com_contexto import processar_pergunta_com_contexto
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
logger = Logger.setup("interativo_contexto")

# Verificar se a chave de API da OpenAI está configurada
if not verificar_api_key():
    sys.exit(1)

@catch_async_errors
async def main():
    """Função principal para interação com o usuário."""
    try:
        # Exibir cabeçalho do sistema usando a função do módulo ui_utils
        exibir_cabecalho_sistema(com_contexto=True)
    
        # Listar conversas existentes
        conversas = ConversationStore.list_conversations()
        logger.info(f"Encontradas {len(conversas)} conversas existentes")
        
        conversation_id = None
        if conversas:
            print("\nConversas existentes:")
            for i, conv_id in enumerate(conversas, 1):
                conversa = ConversationStore.get_conversation(conv_id)
                if conversa:
                    # Adicionar log para depuração
                    logger.info(f"Conversa {conv_id}: nome='{conversa.name}', mensagens={len(conversa.messages)}")
                    
                    # Se a conversa tem um nome personalizado, exibi-lo
                    if conversa.name and conversa.name.strip():
                        nome_exibicao = conversa.name
                        logger.info(f"Usando nome personalizado: {nome_exibicao}")
                    # Caso contrário, usar a primeira mensagem ou ID como fallback
                    elif conversa.messages:
                        nome_exibicao = conversa.messages[0].content[:30] + "..." if len(conversa.messages[0].content) > 30 else conversa.messages[0].content
                        logger.info(f"Usando primeira mensagem como nome: {nome_exibicao}")
                    else:
                        nome_exibicao = f"Conversa {conv_id[:8]}"
                        logger.info(f"Usando ID como nome: {nome_exibicao}")
                    
                    print(f"{i}. {nome_exibicao} ({len(conversa.messages)} mensagens) - ID: {conv_id[:8]}...")
            
            # Criar um dicionário para mapear o índice ao nome da conversa
            nomes_conversas = {}
            for i, conv_id in enumerate(conversas, 1):
                conversa = ConversationStore.get_conversation(conv_id)
                if conversa:
                    if conversa.name and conversa.name.strip():
                        nomes_conversas[i] = conversa.name
                    elif conversa.messages:
                        nomes_conversas[i] = conversa.messages[0].content[:20] + "..." if len(conversa.messages[0].content) > 20 else conversa.messages[0].content
                    else:
                        nomes_conversas[i] = f"Conversa {conv_id[:8]}"
            
            print("\nEscolha uma opção:")
            print("0. Iniciar uma nova conversa")
            for i in range(1, len(conversas) + 1):
                print(f"{i}. Continuar '{nomes_conversas[i]}'")
            
            try:
                escolha = int(input("\nDigite o número da sua escolha: "))
                if 1 <= escolha <= len(conversas):
                    conversation_id = conversas[escolha - 1]
                    logger.info(f"Usuário escolheu continuar conversa: {conversation_id}")
                    print(f"\nContinuando conversa com ID: {conversation_id[:8]}...")
                else:
                    logger.info("Usuário escolheu iniciar nova conversa")
                    print("\nIniciando uma nova conversa...")
                    nome_conversa = input("\nDigite um nome para esta conversa: ")
                    if nome_conversa.strip():
                        conversation_id = ConversationStore.create_conversation(nome_conversa.strip())
                        logger.info(f"Nova conversa criada com nome: {nome_conversa}")
                        print(f"\nNova conversa '{nome_conversa}' iniciada!")
            except ValueError:
                logger.warning("Entrada inválida ao escolher conversa")
                print("\nOpção inválida. Iniciando uma nova conversa...")
                nome_conversa = input("\nDigite um nome para esta conversa: ")
                if nome_conversa.strip():
                    conversation_id = ConversationStore.create_conversation(nome_conversa.strip())
                    logger.info(f"Nova conversa criada com nome: {nome_conversa}")
                    print(f"\nNova conversa '{nome_conversa}' iniciada!")
        else:
            logger.info("Nenhuma conversa anterior encontrada")
            print("\nNenhuma conversa anterior encontrada. Iniciando uma nova conversa...")
            nome_conversa = input("\nDigite um nome para esta conversa: ")
            if nome_conversa.strip():
                conversation_id = ConversationStore.create_conversation(nome_conversa.strip())
                logger.info(f"Nova conversa criada com nome: {nome_conversa}")
                print(f"\nNova conversa '{nome_conversa}' iniciada!")
        
        print("\nDigite 'sair' a qualquer momento para encerrar o programa.")
        print("Digite 'nova' para iniciar uma nova conversa.")
    
        while True:
            # Solicitar pergunta ao usuário
            pergunta = input("\nDigite sua pergunta: ")
            
            # Verificar comando de saída
            if verificar_comando_saida(pergunta):
                break
            
            # Verificar comando para nova conversa
            if pergunta.lower() == 'nova':
                conversation_id = None
                logger.info("Usuário solicitou nova conversa")
                print("Iniciando uma nova conversa...")
                nome_conversa = input("\nDigite um nome para esta conversa: ")
                if nome_conversa.strip():
                    conversation_id = ConversationStore.create_conversation(nome_conversa.strip())
                    logger.info(f"Nova conversa criada com nome: {nome_conversa}")
                    print(f"\nNova conversa '{nome_conversa}' iniciada!")
                continue
            
            # Verificar se a pergunta não está vazia
            if verificar_pergunta_vazia(pergunta):
                continue
            
            # Criar uma função de processamento específica para este caso
            async def processar_com_contexto(p):
                return await processar_pergunta_com_contexto(p, conversation_id)
            
            # Processar a pergunta usando a função padronizada
            sucesso, resultado = await processar_pergunta_padrao(pergunta, processar_com_contexto)
            
            # Se o processamento foi bem-sucedido, exibir o resultado
            if sucesso:
                resposta, conversation_id = resultado
                logger.info(f"Resposta obtida com sucesso, ID da conversa: {conversation_id}")
                print(f"\nResposta: {resposta}")
                
                # Obter o nome da conversa para exibição
                conversa = ConversationStore.get_conversation(conversation_id)
                if conversa and conversa.name:
                    print(f"\n[Conversa: '{conversa.name}' | ID: {conversation_id[:8]}...]")
                else:
                    print(f"\n[ID da conversa: {conversation_id[:8]}...]")
    except Exception as e:
        logger.critical(f"Erro fatal na execução do programa: {str(e)}", exc_info=True)
        print(f"\nErro fatal: {str(e)}")
        print("O programa será encerrado.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.critical(f"Erro fatal na execução do programa: {str(e)}", exc_info=True)
        print(f"\nErro fatal: {str(e)}")
        print("O programa será encerrado.")
