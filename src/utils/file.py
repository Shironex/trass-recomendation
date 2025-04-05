"""
Moduł zawierający funkcje pomocnicze do obsługi operacji na plikach.
"""

from pathlib import Path
from typing import Callable, Any
from src.utils.logger import logger


def prepare_file_path(filepath: str) -> None:
    """
    Przygotowuje ścieżkę do zapisu pliku, tworząc niezbędne katalogi.
    
    Args:
        filepath: Ścieżka do pliku.
    """
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)


def handle_save_error(error: Exception, file_type: str) -> None:
    """
    Obsługuje błędy podczas zapisywania plików.
    
    Args:
        error: Wyjątek, który wystąpił.
        file_type: Typ pliku (CSV, JSON itp.).
        
    Raises:
        ValueError: Przekształcony wyjątek z odpowiednim komunikatem.
    """
    error_msg = f"Błąd podczas zapisywania danych do {file_type}: {str(error)}"
    logger.error(error_msg)
    raise ValueError(error_msg)


def safe_file_operation(operation: Callable, filepath: str, file_type: str, *args, **kwargs) -> Any:
    """
    Wykonuje operację na pliku z odpowiednią obsługą błędów i przygotowaniem ścieżki.
    
    Args:
        operation: Funkcja wykonująca operację na pliku.
        filepath: Ścieżka do pliku.
        file_type: Typ pliku (CSV, JSON itp.).
        *args: Dodatkowe argumenty przekazywane do funkcji operation.
        **kwargs: Dodatkowe argumenty nazwane przekazywane do funkcji operation.
        
    Returns:
        Wynik wywołania funkcji operation.
        
    Raises:
        ValueError: Gdy operacja nie powiodła się.
    """
    try:
        # Przygotowanie ścieżki
        prepare_file_path(filepath)
        
        # Wykonanie operacji
        result = operation(filepath, *args, **kwargs)
        
        logger.info(f"Pomyślnie wykonano operację na pliku {file_type}: {filepath}")
        return result
    except Exception as e:
        handle_save_error(e, file_type) 