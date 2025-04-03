"""
Główny plik aplikacji - punkt wejścia.
"""

import sys
import argparse
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from ui.main import MainWindow
from src.utils import logger, LogLevel
from src.config import Config
# Ścieżka do katalogu zasobów
RESOURCES_DIR = Path("src/tools/resources") 

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
    config = Config()
    parser = argparse.ArgumentParser(description=config.app_title)
    parser.add_argument("--hot-reload", action="store_true", help="Włącz hot reload (automatyczne przeładowanie przy zmianach)")
    parser.add_argument("--debug", action="store_true", help="Włącz tryb debugowania (więcej logów)")
    parser.add_argument("--hot-reload-level", action="store_true", help="Ustaw poziom logowania na HOT_RELOAD (logi hot reload i wyższe)")
    args = parser.parse_args()
    
    # Ustawienie poziomu logowania
    if args.debug:
        logger.level = LogLevel.DEBUG
    elif args.hot_reload_level:
        logger.level = LogLevel.HOT_RELOAD
    else:
        logger.level = LogLevel.INFO
    
    logger.info(f"Uruchamianie aplikacji {config.app_title}")
    
    # Włączenie hot reload, jeśli wybrano odpowiednią opcję
    reloader = None
    if args.hot_reload:
        logger.hot_reload("Próba włączenia hot reloadu")
        reloader = try_enable_hot_reload()
    
    # Inicjalizacja aplikacji Qt
    app = QApplication(sys.argv)
    
    # Ustawienie ikony aplikacji
    try:
        # Specjalne ustawienie dla Windows
        import ctypes
        myappid = config.APP_NAME  # dowolny unikalny string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        logger.debug("Ustawiono AppUserModelID dla Windows")
    except Exception as e:
        logger.warning(f"Nie udało się ustawić AppUserModelID: {e}")

    # Ustawienie ikony aplikacji
    icon_path = RESOURCES_DIR
    if icon_path.exists():
        app_icon = QIcon()
        # Dodanie wszystkich rozmiarów ikon w kolejności od najmniejszej do największej
        icon_sizes = [16, 24, 32, 48, 128, 256]
        for size in icon_sizes:
            icon_file = f'src/tools/resources/icon_{size}x{size}.png'
            if Path(icon_file).exists():
                app_icon.addFile(icon_file, QSize(size, size))
                logger.debug(f"Dodano ikonę {size}x{size}")
        
        # Ustawienie ikony dla aplikacji
        app.setWindowIcon(app_icon)
        
        # Ustawienie ikony dla głównego okna
        window = MainWindow()
        window.setWindowIcon(app_icon)
        logger.debug(f"Ustawiono ikonę aplikacji: {icon_path}")
    else:
        logger.warning(f"Nie znaleziono pliku ikony: {icon_path}")
        window = MainWindow()
    
    window.show()
    
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Błąd podczas wykonania aplikacji: {str(e)}") 