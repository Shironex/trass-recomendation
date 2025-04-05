"""
Testy dla modułu weather_data.
"""

import os
import json
import csv
from datetime import date
import tempfile
import pytest
from src.core.weather_data import WeatherData, WeatherRecord


@pytest.fixture
def sample_records():
    """Zwraca przykładowe rekordy pogodowe do testów."""
    return [
        WeatherRecord(
            date=date(2023, 7, 15),
            location_id="TATRY",
            avg_temp=22.5,
            min_temp=15.2,
            max_temp=28.7,
            precipitation=0.0,
            sunshine_hours=12.5,
            cloud_cover=10
        ),
        WeatherRecord(
            date=date(2023, 7, 16),
            location_id="TATRY",
            avg_temp=24.8,
            min_temp=17.3,
            max_temp=30.2,
            precipitation=5.2,
            sunshine_hours=8.0,
            cloud_cover=30
        ),
        WeatherRecord(
            date=date(2023, 7, 15),
            location_id="BESKIDY",
            avg_temp=20.1,
            min_temp=12.5,
            max_temp=26.3,
            precipitation=2.8,
            sunshine_hours=10.0,
            cloud_cover=20
        ),
    ]

@pytest.fixture
def weather_data(sample_records):
    """Zwraca obiekt WeatherData z przykładowymi rekordami."""
    weather_data = WeatherData()
    weather_data.records = sample_records.copy()
    weather_data.filtered_records = sample_records.copy()
    return weather_data

@pytest.fixture
def temp_csv_file(sample_records):
    """Tworzy tymczasowy plik CSV z przykładowymi danymi pogodowymi."""
    temp_csv = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    with open(temp_csv.name, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'date', 'location_id', 'avg_temp', 'min_temp', 'max_temp',
            'precipitation', 'sunshine_hours', 'cloud_cover'
        ])
        writer.writeheader()
        for record in sample_records:
            writer.writerow({
                'date': record.date.strftime('%Y-%m-%d'),
                'location_id': record.location_id,
                'avg_temp': record.avg_temp,
                'min_temp': record.min_temp,
                'max_temp': record.max_temp,
                'precipitation': record.precipitation,
                'sunshine_hours': record.sunshine_hours,
                'cloud_cover': record.cloud_cover
            })
    
    yield temp_csv.name
    
    # Zamknij i usuń plik po teście
    try:
        os.unlink(temp_csv.name)
    except:
        pass

@pytest.fixture
def temp_json_file(sample_records):
    """Tworzy tymczasowy plik JSON z przykładowymi danymi pogodowymi."""
    temp_json = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
    with open(temp_json.name, 'w', encoding='utf-8') as file:
        json.dump({
            'weather_records': [
                {
                    'date': record.date.strftime('%Y-%m-%d'),
                    'location_id': record.location_id,
                    'avg_temp': record.avg_temp,
                    'min_temp': record.min_temp,
                    'max_temp': record.max_temp,
                    'precipitation': record.precipitation,
                    'sunshine_hours': record.sunshine_hours,
                    'cloud_cover': record.cloud_cover
                }
                for record in sample_records
            ]
        }, file, indent=2)
    
    yield temp_json.name
    
    # Zamknij i usuń plik po teście
    try:
        os.unlink(temp_json.name)
    except:
        pass


def test_load_from_csv(temp_csv_file):
    """Test wczytywania danych z pliku CSV."""
    weather_data = WeatherData()
    weather_data.load_from_csv(temp_csv_file)
    
    # Sprawdzenie liczby wczytanych rekordów
    assert len(weather_data.records) == 3
    
    # Sprawdzenie poprawności wczytanych danych
    record = weather_data.records[0]
    assert record.date == date(2023, 7, 15)
    assert record.location_id == "TATRY"
    assert record.avg_temp == 22.5
    assert record.precipitation == 0.0


def test_load_from_json(temp_json_file):
    """Test wczytywania danych z pliku JSON."""
    weather_data = WeatherData()
    weather_data.load_from_json(temp_json_file)
    
    # Sprawdzenie liczby wczytanych rekordów
    assert len(weather_data.records) == 3
    
    # Sprawdzenie poprawności wczytanych danych
    record = weather_data.records[0]
    assert record.date == date(2023, 7, 15)
    assert record.location_id == "TATRY"
    assert record.avg_temp == 22.5
    assert record.precipitation == 0.0


def test_filter_by_location(weather_data):
    """Test filtrowania danych według lokalizacji."""
    # Filtrowanie
    filtered = weather_data.filter_by_location("TATRY")
    
    # Sprawdzenie liczby przefiltrowanych rekordów
    assert len(filtered) == 2
    assert len(weather_data.filtered_records) == 2
    
    # Sprawdzenie czy wszystkie rekordy są z właściwej lokalizacji
    for record in filtered:
        assert record.location_id == "TATRY"


def test_filter_by_date_range(weather_data):
    """Test filtrowania danych według zakresu dat."""
    # Filtrowanie
    start_date = date(2023, 7, 16)
    end_date = date(2023, 7, 16)
    filtered = weather_data.filter_by_date_range(start_date, end_date)
    
    # Sprawdzenie liczby przefiltrowanych rekordów
    assert len(filtered) == 1
    assert len(weather_data.filtered_records) == 1
    
    # Sprawdzenie czy wszystkie rekordy są z właściwego zakresu dat
    for record in filtered:
        assert start_date <= record.date <= end_date


def test_filter_records(weather_data):
    """Test filtrowania rekordów z różnymi parametrami."""
    # Filtrowanie według lokalizacji
    filtered = weather_data.filter_records(location="BESKIDY")
    assert len(filtered) == 1
    assert filtered[0].location_id == "BESKIDY"
    
    # Resetowanie danych przed kolejnym testem
    weather_data.records = weather_data.records.copy()
    weather_data.filtered_records = weather_data.records.copy()
    
    # Filtrowanie według zakresu dat
    date_range = (date(2023, 7, 16), date(2023, 7, 16))
    filtered = weather_data.filter_records(date_range=date_range)
    assert len(filtered) == 1
    assert filtered[0].date == date(2023, 7, 16)
    
    # Resetowanie danych przed kolejnym testem
    weather_data.records = weather_data.records.copy()
    weather_data.filtered_records = weather_data.records.copy()
    
    # Filtrowanie według lokalizacji i zakresu dat
    filtered = weather_data.filter_records(
        location="TATRY", 
        date_range=(date(2023, 7, 15), date(2023, 7, 15))
    )
    assert len(filtered) == 1
    assert filtered[0].location_id == "TATRY"
    assert filtered[0].date == date(2023, 7, 15)


def test_calculate_statistics(weather_data, sample_records):
    """Test obliczania statystyk pogodowych."""
    # Obliczenie statystyk dla wszystkich danych
    stats = weather_data.calculate_statistics()
    
    # Sprawdzenie poprawności obliczonych statystyk
    expected_avg_temp = (22.5 + 24.8 + 20.1) / 3
    expected_total_precip = 0.0 + 5.2 + 2.8
    
    assert pytest.approx(stats['avg_temperature']) == expected_avg_temp
    assert pytest.approx(stats['total_precipitation']) == expected_total_precip
    
    # Obliczenie statystyk dla wybranej lokalizacji
    stats = weather_data.calculate_statistics(location_id="TATRY")
    
    # Sprawdzenie poprawności obliczonych statystyk
    expected_avg_temp = (22.5 + 24.8) / 2
    expected_total_precip = 0.0 + 5.2
    
    assert pytest.approx(stats['avg_temperature']) == expected_avg_temp
    assert pytest.approx(stats['total_precipitation']) == expected_total_precip


def test_save_to_csv(weather_data, temp_file, sample_records):
    """Test zapisywania danych do pliku CSV."""
    # Zapisanie danych
    weather_data.save_to_csv(temp_file)
    
    # Wczytanie danych z zapisanego pliku
    test_data = WeatherData()
    test_data.load_from_csv(temp_file)
    
    # Sprawdzenie liczby rekordów
    assert len(test_data.records) == 3
    
    # Sprawdzenie poprawności danych
    for i, record in enumerate(test_data.records):
        original = sample_records[i]
        assert record.date == original.date
        assert record.location_id == original.location_id
        assert record.avg_temp == original.avg_temp


def test_save_to_json(weather_data, temp_file, sample_records):
    """Test zapisywania danych do pliku JSON."""
    # Zapisanie danych
    weather_data.save_to_json(temp_file)
    
    # Wczytanie danych z zapisanego pliku
    test_data = WeatherData()
    test_data.load_from_json(temp_file)
    
    # Sprawdzenie liczby rekordów
    assert len(test_data.records) == 3
    
    # Sprawdzenie poprawności danych
    for i, record in enumerate(test_data.records):
        original = sample_records[i]
        assert record.date == original.date
        assert record.location_id == original.location_id
        assert record.avg_temp == original.avg_temp 