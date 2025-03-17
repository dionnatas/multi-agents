"""
Módulo centralizado para gerenciamento de configurações do sistema.

Este módulo fornece uma interface unificada para acessar todas as configurações
do sistema, incluindo variáveis de ambiente, constantes e parâmetros.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Diretório para armazenar as conversas
CONVERSATIONS_DIR = os.path.join(Path(__file__).resolve().parent, "conversations")
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)

# Configurações da API
API_CONFIG = {
    # Configurações da API Nova (Agents SDK)
    "nova": {
        "max_context_messages": 10,  # Número máximo de mensagens no contexto
        "trace_group_id": "sistema_educacional",  # ID do grupo para traces
        "trace_workflow_name": "Sistema Educacional QA",  # Nome do fluxo de trabalho
    },
    
    # Configurações da API Antiga (Assistants API)
    "antiga": {
        "thread_id": "thread_0mIOj6RDNNeK4Bv3UTk2ZyA2",  # ID do thread
        "orquestrador_id": "asst_WhiiRlPHO2Y8itK1S5PK2ySw",  # ID do assistente orquestrador
        "especialistas": {
            "mat-ass": "asst_2x4SggBYScMn9FUMnXZRo0dd",  # Especialista em Matemática
            "port-ass": "asst_yjGrXrWzLIyEJJbZMHV0jNEH",  # Especialista em Português
            "hist-ass": "asst_JbBTnVoYmjnIhvBnDGbEAMdO",  # Especialista em História
            "geo-ass": "asst_ZHaQxRnNmgVONLbmHjLFvBCc",  # Especialista em Geografia
            "fis-ass": "asst_Uf4LKtdZGwOJdvNRGQsIzDrw",  # Especialista em Física
            "quim-ass": "asst_Uf4LKtdZGwOJdvNRGQsIzDrw",  # Especialista em Química
            "bio-ass": "asst_Uf4LKtdZGwOJdvNRGQsIzDrw",  # Especialista em Biologia
        },
        "tempo_espera": 1,  # Tempo de espera entre verificações de status (segundos)
        "status_em_andamento": ["queued", "in_progress", "requires_action"],
        "status_finalizados": ["completed", "failed", "cancelled", "expired"],
    }
}

class ConfigManager:
    """Gerencia as configurações do sistema."""
    
    @staticmethod
    def get_api_key() -> Optional[str]:
        """
        Obtém a chave da API da OpenAI de forma segura.
        
        Returns:
            str ou None: A chave da API ou None se não estiver configurada
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        
        if not api_key:
            return None
            
        return api_key
    
    @staticmethod
    def validate_api_key() -> bool:
        """
        Verifica se a chave da API da OpenAI está configurada.
        
        Returns:
            bool: True se a chave está configurada, False caso contrário
        """
        api_key = ConfigManager.get_api_key()
        
        if not api_key:
            print("ERRO: OPENAI_API_KEY não está configurada.")
            print("Por favor, execute o script run.sh para configurar a variável de ambiente.")
            return False
        
        # Exibe apenas os primeiros caracteres da chave para confirmação
        print(f"API Key detectada: {api_key[:8]}...")
        return True
    
    @staticmethod
    def get_config(api_type: str, key: str = None) -> Any:
        """
        Obtém uma configuração específica.
        
        Args:
            api_type: Tipo de API ('nova' ou 'antiga')
            key: Chave da configuração (opcional)
            
        Returns:
            O valor da configuração ou o dicionário completo se key for None
        """
        if api_type not in API_CONFIG:
            raise ValueError(f"Tipo de API inválido: {api_type}. Use 'nova' ou 'antiga'.")
        
        if key is None:
            return API_CONFIG[api_type]
        
        if key not in API_CONFIG[api_type]:
            raise ValueError(f"Configuração '{key}' não encontrada para a API {api_type}.")
        
        return API_CONFIG[api_type][key]
    
    @staticmethod
    def get_conversations_dir() -> str:
        """
        Obtém o diretório para armazenamento de conversas.
        
        Returns:
            str: Caminho para o diretório de conversas
        """
        return CONVERSATIONS_DIR
