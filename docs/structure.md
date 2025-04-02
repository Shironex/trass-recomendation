# Struktura projektu

Ta strona zawiera szczegółowe informacje na temat organizacji plików i katalogów w projekcie Trass Recommendation.

## Przegląd struktury

Projekt posiada następującą strukturę:

```
trass-recomendation/
├── src/                # Kod źródłowy aplikacji
├── tests/              # Testy aplikacji
├── data/               # Testowe dane do użycia w aplikacji
├── docs/               # Dokumentacja (VitePress)
├── docs/package.json   # Konfiguracja npm/pnpm
├── docs/tsconfig.json  # Konfiguracja TypeScript
├── requirements.txt    # Zależności Python
├── setup.py            # Konfiguracja instalacji
└── venv/               # Środowisko wirtualne (nie jest w repozytorium)
```

## Katalogi główne

### src/

Katalog `src/` zawiera główny kod źródłowy aplikacji. Jest on podzielony na moduły odpowiadające za różne funkcjonalności:

```
src/
├── main.py            # Punkt wejściowy aplikacji
├── core/              # Podstawowe komponenty i funkcjonalności
├── ui/                # Komponenty interfejsu użytkownika
├── utils/             # Narzędzia pomocnicze
├── tools/             # Narzędzia do budowania i dystrybucji
└── __pycache__/       # Skompilowane pliki Python (nie edytować)
```

### tests/

Katalog `tests/` zawiera testy jednostkowe i integracyjne dla aplikacji:

```
tests/
├── test_main.py       # Testy dla głównego modułu
├── test_utils.py      # Testy dla narzędzi pomocniczych 
└── test_core.py       # Testy dla komponentów core
```

### data/

Katalog `data/` przechowuje pliki danych używane przez aplikację:

```
data/
├── trail.csv    # Przykładowe trasy
└── weather.csv  # Przykładowe dane pogody
```

### docs/

Katalog `docs/` zawiera dokumentację projektu w formacie VitePress z TypeScript:

```
docs/
├── .vitepress/           # Konfiguracja VitePress
│   ├── config.ts         # Główna konfiguracja VitePress
│   ├── siteConfig.ts     # Konfiguracja strony (tytuł, opis, linki społecznościowe)
│   ├── theme/            # Customizacje motywu
│   └── tsconfig.json     # Konfiguracja TypeScript dla VitePress
├── public/               # Zasoby statyczne (obrazy, pliki)
├── building-exe.md       # Instrukcje budowania EXE
├── demo.md               # Demonstracja funkcjonalności
├── installation.md       # Instrukcja instalacji
├── index.md              # Strona główna dokumentacji
├── running.md            # Instrukcje uruchamiania
├── structure.md          # Struktura projektu (ten plik)
└── testing.md            # Instrukcje testowania
```

## Pliki konfiguracyjne

### setup.py

Plik `setup.py` definiuje pakiet Python, jego zależności i metadane. Przykład:

```python
from setuptools import setup, find_packages

setup(
    name="trass-recommendation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "PyQt6>=6.6.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
        "build": [
            "pyinstaller>=6.0.0",
            "pillow>=9.0.0",
            "colorama>=0.4.6",
        ],
    },
)
```

### requirements.txt

Plik `requirements.txt` zawiera listę bezpośrednich zależności projektu:

```
PyQt6>=6.6.1
pytest>=7.0.0
pytest-cov>=4.0.0
pyinstaller>=6.0.0
pillow>=9.0.0
colorama>=0.4.6
```

### package.json

Plik `package.json` zawiera konfigurację dla narzędzi JavaScript/TypeScript i skrypty npm/pnpm:

```json
{
  "name": "trass-recomendation",
  "version": "1.0.0",
  "description": "System rekomendacji tras oparty na PyQt6",
  "type": "module",
  "engines": {
    "node": ">=20.0.0",
    "pnpm": ">=9.12.3"
  },
  "scripts": {
    "docs:dev": "vitepress dev docs",
    "docs:build": "vitepress build docs",
    "docs:preview": "vitepress preview docs"
  },
  "devDependencies": {
    "vitepress": "^1.6.3",
    "vue": "^3.4.15",
    "typescript": "^5.3.3",
    "@types/node": "^20.11.5"
  }
}
```

### tsconfig.json

Plik `tsconfig.json` zawiera konfigurację TypeScript dla projektu:

```json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "strict": true,
    "skipLibCheck": true,
    "resolveJsonModule": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["docs/.vitepress/*"]
    }
  },
  "include": [
    "docs/.vitepress/**/*.ts",
    "docs/.vitepress/**/*.d.ts",
    "docs/.vitepress/**/*.vue"
  ],
  "exclude": ["node_modules", "dist"]
}
```

## Następne kroki

Po zapoznaniu się ze strukturą projektu możesz:
- Przejść do [instrukcji uruchamiania](/running)
- Zapoznać się z [testami](/testing)
- Rozpocząć rozwój nowych funkcji 