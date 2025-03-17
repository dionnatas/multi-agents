"""
Configurações para a API antiga da OpenAI.

Este módulo contém constantes e configurações utilizadas pelos demais módulos.
"""

# IDs dos threads e assistentes
THREAD_ID = "thread_0mIOj6RDNNeK4Bv3UTk2ZyA2"  # ID real do thread
ORQUESTRADOR_ID = "asst_WhiiRlPHO2Y8itK1S5PK2ySw"  # ID real do assistente orquestrador

# Mapeamento de especialistas
ESPECIALISTAS = {
    "mat-ass": "asst_2x4SggBYScMn9FUMnXZRo0dd",  # Especialista em Matemática
    "port-ass": "asst_QqqqLr2X6o3ooM6NLADZdD2Q",  # Especialista em Português
    "his-ass": "asst_H7j2hPFtkEpNFmFlgiNmFNq2"   # Especialista em História
}

# Status possíveis para os runs
STATUS_EM_ANDAMENTO = ["queued", "in_progress"]
STATUS_FINALIZADOS = ["completed", "failed", "cancelled", "expired"]

# Tempo de espera entre verificações de status (em segundos)
TEMPO_ESPERA = 1
