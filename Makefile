# --------------------------------
# Makefile dla projektu Trass Recommendation
# --------------------------------

.PHONY: help install install-dev install-build dev build test docs icons install-deps update-deps run dev-hot setup dev-hot-logs

# Zmienne srodowiskowe - używamy pełnych ścieżek z ukośnikami w kierunku naprzód
VENV = venv
PYTHON = $(VENV)/Scripts/python
PIP = $(VENV)/Scripts/pip
PNPM = pnpm
PYTEST = $(VENV)/Scripts/pytest

help:
	@echo Trass Recommendation - dostepne komendy:
	@echo "make install         - Instaluje podstawowe zaleznosci tylko PyQt, Colorama"
	@echo "make install-dev     - Instaluje zaleznosci deweloperskie testy, watchdog, dokumentacja"
	@echo "make install-build   - Instaluje zaleznosci do budowania PyInstaller, Pillow"
	@echo "make dev             - Uruchamia aplikacje w trybie deweloperskim"
	@echo "make dev-hot         - Uruchamia aplikacje z hot reloadingiem"
	@echo "make dev-hot-logs    - Uruchamia aplikacje z hot reloadingiem i tylko logami hot reload"
	@echo "make run             - Uruchamia aplikacje"
	@echo "make test            - Uruchamia testy"
	@echo "make build           - Buduje aplikacje jako plik EXE"
	@echo "make build-debug     - Buduje aplikacje jako plik EXE w trybie debugowania z logami"
	@echo "make icons           - Generuje ikony aplikacji"
	@echo "make docs            - Uruchamia serwer dokumentacji"
	@echo "make docs-build      - Buduje dokumentacje"
	@echo "make setup           - Ustawia PYTHONPATH dla biezacej sesji"

# Instalacja podstawowych zaleznosci
install:
	@echo Instalowanie podstawowych zaleznosci...
	$(PIP) install -e .
	@echo Instalacja podstawowych zaleznosci zakonczona!

# Instalacja zaleznosci deweloperskich
install-dev: install
	@echo Instalowanie zaleznosci deweloperskich...
	$(PIP) install -e ".[dev]"
	$(PIP) install watchdog
	$(PNPM) install
	@echo Instalacja zaleznosci deweloperskich zakonczona!

# Instalacja zaleznosci do budowania
install-build: install
	@echo Instalowanie zaleznosci do budowania...
	$(PIP) install -e ".[build]"
	@echo Instalacja zaleznosci do budowania zakonczona!

# Instalacja wszystkich zaleznosci (legacy)
install-all: install install-dev install-build
	@echo Wszystkie zaleznosci zainstalowane!

# Aktualizacja zaleznosci Python
update-deps:
	@echo Aktualizowanie zaleznosci Python...
	$(PIP) install --upgrade -e .
	$(PIP) install --upgrade -e ".[dev]"
	$(PIP) install --upgrade -e ".[build]"
	$(PIP) install --upgrade watchdog
	@echo Zaleznosci Python zaktualizowane!

# Uruchomienie aplikacji w trybie deweloperskim
dev: 
	@echo Uruchamianie aplikacji w trybie deweloperskim...
	$(PYTHON) src/main.py --debug

# Uruchomienie aplikacji z hot reloadingiem
dev-hot: 
	@echo Uruchamianie aplikacji z hot reloadingiem...
	$(PYTHON) src/main.py --hot-reload --debug

# Uruchomienie aplikacji z hot reloadingiem i tylko logami hot reload
dev-hot-logs: 
	@echo Uruchamianie aplikacji z hot reloadingiem i tylko logami hot reload...
	$(PYTHON) src/main.py --hot-reload --hot-reload-level

# Uruchomienie aplikacji
run: 
	@echo Uruchamianie aplikacji...
	$(PYTHON) src/main.py

# Uruchomienie testow
test: 
	@echo Uruchamianie testow...
	$(PYTEST) tests/

# Uruchomienie testow z pokryciem kodu
test-cov: 
	@echo Uruchamianie testow z pokryciem kodu...
	$(PYTEST) --cov=src tests/

# Budowanie aplikacji jako plik EXE
build: 
	@echo Budowanie aplikacji jako plik EXE...
	$(PYTHON) -m src.tools.build_exe --clean --onefile

# Budowanie aplikacji jako plik EXE w trybie debugowania
build-debug:
	@echo Budowanie aplikacji jako plik EXE w trybie debugowania z logami...
	$(PYTHON) -m src.tools.build_exe --clean --onefile --console --debug

# Generowanie ikon aplikacji
icons: 
	@echo Generowanie ikon aplikacji...
	$(PYTHON) -m src.tools.create_icon

# Uruchomienie serwera dokumentacji
docs:
	@echo Uruchamianie serwera dokumentacji...
	$(PNPM) run docs:dev

# Budowanie dokumentacji
docs-build:
	@echo Budowanie dokumentacji...
	$(PNPM) run docs:build

# Ustawienie PYTHONPATH
setup:
	@echo Ustawianie PYTHONPATH...
	@cmd /c "set PYTHONPATH=%PYTHONPATH%;P:\trass-recomendation"
	@echo PYTHONPATH ustawiony! 