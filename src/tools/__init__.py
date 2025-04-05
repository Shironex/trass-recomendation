"""
Pakiet zawierający narzędzia związane z budowaniem i dystrybucją aplikacji.

Ten moduł zawiera narzędzia do budowania aplikacji jako plik EXE i generowania ikony aplikacji.

Przykłady użycia:

1. Generowanie ikony aplikacji:
   ```python
   # Z modułu Python
   from src.tools import create_app_icon
   create_app_icon(output_path="icon.ico", sizes=[32, 64, 128])

   # Z linii poleceń
   python -m src.tools.create_icon
   # lub
   trass-create-icon  # (po instalacji pakietu)
   ```

2. Budowanie aplikacji jako plik EXE:
   ```python
   # Z modułu Python
   from src.tools import build_exe
   build_exe(one_file=True, console=False, clean=True)

   # Z linii poleceń
   python -m src.tools.build_exe --onefile --clean --generate-icon
   # lub
   trass-build-exe --onefile --clean --generate-icon  # (po instalacji pakietu)
   ```

Więcej informacji można znaleźć w dokumentacji: https://shironex.github.io/trass-recomendation/building-exe
"""

import sys
from pathlib import Path

# Dodanie katalogu głównego projektu do ścieżki Pythona, jeśli jest to potrzebne
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Teraz możemy bezpiecznie importować moduły
try:
    # Importy bezwzględne (działa zawsze)
    from src.tools.build_exe import build_exe
    from src.tools.create_icon import create_app_icon
except ImportError as e:
    print(f"Uwaga: Wystąpił błąd podczas importowania: {e}")
    print("Sprawdź, czy katalog główny projektu jest w ścieżce Pythona.")
    # Próba importu względnego w przypadku błędu
    try:
        from .build_exe import build_exe
        from .create_icon import create_app_icon
    except ImportError:
        print("Nie można zaimportować modułów. Upewnij się, że uruchamiasz skrypt z głównego katalogu projektu.")

__all__ = [
    'build_exe',
    'create_app_icon',
] 