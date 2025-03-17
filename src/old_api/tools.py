"""
Módulo para gerenciamento de ferramentas (tools) na API antiga da OpenAI.

Este módulo contém funções para extrair informações de chamadas de ferramentas.
"""

import json
from typing import Dict, Tuple, Any, Optional

# Variáveis globais para armazenar informações extraídas das chamadas de ferramentas
nome_assistente = None
mensagem = None

def extrair_argumentos_tool_call(tool_call: Any) -> Dict[str, str]:
    """Extrai os argumentos de uma chamada de ferramenta.
    
    Args:
        tool_call: Objeto da chamada de ferramenta.
        
    Returns:
        Dicionário com os argumentos extraídos.
    """
    try:
        # Extrair e analisar os argumentos JSON
        argumentos_json = tool_call.function.arguments
        return json.loads(argumentos_json)
    except Exception as e:
        print(f"Erro ao extrair argumentos da chamada de ferramenta: {e}")
        return {}

def extrair_tool_call_info(run: Any) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Extrai informações da chamada de ferramenta de um run.
    
    Esta função extrai o ID da chamada de ferramenta, o nome do assistente
    e a mensagem associada.
    
    Args:
        run: Objeto do run que contém a chamada de ferramenta.
        
    Returns:
        Uma tupla contendo (tool_call_id, nome_assistente, mensagem).
        Qualquer um desses valores pode ser None se não for encontrado.
    """
    global nome_assistente, mensagem
    
    # Verificar se o run requer ação
    if not hasattr(run, "required_action") or not run.required_action:
        print("O run não requer ação.")
        return None, None, None
    
    try:
        # Obter a primeira chamada de ferramenta
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        if not tool_calls:
            print("Nenhuma chamada de ferramenta encontrada.")
            return None, None, None
        
        # Extrair o ID da chamada de ferramenta
        tool_call = tool_calls[0]
        tool_call_id = tool_call.id
        
        # Extrair argumentos da chamada de ferramenta
        argumentos = extrair_argumentos_tool_call(tool_call)
        
        # Atualizar variáveis globais
        # Verificar diferentes chaves possíveis para o nome do especialista
        nome_assistente = argumentos.get("nome_assistente", "") or argumentos.get("especialista", "")
        mensagem = argumentos.get("mensagem", "")
        
        # Imprimir informações para debug
        print(f"\n--- Informações da chamada de ferramenta ---")
        print(f"Tool Call ID: {tool_call_id}")
        print(f"Argumentos: {argumentos}")
        print(f"Nome do especialista identificado: {nome_assistente}")
        
        return tool_call_id, nome_assistente, mensagem
    
    except Exception as e:
        print(f"Erro ao extrair informações da chamada de ferramenta: {e}")
        return None, None, None
