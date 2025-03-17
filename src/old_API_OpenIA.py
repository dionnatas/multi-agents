"""Módulo para processamento de perguntas usando a API antiga da OpenAI (Assistants API).

[DEPRECIADO] Este arquivo foi substituído pelo pacote 'old_api' e será removido em breve.
Por favor, use a nova implementação em 'old_api/processador.py' para novas funcionalidades.

Este módulo implementa a comunicação com a API de Assistentes da OpenAI,
que será descontinuada em 2026. O código segue boas práticas de programação
e permite o encaminhamento de perguntas para agentes especialistas.
"""

import json
import time
import os
from typing import Dict, List, Optional, Tuple, Any
from openai import OpenAI

# Constantes
THREAD_ID = "thread_0mIOj6RDNNeK4Bv3UTk2ZyA2"
ORQUESTRADOR_ID = "asst_WhiiRlPHO2Y8itK1S5PK2ySw"

# Mapeamento de especialistas
ESPECIALISTAS = {
    "mat-ass": "asst_2x4SggBYScMn9FUMnXZRo0dd",  # Especialista em Matemática
    "port-ass": "asst_QqqqLr2X6o3ooM6NLADZdD2Q", # Especialista em Português
    "his-ass": "asst_H7j2hPFtkEpNFmFlgiNmFNq2"  # Especialista em História
}

# Status possíveis para um run
STATUS_EM_ANDAMENTO = ["queued", "in_progress"]
STATUS_FINALIZADOS = ["completed", "failed", "cancelled", "expired"]

# Verificação da chave da API
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


def extrair_argumentos_tool_call(tool_call: Any) -> Dict[str, str]:
    """Extrai e processa os argumentos de uma chamada de ferramenta.
    
    Args:
        tool_call: Objeto contendo informações da chamada de ferramenta.
        
    Returns:
        Dicionário com os argumentos processados.
    """
    try:
        return json.loads(tool_call.function.arguments)
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar argumentos JSON: {e}")
        return {}


def extrair_tool_call_info(run: Any) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extrai informações relevantes de um run que requer ação.
    
    Args:
        run: Objeto contendo informações do run atual.
        
    Returns:
        Uma tupla contendo (tool_call_id, nome_assistente, mensagem).
    """
    tool_call_id = None
    nome_assistente = None
    mensagem = None
    
    if run.status == "requires_action" and run.required_action:
        if run.required_action.type == "submit_tool_outputs":
            tool_calls = run.required_action.submit_tool_outputs.tool_calls
            for i, tool_call in enumerate(tool_calls):
                if tool_call.type == "function":
                    print(f"\n--- Tool Call {i+1} ---")
                    print(f"RequiredActionFunctionToolCall id: {tool_call.id}")
                    print(f"Function name: {tool_call.function.name}")
                    
                    # Extrair argumentos
                    args = extrair_argumentos_tool_call(tool_call)
                    print(f"\nArgumentos processados:")
                    for key, value in args.items():
                        print(f"{key}: {value}")
                        if key == "nome_assistente":
                            nome_assistente = value
                        if key == "mensagem":
                            mensagem = value
                    
                    tool_call_id = tool_call.id
                    break  # Processamos apenas o primeiro tool call
    
    return tool_call_id, nome_assistente, mensagem


def criar_mensagem(thread_id: str, conteudo: str) -> Any:
    """Cria uma nova mensagem no thread especificado.
    
    Args:
        thread_id: ID do thread onde a mensagem será criada.
        conteudo: Conteúdo da mensagem.
        
    Returns:
        Objeto contendo informações da mensagem criada.
    """
    return client.beta.threads.messages.create(
        thread_id,
        role="user",
        content=conteudo
    )


def criar_run(thread_id: str, assistant_id: str) -> Any:
    """Cria um novo run com o assistente especificado.
    
    Args:
        thread_id: ID do thread onde o run será criado.
        assistant_id: ID do assistente que será usado.
        
    Returns:
        Objeto contendo informações do run criado.
    """
    return client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )


def obter_run(thread_id: str, run_id: str) -> Any:
    """Obtém informações de um run específico.
    
    Args:
        thread_id: ID do thread do run.
        run_id: ID do run a ser obtido.
        
    Returns:
        Objeto contendo informações do run.
    """
    return client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id
    )


def aguardar_run(thread_id: str, run_id: str, aguardar_conclusao: bool = False) -> Any:
    """Aguarda até que um run seja concluído ou requeira ação.
    
    Args:
        thread_id: ID do thread do run.
        run_id: ID do run a ser monitorado.
        aguardar_conclusao: Se True, aguarda até que o run seja concluído.
                           Se False, aguarda até que o run requeira ação ou seja concluído.
        
    Returns:
        Objeto contendo informações do run após a conclusão ou ação requerida.
    """
    run = obter_run(thread_id, run_id)
    
    if aguardar_conclusao:
        # Aguardar até que o run seja concluído
        while run.status not in STATUS_FINALIZADOS:
            print(f"Status atual: {run.status}")
            time.sleep(1)  # Evitar muitas requisições em curto período
            run = obter_run(thread_id, run_id)
    else:
        # Aguardar até que o run requeira ação ou seja concluído
        while run.status in STATUS_EM_ANDAMENTO:
            print(f"Status atual: {run.status}")
            time.sleep(1)  # Evitar muitas requisições em curto período
            run = obter_run(thread_id, run_id)
    
    return run


def submeter_resposta_ferramenta(thread_id: str, run_id: str, tool_call_id: str, output: str = "success:true") -> Any:
    """Submete a resposta para uma chamada de ferramenta.
    
    Args:
        thread_id: ID do thread do run.
        run_id: ID do run que requer ação.
        tool_call_id: ID da chamada de ferramenta.
        output: Saída da ferramenta.
        
    Returns:
        Objeto contendo informações do run após a submissão.
    """
    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=[
            {
                "tool_call_id": tool_call_id,
                "output": output
            }
        ]
    )


def obter_mensagens(thread_id: str) -> List[Any]:
    """Obtém todas as mensagens de um thread.
    
    Args:
        thread_id: ID do thread.
        
    Returns:
        Lista de mensagens do thread.
    """
    return client.beta.threads.messages.list(thread_id).data


def obter_ultima_resposta_assistente(thread_id: str) -> Optional[str]:
    """Obtém a resposta mais recente do assistente em um thread.
    
    Args:
        thread_id: ID do thread.
        
    Returns:
        Texto da última resposta do assistente ou None se não houver resposta.
    """
    mensagens = obter_mensagens(thread_id)
    
    for mensagem in mensagens:
        if mensagem.role == "assistant":
            for conteudo in mensagem.content:
                if conteudo.type == "text":
                    return conteudo.text.value
            break
    
    return None


def processar_pergunta(pergunta: str) -> str:
    """Processa uma pergunta usando a API antiga da OpenAI.
    
    Este é o ponto de entrada principal para processar perguntas.
    A função coordena todo o fluxo de comunicação com a API.
    
    Args:
        pergunta: A pergunta a ser processada.
        
    Returns:
        A resposta do assistente especialista.
    """
    # Verificar se a chave da API está configurada
    if not verificar_api_key():
        return "ERRO: OPENAI_API_KEY não está configurada. Por favor, execute o script run.sh."
    
    try:
        # Criar nova mensagem no thread
        print(f"\nEnviando pergunta: '{pergunta}'")
        criar_mensagem(THREAD_ID, pergunta)
        
        # Criar novo run com o orquestrador
        print("\nIniciando processamento com o orquestrador...")
        run = criar_run(THREAD_ID, ORQUESTRADOR_ID)
        print(f"Run ID: {run.id}")
        
        # Aguardar até que o run requeira ação ou seja concluído
        run = aguardar_run(THREAD_ID, run.id)
        
        # Verificar o resultado do run
        if run.status == "completed":
            # Caso raro: o orquestrador respondeu diretamente
            resposta = obter_ultima_resposta_assistente(THREAD_ID)
            return resposta or "Não foi possível obter a resposta."
        
        elif run.status == "requires_action":
            # Extrair informações da chamada de ferramenta
            tool_call_id, nome_assistente, _ = extrair_tool_call_info(run)
            
            if not tool_call_id:
                return "Erro: Não foi possível extrair o ID da chamada de ferramenta."
            
            # Submeter resposta para a chamada de ferramenta
            print("\nEncaminhando para o especialista...")
            submeter_resposta_ferramenta(THREAD_ID, run.id, tool_call_id)
            
            # Aguardar a conclusão do run atual
            run = aguardar_run(THREAD_ID, run.id, aguardar_conclusao=True)
            
            # Verificar se temos um especialista válido
            if not nome_assistente or nome_assistente not in ESPECIALISTAS:
                return "Erro: Especialista não identificado ou inválido."
            
            # Criar run para o agente especialista
            print(f"\nConsultando o especialista: {nome_assistente}")
            run_especialista = criar_run(THREAD_ID, ESPECIALISTAS[nome_assistente])
            
            # Aguardar a resposta do especialista
            aguardar_run(THREAD_ID, run_especialista.id, aguardar_conclusao=True)
            
            # Obter a resposta final
            resposta = obter_ultima_resposta_assistente(THREAD_ID)
            return resposta or "Não foi possível obter a resposta do especialista."
        
        else:
            return f"Erro: O run terminou com status inesperado: {run.status}"
    
    except Exception as e:
        # Capturar e retornar qualquer erro que ocorra durante o processamento
        print(f"Erro ao processar a pergunta: {str(e)}")
        return f"Erro ao processar a pergunta: {str(e)}"


# Execução direta do script para teste
if __name__ == "__main__":
    pergunta_teste = "Quem descobriu o Brasil e em que ano?"
    print(f"\n=== Testando processamento com a pergunta: '{pergunta_teste}' ===")
    resposta = processar_pergunta(pergunta_teste)
    print(f"\nResposta final:\n{resposta}")