"""
Módulo para gerenciamento de runs na API antiga da OpenAI.

Este módulo contém funções para criar, monitorar e interagir com runs.
"""

import time
from typing import Dict, Any, Optional
from .client import client
from .config import STATUS_EM_ANDAMENTO, STATUS_FINALIZADOS, TEMPO_ESPERA

def criar_run(thread_id: str, assistant_id: str) -> Any:
    """Cria um novo run com o assistente especificado.
    
    Args:
        thread_id: ID do thread onde o run será criado.
        assistant_id: ID do assistente que será usado para o run.
        
    Returns:
        Objeto do run criado.
        
    Raises:
        Exception: Se ocorrer um erro ao criar o run.
    """
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id
        )
        return run
    except Exception as e:
        print(f"Erro ao criar run: {e}")
        raise

def aguardar_run(thread_id: str, run_id: str, aguardar_conclusao: bool = False) -> Any:
    """Aguarda até que o run atinja um estado específico.
    
    Args:
        thread_id: ID do thread onde o run está.
        run_id: ID do run a ser monitorado.
        aguardar_conclusao: Se True, aguarda até que o run seja concluído.
                           Se False, retorna quando o run requer ação.
        
    Returns:
        Objeto do run atualizado.
    """
    while True:
        try:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            
            # Verificar se o run requer ação
            if run.status == "requires_action" and not aguardar_conclusao:
                return run
            
            # Verificar se o run foi concluído
            if run.status in STATUS_FINALIZADOS:
                return run
            
            # Se o run ainda está em andamento, aguardar e verificar novamente
            if run.status in STATUS_EM_ANDAMENTO:
                print(f"Run em andamento. Status: {run.status}")
                time.sleep(TEMPO_ESPERA)
                continue
            
            # Status desconhecido
            print(f"Status desconhecido: {run.status}")
            return run
            
        except Exception as e:
            print(f"Erro ao recuperar status do run: {e}")
            time.sleep(TEMPO_ESPERA)

def submeter_resposta_ferramenta(thread_id: str, run_id: str, tool_call_id: str, output: str = "") -> None:
    """Submete uma resposta para uma chamada de ferramenta.
    
    Args:
        thread_id: ID do thread onde o run está.
        run_id: ID do run que requer a ação.
        tool_call_id: ID da chamada de ferramenta a ser respondida.
        output: Saída opcional para a ferramenta.
        
    Raises:
        Exception: Se ocorrer um erro ao submeter a resposta.
    """
    try:
        client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run_id,
            tool_outputs=[
                {
                    "tool_call_id": tool_call_id,
                    "output": output
                }
            ]
        )
    except Exception as e:
        print(f"Erro ao submeter resposta da ferramenta: {e}")
        raise


def listar_runs_ativos(thread_id: str) -> list:
    """Lista todos os runs ativos em um thread.
    
    Args:
        thread_id: ID do thread para verificar runs ativos.
        
    Returns:
        Lista de runs ativos.
    """
    try:
        runs = client.beta.threads.runs.list(thread_id=thread_id)
        runs_ativos = [run for run in runs.data if run.status in STATUS_EM_ANDAMENTO]
        return runs_ativos
    except Exception as e:
        print(f"Erro ao listar runs: {e}")
        return []


def listar_todos_runs(thread_id: str) -> list:
    """Lista todos os runs em um thread, independente do status.
    
    Args:
        thread_id: ID do thread para listar runs.
        
    Returns:
        Lista de todos os runs.
    """
    try:
        runs = client.beta.threads.runs.list(thread_id=thread_id)
        return runs.data
    except Exception as e:
        print(f"Erro ao listar todos os runs: {e}")
        return []


def obter_status_run(thread_id: str, run_id: str) -> str:
    """Obtém o status de um run específico.
    
    Args:
        thread_id: ID do thread onde o run está.
        run_id: ID do run para verificar o status.
        
    Returns:
        Status do run ou None se ocorrer um erro.
    """
    try:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        return run.status
    except Exception as e:
        print(f"Erro ao obter status do run {run_id}: {e}")
        return None


def cancelar_run(thread_id: str, run_id: str) -> bool:
    """Cancela um run específico.
    
    Args:
        thread_id: ID do thread onde o run está.
        run_id: ID do run a ser cancelado.
        
    Returns:
        True se o cancelamento foi bem-sucedido, False caso contrário.
    """
    try:
        client.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)
        print(f"Run {run_id} cancelado com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao cancelar run {run_id}: {e}")
        return False


def limpar_runs_ativos(thread_id: str) -> bool:
    """Cancela todos os runs ativos em um thread.
    
    Args:
        thread_id: ID do thread para limpar runs ativos.
        
    Returns:
        True se todos os runs foram cancelados com sucesso, False caso contrário.
    """
    runs_ativos = listar_runs_ativos(thread_id)
    
    if not runs_ativos:
        print("Não há runs ativos para cancelar.")
        return True
    
    print(f"Encontrados {len(runs_ativos)} runs ativos. Cancelando...")
    sucesso = True
    
    for run in runs_ativos:
        if not cancelar_run(thread_id, run.id):
            sucesso = False
    
    # Aguardar um momento para garantir que os cancelamentos sejam processados
    time.sleep(2)
    return sucesso
