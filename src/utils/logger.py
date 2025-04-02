"""
Moduł zawierający klasę do kolorowych logów konsolowych.
"""

import datetime
import platform
from enum import Enum
import colorama


class LogLevel(Enum):
    """Poziomy logowania."""
    DEBUG = 0
    INFO = 1
    WARN = 2
    ERROR = 3


class ColorLogger:
    """
    Klasa do kolorowych logów konsolowych.
    Zawiera metody do wyświetlania komunikatów w różnych kolorach,
    w zależności od poziomu logowania.
    """

    # Kody ANSI dla kolorów
    COLORS = {
        "RESET": "\033[0m",
        "RED": "\033[91m",     # Jasny czerwony
        "GREEN": "\033[92m",   # Jasny zielony
        "YELLOW": "\033[93m",  # Jasny żółty
        "BLUE": "\033[94m",    # Jasny niebieski
        "MAGENTA": "\033[95m", # Jasny magenta
        "CYAN": "\033[96m",    # Jasny cyjan
        "WHITE": "\033[97m",   # Biały
    }

    def __init__(self, level=LogLevel.INFO, show_timestamps=True):
        """
        Inicjalizacja loggera.
        
        Args:
            level (LogLevel): Minimalny poziom logowania (domyślnie INFO)
            show_timestamps (bool): Czy pokazywać znaczniki czasu (domyślnie True)
        """
        if platform.system() == 'Windows':
            colorama.init()  # Inicjalizacja colorama dla Windows
        self.level = level
        self.show_timestamps = show_timestamps

    def _get_timestamp(self):
        """Zwraca aktualny znacznik czasu."""
        if self.show_timestamps:
            now = datetime.datetime.now()
            return f"[{now.strftime('%H:%M:%S.%f')[:-3]}] "
        return ""

    def _log(self, level, color, prefix, message):
        """
        Główna metoda logowania.
        
        Args:
            level (LogLevel): Poziom logowania wiadomości
            color (str): Kod koloru ANSI
            prefix (str): Prefiks wiadomości (DEBUG, INFO, itp.)
            message (str): Treść wiadomości
        """
        if level.value >= self.level.value:
            timestamp = self._get_timestamp()
            colored_prefix = f"{color}{prefix}{self.COLORS['RESET']}"
            print(f"{timestamp}{colored_prefix} {message}")

    def debug(self, message):
        """
        Logowanie na poziomie DEBUG (niebieski).
        
        Args:
            message (str): Treść wiadomości
        """
        self._log(LogLevel.DEBUG, self.COLORS["BLUE"], "[DEBUG]", message)

    def info(self, message):
        """
        Logowanie na poziomie INFO (zielony).
        
        Args:
            message (str): Treść wiadomości
        """
        self._log(LogLevel.INFO, self.COLORS["GREEN"], "[INFO]", message)

    def warn(self, message):
        """
        Logowanie na poziomie WARN (żółty).
        
        Args:
            message (str): Treść wiadomości
        """
        self._log(LogLevel.WARN, self.COLORS["YELLOW"], "[UWAGA]", message)

    def error(self, message):
        """
        Logowanie na poziomie ERROR (czerwony).
        
        Args:
            message (str): Treść wiadomości
        """
        self._log(LogLevel.ERROR, self.COLORS["RED"], "[BŁĄD]", message)


# Utworzenie domyślnej instancji loggera
logger = ColorLogger() 