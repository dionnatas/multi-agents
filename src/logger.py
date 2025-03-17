"""
Módulo para gerenciamento de logs do sistema.

Este módulo implementa um sistema de logging estruturado para facilitar
o diagnóstico de problemas e monitoramento do sistema.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Diretório para armazenar os logs
LOGS_DIR = os.path.join(Path(__file__).resolve().parent.parent, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

# Configuração do formato de log
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Níveis de log
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}

# Configuração padrão
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_TO_FILE = True
DEFAULT_LOG_TO_CONSOLE = True

class Logger:
    """Gerencia o sistema de logging."""
    
    _loggers = {}
    
    @staticmethod
    def setup(name: str, 
              level: str = DEFAULT_LOG_LEVEL, 
              log_to_file: bool = DEFAULT_LOG_TO_FILE,
              log_to_console: bool = DEFAULT_LOG_TO_CONSOLE) -> logging.Logger:
        """
        Configura um logger com o nome especificado.
        
        Args:
            name: Nome do logger
            level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_to_file: Se True, logs serão salvos em arquivo
            log_to_console: Se True, logs serão exibidos no console
            
        Returns:
            logging.Logger: O logger configurado
        """
        # Verificar se o logger já existe
        if name in Logger._loggers:
            return Logger._loggers[name]
        
        # Criar novo logger
        logger = logging.getLogger(name)
        
        # Definir nível de log
        log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
        logger.setLevel(log_level)
        
        # Limpar handlers existentes
        if logger.handlers:
            logger.handlers.clear()
        
        # Adicionar handler para console
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
            logger.addHandler(console_handler)
        
        # Adicionar handler para arquivo
        if log_to_file:
            log_file = os.path.join(LOGS_DIR, f"{name}_{datetime.now().strftime('%Y%m%d')}.log")
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(logging.Formatter(LOG_FORMAT, DATE_FORMAT))
            logger.addHandler(file_handler)
        
        # Armazenar o logger
        Logger._loggers[name] = logger
        
        return logger
    
    @staticmethod
    def get(name: str) -> logging.Logger:
        """
        Obtém um logger existente ou cria um novo com configurações padrão.
        
        Args:
            name: Nome do logger
            
        Returns:
            logging.Logger: O logger solicitado
        """
        if name not in Logger._loggers:
            return Logger.setup(name)
        
        return Logger._loggers[name]

# Configurar logger principal
main_logger = Logger.setup("sistema_educacional")

# Função para facilitar o acesso ao logger principal
def log():
    """
    Obtém o logger principal do sistema.
    
    Returns:
        logging.Logger: O logger principal
    """
    return main_logger
