# Uruchamianie aplikacji

Ta strona zawiera instrukcje dotyczące uruchamiania aplikacji Trass Recommendation.

## Przygotowanie środowiska

Przed uruchomieniem aplikacji upewnij się, że:

1. Zainstalowałeś wszystkie wymagane zależności (patrz: [Instalacja](/installation))
2. Aktywowałeś środowisko wirtualne Python
3. Masz odpowiednią wersję Node.js (20+) i pnpm (9.12.3+)

## Aktywacja środowiska wirtualnego

### Windows:

```bash
.\venv\Scripts\activate
```

### Linux/MacOS:

```bash
source venv/bin/activate
```

## Uruchomienie aplikacji

Po aktywacji środowiska wirtualnego, możesz uruchomić aplikację za pomocą polecenia:

```bash
python src/main.py
```

## Uruchamianie w trybie deweloperskim

Jeśli chcesz uruchomić aplikację w trybie deweloperskim z dodatkowymi narzędziami do debugowania, użyj:

```bash
python src/main.py --debug
```

## Uruchamianie z określonymi parametrami

Aplikacja obsługuje różne parametry wejściowe:

```bash
python src/main.py --config config.json --data-dir ./data
```

Dostępne opcje:
- `--config` - ścieżka do pliku konfiguracyjnego
- `--data-dir` - ścieżka do katalogu z danymi
- `--debug` - włączenie trybu debugowania
- `--help` - wyświetlenie dostępnych opcji

## Uruchamianie dokumentacji VitePress

Aby uruchomić lokalnie dokumentację VitePress z TypeScript, wykonaj:

```bash
pnpm docs:dev
```

Dokumentacja będzie dostępna pod adresem `http://localhost:5173`.

### Budowanie dokumentacji do wdrożenia

Aby zbudować statyczną wersję dokumentacji gotową do wdrożenia:

```bash
pnpm docs:build
```

Wygenerowane pliki będą dostępne w katalogu `docs/.vitepress/dist`.

### Podgląd zbudowanej dokumentacji

Aby zobaczyć podgląd zbudowanej dokumentacji przed wdrożeniem:

```bash
pnpm docs:preview
```

## Typowe problemy

### Problem z importami

Jeśli napotkasz błąd `ModuleNotFoundError: No module named 'src'`, upewnij się, że:

1. Pakiet został zainstalowany w trybie edycyjnym:
```bash
pip install -e .
```

2. Środowisko wirtualne jest aktywne

3. Znajdujesz się w głównym katalogu projektu podczas uruchamiania aplikacji

### Problem z biblioteką PyQt

Jeśli wystąpi błąd związany z PyQt, upewnij się, że masz zainstalowaną właściwą wersję:

```bash
pip install PyQt6==6.6.1
```

### Problem z VitePress i TypeScript

Jeśli napotkasz błędy podczas uruchamiania dokumentacji VitePress:

1. Upewnij się, że masz zainstalowane wszystkie zależności:
```bash
pnpm install
```

2. Sprawdź, czy używasz odpowiednich wersji Node.js i pnpm:
```bash
node -v  # Powinno być 20.0.0 lub nowsze
pnpm -v  # Powinno być 9.12.3 lub nowsze
```

3. Jeśli występują błędy TypeScript, możesz wyczyścić pamięć podręczną:
```bash
pnpm cache clean
rm -rf node_modules
pnpm install
```

### Problem z prawami dostępu

W przypadku błędów związanych z prawami dostępu, upewnij się, że:

1. Na systemach Unix-like, pliki wykonywalne mają odpowiednie uprawnienia:
```bash
chmod +x src/main.py
```

2. Posiadasz odpowiednie uprawnienia do katalogów z danymi

## Następne kroki

Po pomyślnym uruchomieniu aplikacji możesz:
- Przejść do korzystania z aplikacji
- Rozpocząć [testowanie](/testing)
- Rozwijać nowe funkcje 