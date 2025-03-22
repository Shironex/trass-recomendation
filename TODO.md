# Plan implementacji Rekomendatora tras turystycznych

## 1. Struktura projektu
- [x] Utworzenie podstawowej struktury katalogów:
  - `data/` - katalog na pliki z danymi
  - `src/` - katalog na kod źródłowy
  - `tests/` - katalog na testy
  - `docs/` - katalog na dokumentację
- [x] Utworzenie pliku `requirements.txt` z zależnościami
- [x] Utworzenie pliku README.md z opisem projektu

## 2. Implementacja modułów (Etap 1)

### 2.1 Moduł obsługi danych o trasach (`src/trail_data.py`)
- [x] Implementacja klasy `TrailData`
- [x] Funkcje do wczytywania danych z plików CSV/JSON
- [x] Implementacja funkcji filtrowania tras:
  - [x] Po długości
  - [x] Po trudności
  - [x] Po regionie
- [x] Implementacja funkcji do zapisywania przetworzonych danych

### 2.2 Moduł obsługi danych pogodowych (`src/weather_data.py`)
- [x] Implementacja klasy `WeatherData`
- [x] Funkcje do wczytywania danych pogodowych z plików CSV/JSON
- [x] Implementacja funkcji obliczających statystyki:
  - [x] Średnia temperatura
  - [x] Suma opadów
  - [x] Liczba dni słonecznych
- [x] Implementacja funkcji do zapisywania przetworzonych danych

### 2.3 Moduł przetwarzania danych (`src/data_processor.py`)
- [x] Implementacja funkcji wykorzystujących programowanie funkcyjne:
  - [x] Użycie `map()` do transformacji danych
  - [x] Użycie `filter()` do filtrowania danych
  - [x] Użycie `reduce()` do agregacji danych
- [x] Implementacja wyrażeń listowych i słownikowych
- [x] Implementacja funkcji lambda do operacji na danych

### 2.4 Moduł interfejsu użytkownika (`src/ui.py`)
- [x] Implementacja prostego interfejsu konsolowego
- [x] Funkcje do wyświetlania menu
- [x] Funkcje do pobierania danych od użytkownika

## 3. Testy
- [ ] Utworzenie testów jednostkowych dla każdego modułu
- [ ] Implementacja testów integracyjnych
- [ ] Utworzenie przykładowych danych testowych

## 4. Dokumentacja
- [x] Dokumentacja kodu (docstringi)
- [x] Instrukcja instalacji i uruchomienia

## 5. Dane przykładowe
- [x] Przygotowanie przykładowych plików CSV z danymi o trasach
- [x] Przygotowanie przykładowych plików CSV z danymi pogodowymi
- [x] Utworzenie dokumentacji formatu danych