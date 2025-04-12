# Testy

Ta strona zawiera informacje na temat testowania aplikacji Trass Recommendation.

## Przegląd testów

Projekt wykorzystuje framework pytest do testowania różnych aspektów aplikacji. W naszym projekcie mamy następujące kategorie testów:

- **Testy danych tras** - weryfikują operacje na danych dotyczących szlaków turystycznych
- **Testy danych pogodowych** - sprawdzają poprawność przetwarzania i filtrowania danych pogodowych
- **Testy filtrowania danych pogodowych** - specjalizowane testy dla algorytmów filtrowania w oparciu o preferencje

Testy zostały zorganizowane w następujących plikach:
- `tests/test_trail_data.py` - testy dla modułu obsługującego dane tras
- `tests/test_weather_data.py` - testy dla modułu obsługującego dane pogodowe
- `tests/test_weather_filter.py` - testy filtrowania danych pogodowych według preferencji

## Instalacja zależności testowych

Przed uruchomieniem testów, upewnij się, że zainstalowałeś wszystkie wymagane zależności deweloperskie:

```bash
pip install -e ".[dev]"
```

Ten polecenie zainstaluje:
- pytest - framework do testowania
- pytest-cov - narzędzie do analizy pokrycia kodu testami
- inne niezbędne narzędzia testowe

## Uruchamianie testów

### Uruchamianie wszystkich testów

Aby uruchomić wszystkie testy, użyj polecenia:

```bash
pytest
```

### Uruchamianie określonych testów

Możesz uruchomić tylko określone testy, podając ścieżkę do modułu, klasy lub funkcji testowej:

```bash
# Uruchomienie testów z określonego modułu
pytest tests/test_trail_data.py

# Uruchomienie konkretnej klasy testowej
pytest tests/test_trail_data.py::TestTrailData

# Uruchomienie określonej funkcji testowej
pytest tests/test_trail_data.py::TestTrailData::test_filter_by_region
```

## Analiza pokrycia kodu

Aby sprawdzić, jaka część kodu jest pokryta testami, użyj opcji `--cov`:

```bash
# Podstawowa analiza pokrycia
pytest --cov=src

# Bardziej szczegółowa analiza z raportem HTML
pytest --cov=src --cov-report=html
```

Po uruchomieniu drugiego polecenia, raport HTML zostanie wygenerowany w katalogu `htmlcov`. Możesz otworzyć plik `index.html` w przeglądarce, aby zobaczyć szczegółowy raport.

## Fixtures

W projekcie wykorzystywane są następujące fixtures:

### Fixtures ogólne (conftest.py)

- `ensure_test_data_dir` - tworzy katalog na dane testowe, jeśli nie istnieje
- `temp_file` - tworzy tymczasowy plik do testów i usuwa go po zakończeniu
- `sample_date` - dostarcza przykładową datę do testów

### Fixtures dla danych tras (test_trail_data.py)

- `sample_trails` - dostarcza przykładowe obiekty TrailRecord do testów
- `sample_csv_file` - tworzy tymczasowy plik CSV z danymi tras
- `sample_json_file` - tworzy tymczasowy plik JSON z danymi tras
- `trail_data` - dostarcza instancję klasy TrailData

### Fixtures dla danych pogodowych (test_weather_data.py)

- `sample_records` - dostarcza przykładowe obiekty WeatherRecord
- `weather_data` - dostarcza instancję klasy WeatherData z załadowanymi przykładowymi danymi
- `temp_csv_file` - tworzy tymczasowy plik CSV z danymi pogodowymi
- `temp_json_file` - tworzy tymczasowy plik JSON z danymi pogodowymi

## Przykłady testów

### Test wczytywania danych tras z pliku CSV

```python
def test_load_from_csv(trail_data, sample_csv_file, sample_trails):
    """Test wczytywania danych z pliku CSV."""
    trail_data.load_from_csv(sample_csv_file)
    
    # Sprawdzenie liczby wczytanych tras
    assert len(trail_data.trails) == 3
    
    # Sprawdzenie poprawności wczytanych danych
    trail = trail_data.trails[0]
    assert trail.id == "T001"
    assert trail.name == "Dolina Kościeliska"
    assert trail.region == "TATRY"
    assert trail.length_km == 7.8
    assert trail.elevation_gain == 320.0
    assert trail.difficulty == 2
    assert trail.terrain_type == "szlak pieszy"
    assert trail.tags == ["dolina", "łatwa", "rodzinna"]
```

### Test filtrowania danych pogodowych według preferencji

```python
def test_combined_filters(weather_data):
    """Test kombinacji wszystkich filtrów preferencji."""
    # Filtrowanie
    min_temp = 15.0
    max_precip = 10.0
    min_sunshine = 8.0
    filtered = filter_by_preferences(
        weather_data.records,
        min_temp=min_temp,
        max_precip=max_precip,
        min_sunshine=min_sunshine
    )
    
    # Sprawdzenie
    expected_count = 0
    for record in weather_data.records:
        if (record.min_temp >= min_temp and 
            record.precipitation <= max_precip and 
            record.sunshine_hours >= min_sunshine):
            expected_count += 1
            
    assert len(filtered) == expected_count
    for record in filtered:
        assert record.min_temp >= min_temp
        assert record.precipitation <= max_precip
        assert record.sunshine_hours >= min_sunshine
```