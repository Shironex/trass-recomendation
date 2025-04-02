# Struktura projektu

Ta strona zawiera szczegółowe informacje na temat organizacji plików i katalogów w projekcie Trass Recommendation.

## Przegląd struktury

Projekt posiada następującą strukturę:

```
trass-recomendation/
├── src/                # Kod źródłowy aplikacji
├── tests/              # Testy aplikacji
├── data/               # Pliki danych
├── docs/               # Dokumentacja (VitePress)
├── requirements.txt    # Zależności Python
├── setup.py            # Konfiguracja instalacji
├── package.json        # Konfiguracja npm/pnpm
├── tsconfig.json       # Konfiguracja TypeScript
├── venv/               # Środowisko wirtualne (nie jest w repozytorium)
└── TODO.md             # Lista zadań do wykonania
```

## Katalogi główne

### src/

Katalog `src/` zawiera główny kod źródłowy aplikacji. Jest on podzielony na moduły odpowiadające za różne funkcjonalności:

```
src/
├── __init__.py        # Inicjalizacja pakietu
├── main.py            # Punkt wejściowy aplikacji
├── models/            # Modele danych
├── views/             # Komponenty interfejsu użytkownika
├── controllers/       # Logika kontrolerów
└── utils/             # Narzędzia pomocnicze
```

### tests/

Katalog `tests/` zawiera testy jednostkowe i integracyjne dla aplikacji:

```
tests/
├── __init__.py
├── test_models/       # Testy dla modeli
├── test_controllers/  # Testy dla kontrolerów
└── test_utils/        # Testy dla narzędzi
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
├── .vitepress/        # Konfiguracja VitePress
│   ├── config.ts      # Konfiguracja w TypeScript
│   ├── tsconfig.json  # Konfiguracja TypeScript dla VitePress
│   └── theme/         # Customizacje motywu
├── guide/             # Przewodnik użytkownika
├── index.md           # Strona główna dokumentacji
└── ...                # Inne strony dokumentacji
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
        ]
    },
)
```

### requirements.txt

Plik `requirements.txt` zawiera listę bezpośrednich zależności projektu:

```
PyQt6>=6.6.1
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

## Konwencje nazewnictwa

W projekcie stosujemy następujące konwencje:

- Moduły i pakiety Python: `snake_case`
- Klasy Python: `PascalCase`
- Funkcje i zmienne Python: `snake_case`
- Stałe Python: `UPPER_SNAKE_CASE`
- Pliki TypeScript: `camelCase.ts` lub `PascalCase.ts` dla komponentów
- Interfejsy TypeScript: `IPascalCase`
- Typy TypeScript: `TPascalCase`

## Organizacja kodu

Kod jest zorganizowany zgodnie z wzorcem MVC (Model-View-Controller):

- **Model**: Przechowuje dane i stan aplikacji
- **View**: Odpowiada za interfejs użytkownika i prezentację
- **Controller**: Zawiera logikę biznesową i łączy Model z View

## Następne kroki

Po zapoznaniu się ze strukturą projektu możesz:
- Przejść do [instrukcji uruchamiania](/running)
- Zapoznać się z [testami](/testing)
- Rozpocząć rozwój nowych funkcji 