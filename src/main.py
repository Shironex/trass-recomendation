"""
Główny plik aplikacji - punkt wejścia.
"""

import sys
import argparse
from PyQt6.QtWidgets import QApplication
from ui.main import MainWindow
from src.utils import logger, LogLevel

# Funkcja do włączania hot reload
def try_enable_hot_reload():
    """Próbuje włączyć hot reload, jeśli dostępny."""
    try:
        from src.hot_reload import enable_hot_reload
        # Włączamy hot reload dla katalogu src (domyślne ustawienie)
        reloader = enable_hot_reload(directories=['src/ui/pages'])
        return reloader
    except ImportError as e:
        logger.warn(f"Hot reload nie jest dostępny: {str(e)}")
        logger.info("Aby włączyć hot reload, zainstaluj watchdog: pnpm run install watchdog")
        return None

if __name__ == "__main__":
    # Parsowanie argumentów linii poleceń
    parser = argparse.ArgumentParser(description="Rekomendator Tras Turystycznych")
    parser.add_argument("--hot-reload", action="store_true", help="Włącz hot reload (automatyczne przeładowanie przy zmianach)")
    parser.add_argument("--debug", action="store_true", help="Włącz tryb debugowania (więcej logów)")
    args = parser.parse_args()
    
    # Ustawienie poziomu logowania
    if args.debug:
        logger.level = LogLevel.DEBUG
    else:
        logger.level = LogLevel.INFO
    
    logger.info("Uruchamianie aplikacji Rekomendator Tras Turystycznych")
    
    # Włączenie hot reload, jeśli wybrano odpowiednią opcję
    reloader = None
    if args.hot_reload:
        logger.info("Próba włączenia hot reloadu")
        reloader = try_enable_hot_reload()
    
    # Inicjalizacja aplikacji Qt
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Błąd podczas wykonania aplikacji: {str(e)}") 