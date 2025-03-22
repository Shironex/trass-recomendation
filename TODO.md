# Plan implementacji Rekomendatora tras turystycznych

## 1. Struktura projektu
- [x] Utworzenie podstawowej struktury katalogów:
  - `data/` - katalog na pliki z danymi
  - `src/` - katalog na kod źródłowy
  - `tests/` - katalog na testy
  - `docs/` - katalog na dokumentację
- [ ] Utworzenie pliku `requirements.txt` z zależnościami
- [ ] Utworzenie pliku README.md z opisem projektu

## 2. Implementacja modułów (Etap 1)

### 2.1 Moduł obsługi danych o trasach (`src/trail_data.py`)
- [ ] Implementacja klasy `TrailData`
- [ ] Funkcje do wczytywania danych z plików CSV/JSON
- [ ] Implementacja funkcji filtrowania tras:
  - [ ] Po długości
  - [ ] Po trudności
  - [ ] Po regionie
- [ ] Implementacja funkcji do zapisywania przetworzonych danych

### 2.2 Moduł obsługi danych pogodowych (`src/weather_data.py`)
- [ ] Implementacja klasy `WeatherData`
- [ ] Funkcje do wczytywania danych pogodowych z plików CSV/JSON
- [ ] Implementacja funkcji obliczających statystyki:
  - [ ] Średnia temperatura
  - [ ] Suma opadów
  - [ ] Liczba dni słonecznych
- [ ] Implementacja funkcji do zapisywania przetworzonych danych

### 2.3 Moduł przetwarzania danych (`src/data_processor.py`)
- [ ] Implementacja funkcji wykorzystujących programowanie funkcyjne:
  - [ ] Użycie `map()` do transformacji danych
  - [ ] Użycie `filter()` do filtrowania danych
  - [ ] Użycie `reduce()` do agregacji danych
- [ ] Implementacja wyrażeń listowych i słownikowych
- [ ] Implementacja funkcji lambda do operacji na danych

### 2.4 Moduł interfejsu użytkownika (`src/ui.py`)
- [x] Implementacja prostego interfejsu konsolowego
- [x] Funkcje do wyświetlania menu
- [ ] Funkcje do pobierania danych od użytkownika

## 3. Testy
- [ ] Utworzenie testów jednostkowych dla każdego modułu
- [ ] Implementacja testów integracyjnych
- [ ] Utworzenie przykładowych danych testowych

## 4. Dokumentacja
- [ ] Dokumentacja kodu (docstringi)
- [ ] Instrukcja instalacji i uruchomienia

## 5. Dane przykładowe
- [ ] Przygotowanie przykładowych plików CSV z danymi o trasach
- [ ] Przygotowanie przykładowych plików CSV z danymi pogodowymi
- [ ] Utworzenie dokumentacji formatu danych