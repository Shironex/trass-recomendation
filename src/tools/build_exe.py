"""
Skrypt do budowania aplikacji jako plik EXE za pomocą PyInstaller.
"""

import os
import sys
import shutil
from pathlib import Path
import argparse

try:
    import PyInstaller.__main__
except ImportError:
    print("Brak modułu PyInstaller. Zainstaluj go używając: pip install pyinstaller")
    raise

# Dodanie katalogu głównego projektu do ścieżki Pythona, jeśli uruchamiamy skrypt bezpośrednio
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import modułów z pakietu src
from src.utils import logger, LogLevel

# Import modułu create_icon - obsługa zarówno jako moduł jak i jako bezpośredni plik
try:
    # Próba importu względnego (działa, gdy uruchamiamy jako moduł)
    from .create_icon import create_app_icon
except ImportError:
    # Próba importu bezpośredniego (działa, gdy uruchamiamy jako plik)
    from src.tools.create_icon import create_app_icon

# Ścieżka do katalogu zasobów w src/tools
TOOLS_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = TOOLS_DIR / "resources"

def build_exe(one_file=False, console=False, clean=False):
    """
    Buduje aplikację jako plik EXE za pomocą PyInstaller.
    
    Args:
        one_file (bool): Czy budować jako pojedynczy plik EXE.
        console (bool): Czy aplikacja ma pokazywać konsolę.
        clean (bool): Czy usunąć pliki tymczasowe przed budowaniem.
    """
    logger.info("Budowanie aplikacji jako plik EXE...")
    
    # Zmiana katalogu roboczego na katalog główny projektu
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent
    os.chdir(project_root)
    
    # Katalogi budowy
    build_dir = "build"
    dist_dir = "dist"
    
    # Usuwanie poprzednich plików budowy
    if clean and os.path.exists(build_dir):
        logger.info(f"Usuwanie katalogu {build_dir}...")
        shutil.rmtree(build_dir)
    
    if clean and os.path.exists(dist_dir):
        logger.info(f"Usuwanie katalogu {dist_dir}...")
        shutil.rmtree(dist_dir)
    
    # Nazwa i ścieżka ikony aplikacji
    ico_path = RESOURCES_DIR / "icon.ico"
    
    # Sprawdzenie, czy ikona istnieje
    if not ico_path.exists():
        logger.warn("Plik ikony nie został znaleziony. Zostanie użyta domyślna ikona.")
        ico_path = None
    else:
        # Konwersja do bezwzględnej ścieżki string
        ico_path = str(ico_path.absolute())
    
    # Główny plik aplikacji
    main_file = os.path.join("src", "main.py")
    
    # Dodatkowe dane
    added_data = [
        # (source, destination)
        # Przykład: ("resources", "resources")
    ]
    
    # Przygotowanie argumentów dla PyInstaller
    args = [
        main_file,
        "--name=TrassRecommendation",
        "--clean",
        "--noconfirm",
    ]
    
    # Dodanie argumentu dla ikony
    if ico_path:
        args.append(f"--icon={ico_path}")
    
    # Dodanie argumentu dla budowania jako pojedynczy plik
    if one_file:
        args.append("--onefile")
    else:
        args.append("--onedir")
    
    # Dodanie argumentu dla pokazywania/ukrywania konsoli
    if console:
        args.append("--console")
    else:
        args.append("--windowed")
    
    # Dodanie dodatkowych danych
    for src, dst in added_data:
        args.append(f"--add-data={src}{os.pathsep}{dst}")
    
    # Dodanie ścieżek dla importów
    args.append("--paths=.")
    
    # Dodanie ukrytych importów
    hidden_imports = [
        "PyQt6.QtCore",
        "PyQt6.QtWidgets",
        "PyQt6.QtGui",
    ]
    for imp in hidden_imports:
        args.append(f"--hidden-import={imp}")
    
    try:
        # Uruchomienie PyInstaller
        logger.debug(f"Uruchamianie PyInstaller z argumentami: {args}")
        PyInstaller.__main__.run(args)
        
        logger.info("Budowanie zakończone pomyślnie!")
        
        output_path = os.path.join(dist_dir, "TrassRecommendation")
        if one_file:
            output_path += ".exe"
            logger.info(f"Plik EXE znajduje się w: {output_path}")
        else:
            logger.info(f"Katalog z aplikacją znajduje się w: {output_path}")
        
    except Exception as e:
        logger.error(f"Błąd podczas budowania: {str(e)}")
        return False
    
    return True

def create_resources_dir():
    """Tworzy katalog resources w katalogu src/tools, jeśli nie istnieje."""
    if not RESOURCES_DIR.exists():
        RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Utworzono katalog {RESOURCES_DIR}")

def main():
    # Ustawienie poziomu logowania na DEBUG
    logger.level = LogLevel.DEBUG
    
    parser = argparse.ArgumentParser(description="Budowanie aplikacji jako plik EXE")
    parser.add_argument("--onefile", action="store_true", help="Buduj jako pojedynczy plik EXE")
    parser.add_argument("--console", action="store_true", help="Pokaż konsolę podczas uruchamiania aplikacji")
    parser.add_argument("--clean", action="store_true", help="Usuń pliki tymczasowe przed budowaniem")
    parser.add_argument("--generate-icon", action="store_true", help="Wygeneruj ikonę aplikacji przed budowaniem")
    parser.add_argument("--quiet", action="store_true", help="Pokazuj tylko ważne komunikaty (logowanie na poziomie INFO)")
    
    args = parser.parse_args()
    
    # Ustawienie poziomu logowania na INFO, jeśli wybrano opcję --quiet
    if args.quiet:
        logger.level = LogLevel.INFO
    
    create_resources_dir()
    
    # Generowanie ikony jeśli wybrano odpowiednią opcję
    if args.generate_icon:
        logger.info("Generowanie ikony aplikacji...")
        output_path = str(RESOURCES_DIR / "icon.ico")
        create_app_icon(output_path=output_path)
    
    build_exe(one_file=args.onefile, console=args.console, clean=args.clean)

if __name__ == "__main__":
    main() 