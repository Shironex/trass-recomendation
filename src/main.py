"""
Główny plik aplikacji - punkt wejścia.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.main import MainWindow
from src.utils import logger, LogLevel

if __name__ == "__main__":
    # Ustawienie poziomu logowania (opcjonalnie)
    # logger = ColorLogger(LogLevel.DEBUG)  # Pokaż wszystkie komunikaty
    logger.level = LogLevel.DEBUG  # Pokaż wszystkie komunikaty
    
    logger.info("Uruchamianie aplikacji Rekomendator Tras Turystycznych")
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Błąd podczas wykonania aplikacji: {str(e)}") 