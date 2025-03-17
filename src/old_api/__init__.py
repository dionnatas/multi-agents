"""
Pacote para interação com a API antiga da OpenAI.

Este pacote contém módulos para interagir com a API de Assistentes da OpenAI,
organizados de forma modular para melhor manutenção e legibilidade.
"""

from .client import verificar_api_key, client
from .mensagens import criar_mensagem, obter_ultima_resposta_assistente
from .runs import criar_run, aguardar_run, submeter_resposta_ferramenta
from .tools import extrair_argumentos_tool_call, extrair_tool_call_info
from .processador import processar_pergunta

# Exportar apenas o necessário
__all__ = [
    "verificar_api_key",
    "client",
    "criar_mensagem",
    "obter_ultima_resposta_assistente",
    "criar_run",
    "aguardar_run",
    "submeter_resposta_ferramenta",
    "extrair_argumentos_tool_call",
    "extrair_tool_call_info",
    "processar_pergunta"
]
