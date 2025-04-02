# Rozwiązywanie problemów

Na tej stronie znajdziesz rozwiązania najczęstszych problemów, które możesz napotkać podczas pracy z projektem Trass Recommendation.

## Problemy z instalacją

### ModuleNotFoundError: No module named 'PyQt6'

**Problem:** Po instalacji, przy próbie uruchomienia aplikacji pojawia się błąd związany z brakiem modułu PyQt6.

**Rozwiązanie:**
1. Upewnij się, że masz aktywne środowisko wirtualne
2. Zainstaluj ponownie PyQt6:
```bash
pip install PyQt6==6.6.1
```
3. Jeśli używasz Windows, może być konieczne zainstalowanie dodatkowo:
```bash
pip install PyQt6-Qt6==6.6.1
pip install PyQt6-sip==13.6.0
```

### Błąd przy instalacji PyQt6 na Linux

**Problem:** Podczas instalacji PyQt6 na systemie Linux pojawiają się błędy kompilacji.

**Rozwiązanie:**
1. Zainstaluj wymagane pakiety systemowe:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libxcb-xinerama0 libxcb-xinerama0-dev libxkbcommon-x11-0 libxkbcommon-dev

# Fedora
sudo dnf install python3-devel libxkbcommon-x11 libxkbcommon-devel
```
2. Spróbuj ponownie zainstalować PyQt6

### Niekompatybilna wersja Node.js lub pnpm

**Problem:** Podczas instalacji lub uruchamiania pojawia się błąd związany z wersją Node.js lub pnpm.

**Rozwiązanie:**
1. Sprawdź wymagane wersje:
```bash
node -v  # Powinno być 20.0.0 lub nowsze
pnpm -v  # Powinno być 9.12.3 lub nowsze
```

2. Zaktualizuj Node.js za pomocą NVM:
```bash
# Instalacja NVM
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash

# Instalacja i użycie wymaganej wersji
nvm install 20
nvm use 20
```

3. Zaktualizuj pnpm:
```bash
npm install -g pnpm@latest
```

## Problemy z uruchamianiem

### Aplikacja uruchamia się, ale nie wyświetla interfejsu

**Problem:** Aplikacja uruchamia się bez błędów, ale nie pojawia się okno interfejsu.

**Rozwiązanie:**
1. Sprawdź, czy nie występują błędy w konsoli
2. Upewnij się, że używasz właściwej wersji PyQt6
3. Na systemach Unix-like sprawdź, czy masz poprawnie skonfigurowany serwer X11:
```bash
echo $DISPLAY
# Powinno zwrócić np. :0
```

### Błędy podczas importowania modułów

**Problem:** Podczas uruchamiania aplikacji pojawiają się błędy importu.

**Rozwiązanie:**
1. Upewnij się, że zainstalowałeś pakiet w trybie edycyjnym:
```bash
pip install -e .
```
2. Sprawdź strukturę projektu i poprawność importów
3. Upewnij się, że uruchamiasz aplikację z głównego katalogu projektu

### Problemy z PYTHONPATH przy budowaniu EXE

**Problem:** Podczas budowania pliku EXE pojawiają się błędy związane z importem modułów z pakietu `src`.

**Rozwiązanie:**
1. Dodaj katalog główny projektu do zmiennej środowiskowej PYTHONPATH:
```bash
# Windows (PowerShell)
$env:PYTHONPATH = $env:PYTHONPATH + ";C:\ścieżka\do\projektu"

# Windows (CMD)
set PYTHONPATH=%PYTHONPATH%;C:\ścieżka\do\projektu

# Linux/MacOS
export PYTHONPATH=$PYTHONPATH:/ścieżka/do/projektu
```
2. Upewnij się, że pakiet jest poprawnie skonfigurowany w pliku `setup.py`:
```python
setup(
    # ...
    packages=find_packages(include=["src", "src.*"]),
    include_package_data=True,
    # ...
)
```
3. Po wprowadzeniu zmian w `setup.py`, przeinstaluj pakiet w trybie edycyjnym:
```bash
pip install -e . --no-warn-script-location
```

## Problemy z wydajnością

### Aplikacja działa wolno

**Problem:** Interfejs aplikacji reaguje z opóźnieniem lub przetwarza dane zbyt wolno.

**Rozwiązanie:**
1. Sprawdź obciążenie systemu podczas działania aplikacji
2. Zoptymalizuj algorytmy przetwarzania danych
3. Rozważ użycie wielowątkowości dla ciężkich operacji:
```python
from PyQt6.QtCore import QThread, pyqtSignal

class WorkerThread(QThread):
    finished = pyqtSignal(object)
    
    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        
    def run(self):
        result = self.function(*self.args, **self.kwargs)
        self.finished.emit(result)
```

## Problemy z testami

### Testy nie znajdują modułów

**Problem:** Podczas uruchamiania testów pojawiają się błędy importu modułów.

**Rozwiązanie:**
1. Upewnij się, że zainstalowałeś pakiet w trybie edycyjnym
2. Sprawdź, czy struktura importów w testach jest poprawna
3. Dodaj katalog główny projektu do `PYTHONPATH`:
```bash
# Windows
set PYTHONPATH=.

# Linux/MacOS
export PYTHONPATH=.
```

### Testy UI się nie uruchamiają

**Problem:** Testy interfejsu użytkownika nie uruchamiają się lub kończą się błędami.

**Rozwiązanie:**
1. Upewnij się, że masz zainstalowany pakiet `pytest-qt`:
```bash
pip install pytest-qt
```
2. Na systemach bez interfejsu graficznego, użyj wirtualnego serwera X:
```bash
# Instalacja na Ubuntu/Debian
sudo apt-get install xvfb

# Uruchamianie testów
xvfb-run pytest tests/test_ui/
```

## Problemy z dokumentacją

### Błędy przy uruchamianiu dokumentacji VitePress

**Problem:** Podczas uruchamiania lub budowania dokumentacji VitePress występują błędy.

**Rozwiązanie:**
1. Upewnij się, że masz zainstalowane wymagane pakiety:
```bash
pnpm install
```
2. Sprawdź, czy używasz wymaganej wersji Node.js i pnpm:
```bash
node -v  # Powinno być 20.0.0 lub nowsze
pnpm -v  # Powinno być 9.12.3 lub nowsze
```
3. Wyczyść pamięć podręczną i zainstaluj ponownie zależności:
```bash
pnpm cache clean
rm -rf node_modules
pnpm install
```

### Błędy związane z TypeScript

**Problem:** Występują błędy kompilacji TypeScript podczas uruchamiania lub budowania dokumentacji.

**Rozwiązanie:**
1. Sprawdź, czy pliki TypeScript mają poprawną składnię:
```bash
pnpm exec tsc --noEmit
```
2. Upewnij się, że masz prawidłowo skonfigurowane pliki tsconfig.json
3. Sprawdź, czy zależności TypeScript są zainstalowane:
```bash
pnpm install typescript@5.3.3 @types/node@20.11.5
```
4. Jeśli problem dotyczy konkretnego importu, sprawdź czy masz zainstalowany odpowiedni pakiet @types

### Problemy z hot-reloadingiem dokumentacji

**Problem:** Zmiany w plikach dokumentacji nie są automatycznie odświeżane w przeglądarce.

**Rozwiązanie:**
1. Upewnij się, że serwer deweloperski działa poprawnie
2. Spróbuj ponownie uruchomić serwer:
```bash
pnpm docs:dev
```
3. Sprawdź, czy twoja przeglądarka nie blokuje websocket używanego do hot-reloadingu
4. Sprawdź, czy w systemie nie ma oprogramowania blokującego komunikację na portach używanych przez VitePress (domyślnie 5173)

## Problemy z danymi

### Aplikacja nie może załadować danych

**Problem:** Aplikacja wyświetla błędy związane z ładowaniem lub brakiem danych.

**Rozwiązanie:**
1. Sprawdź, czy pliki danych istnieją w oczekiwanej lokalizacji
2. Upewnij się, że format danych jest poprawny
3. Dodaj obsługę błędów w kodzie, aby zapewnić bardziej informacyjne komunikaty:
```python
try:
    data = load_data(path)
except FileNotFoundError:
    print(f"Nie znaleziono pliku danych: {path}")
    # Utwórz dane domyślne lub poproś użytkownika o podanie ścieżki
except ValueError as e:
    print(f"Nieprawidłowy format danych: {e}")
    # Obsłuż błędny format
```

## Kontakt i zgłaszanie problemów

Jeśli napotkałeś problem, który nie został opisany w tej sekcji:

1. Sprawdź istniejące zgłoszenia problemów w repozytorium projektu
2. Utwórz nowe zgłoszenie, zawierające:
   - Dokładny opis problemu
   - Kroki umożliwiające odtworzenie problemu
   - Logi i komunikaty błędów
   - Informacje o środowisku (system operacyjny, wersja Python, Node.js, pnpm, itp.)
3. Skontaktuj się z [zespołem wsparcia](mailto:support@example.com) 