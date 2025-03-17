"""
Módulo para gerenciamento de histórico de conversas para a SDK de Agentes da OpenAI.

Este módulo implementa um sistema de armazenamento de conversas que permite manter
o contexto entre sessões diferentes, similar ao THREAD_ID da API antiga.
"""

import json
import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import uuid
from datetime import datetime

# Adicionar o diretório raiz ao path para permitir importações dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Diretório para armazenar as conversas
CONVERSATIONS_DIR = os.path.join(os.path.dirname(__file__), "conversations")
os.makedirs(CONVERSATIONS_DIR, exist_ok=True)


@dataclass
class Message:
    """Representa uma mensagem na conversa."""
    role: str  # "user" ou "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class Conversation:
    """Representa uma conversa completa."""
    id: str
    name: str = ""
    messages: List[Message] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


class ConversationStore:
    """Gerencia o armazenamento e recuperação de conversas."""

    @staticmethod
    def create_conversation(name: str = "") -> str:
        """
        Cria uma nova conversa e retorna seu ID.
        
        Args:
            name (str, opcional): Nome personalizado para a conversa
            
        Returns:
            str: ID da conversa criada
        """
        conversation_id = str(uuid.uuid4())
        conversation = Conversation(id=conversation_id, name=name)
        
        # Salvar a conversa vazia
        ConversationStore._save_conversation(conversation)
        
        return conversation_id

    @staticmethod
    def add_message(conversation_id: str, role: str, content: str) -> None:
        """
        Adiciona uma mensagem a uma conversa existente.
        
        Args:
            conversation_id: ID da conversa
            role: Papel do remetente ("user" ou "assistant")
            content: Conteúdo da mensagem
        """
        conversation = ConversationStore.get_conversation(conversation_id)
        if not conversation:
            # Se a conversa não existir, cria uma nova
            conversation = Conversation(id=conversation_id)
        # Importante: preservar o nome da conversa se já existir
        
        # Adicionar a mensagem
        message = Message(role=role, content=content)
        conversation.messages.append(message)
        conversation.updated_at = datetime.now().isoformat()
        
        # Salvar a conversa atualizada
        ConversationStore._save_conversation(conversation)

    @staticmethod
    def get_conversation(conversation_id: str) -> Optional[Conversation]:
        """
        Recupera uma conversa pelo ID.
        
        Args:
            conversation_id: ID da conversa
            
        Returns:
            Conversation ou None se não encontrada
        """
        file_path = os.path.join(CONVERSATIONS_DIR, f"{conversation_id}.json")
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Reconstruir a conversa a partir dos dados
            conversation = Conversation(
                id=data['id'],
                name=data.get('name', ''),  # Carregar o nome da conversa
                created_at=data['created_at'],
                updated_at=data['updated_at'],
                metadata=data.get('metadata', {})
            )
            
            # Reconstruir as mensagens
            for msg_data in data.get('messages', []):
                message = Message(
                    role=msg_data['role'],
                    content=msg_data['content'],
                    timestamp=msg_data['timestamp']
                )
                conversation.messages.append(message)
                
            return conversation
        except Exception as e:
            print(f"Erro ao carregar conversa {conversation_id}: {e}")
            return None

    @staticmethod
    def get_messages_as_input_list(conversation_id: str) -> List[Dict[str, str]]:
        """
        Recupera as mensagens de uma conversa no formato esperado pela SDK de Agentes.
        
        Args:
            conversation_id: ID da conversa
            
        Returns:
            Lista de mensagens no formato esperado pela SDK
        """
        conversation = ConversationStore.get_conversation(conversation_id)
        if not conversation:
            return []
        
        # Converter para o formato esperado pela SDK
        return [{"role": msg.role, "content": msg.content} for msg in conversation.messages]

    @staticmethod
    def _save_conversation(conversation: Conversation) -> None:
        """
        Salva uma conversa no armazenamento.
        
        Args:
            conversation: Objeto da conversa a ser salvo
        """
        file_path = os.path.join(CONVERSATIONS_DIR, f"{conversation.id}.json")
        
        # Converter para dicionário
        data = asdict(conversation)
        
        # Salvar como JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    @staticmethod
    def list_conversations() -> List[str]:
        """
        Lista todos os IDs de conversas disponíveis.
        
        Returns:
            Lista de IDs de conversas
        """
        conversations = []
        for filename in os.listdir(CONVERSATIONS_DIR):
            if filename.endswith('.json'):
                conversations.append(filename[:-5])  # Remover a extensão .json
        return conversations
