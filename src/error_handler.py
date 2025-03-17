"""
Módulo para tratamento de erros e exceções do sistema.

Este módulo implementa um sistema centralizado para gerenciar exceções
e erros, facilitando o diagnóstico e tratamento de problemas.
"""

import sys
import traceback
from functools import wraps
from typing import Callable, Any, Type, Union, List, Dict, Optional

from src.logger import Logger

# Configurar logger específico para erros
error_logger = Logger.setup("erros", level="ERROR")

class AppError(Exception):
    """Classe base para exceções da aplicação."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Inicializa uma nova exceção da aplicação.
        
        Args:
            message: Mensagem de erro
            details: Detalhes adicionais sobre o erro (opcional)
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)


class APIKeyError(AppError):
    """Exceção para problemas com a chave da API."""
    pass


class APIConnectionError(AppError):
    """Exceção para problemas de conexão com a API."""
    pass


class APIResponseError(AppError):
    """Exceção para respostas de erro da API."""
    pass


class ConfigError(AppError):
    """Exceção para problemas de configuração."""
    pass


class ValidationError(AppError):
    """Exceção para erros de validação de dados."""
    pass


class ErrorHandler:
    """Gerencia o tratamento de erros e exceções."""
    
    @staticmethod
    def handle_error(error: Exception, log_error: bool = True) -> Dict[str, Any]:
        """
        Trata uma exceção e retorna informações estruturadas sobre o erro.
        
        Args:
            error: A exceção a ser tratada
            log_error: Se True, registra o erro no log
            
        Returns:
            Dict: Informações estruturadas sobre o erro
        """
        # Extrair informações do erro
        error_type = type(error).__name__
        error_message = str(error)
        error_traceback = traceback.format_exc()
        
        # Registrar o erro no log
        if log_error:
            error_logger.error(f"{error_type}: {error_message}\n{error_traceback}")
        
        # Construir resposta estruturada
        error_info = {
            "type": error_type,
            "message": error_message,
            "traceback": error_traceback,
        }
        
        # Adicionar detalhes extras para AppError
        if isinstance(error, AppError) and error.details:
            error_info["details"] = error.details
        
        return error_info
    
    @staticmethod
    def format_user_message(error: Exception) -> str:
        """
        Formata uma mensagem amigável para o usuário com base no erro.
        
        Args:
            error: A exceção a ser formatada
            
        Returns:
            str: Mensagem formatada para o usuário
        """
        if isinstance(error, APIKeyError):
            return "Erro de configuração: A chave da API não está configurada corretamente. Por favor, verifique suas configurações."
        
        elif isinstance(error, APIConnectionError):
            return "Erro de conexão: Não foi possível conectar à API da OpenAI. Verifique sua conexão com a internet ou tente novamente mais tarde."
        
        elif isinstance(error, APIResponseError):
            return f"Erro na resposta da API: {error.message}"
        
        elif isinstance(error, ConfigError):
            return f"Erro de configuração: {error.message}"
        
        elif isinstance(error, ValidationError):
            return f"Erro de validação: {error.message}"
        
        else:
            return f"Ocorreu um erro inesperado: {str(error)}"


def catch_errors(func: Callable) -> Callable:
    """
    Decorador para capturar e tratar exceções em funções.
    
    Este decorador registra todas as exceções, mas propaga exceções específicas da aplicação
    (APIKeyError, APIConnectionError, ValidationError, etc.) para serem tratadas pelo chamador.
    Apenas exceções genéricas são convertidas em respostas estruturadas.
    
    Args:
        func: A função a ser decorada
        
    Returns:
        Callable: A função decorada
    
    Raises:
        AppError: Propaga exceções específicas da aplicação
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AppError:
            # Registrar o erro, mas propagar exceções específicas da aplicação
            error_logger.error(f"Erro da aplicação capturado: {traceback.format_exc()}")
            raise
        except Exception as e:
            # Tratar exceções genéricas
            error_info = ErrorHandler.handle_error(e)
            user_message = ErrorHandler.format_user_message(e)
            raise AppError(user_message, error_info)
    
    return wrapper


def catch_async_errors(func: Callable) -> Callable:
    """
    Decorador para capturar e tratar exceções em funções assíncronas.
    
    Este decorador registra todas as exceções, mas propaga exceções específicas da aplicação
    (APIKeyError, APIConnectionError, ValidationError, etc.) para serem tratadas pelo chamador.
    Apenas exceções genéricas são convertidas em respostas estruturadas.
    
    Args:
        func: A função assíncrona a ser decorada
        
    Returns:
        Callable: A função decorada
    
    Raises:
        AppError: Propaga exceções específicas da aplicação
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except AppError:
            # Registrar o erro, mas propagar exceções específicas da aplicação
            error_logger.error(f"Erro da aplicação capturado: {traceback.format_exc()}")
            raise
        except Exception as e:
            # Tratar exceções genéricas
            error_info = ErrorHandler.handle_error(e)
            user_message = ErrorHandler.format_user_message(e)
            raise AppError(user_message, error_info)
    
    return wrapper
