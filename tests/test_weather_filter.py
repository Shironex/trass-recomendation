"""
Testy filtrowania danych pogodowych.
"""

import pytest
from datetime import date
from src.core.weather_data import WeatherData, WeatherRecord


@pytest.fixture
def weather_data():
    """Przygotowanie obiektu WeatherData z przykładowymi danymi."""
    weather_data = WeatherData()
    
    # Przygotowanie danych testowych z różnymi wartościami temperatur, opadów i nasłonecznienia
    sample_records = [
        # Różne temperatury
        WeatherRecord(
            date=date(2023, 7, 10),
            location_id="TATRY",
            avg_temp=20.0,
            min_temp=10.0,  # Zimny poranek
            max_temp=30.0,
            precipitation=0.0,
            sunshine_hours=10.0,
            cloud_cover=10
        ),
        WeatherRecord(
            date=date(2023, 7, 11),
            location_id="TATRY",
            avg_temp=25.0,
            min_temp=18.0,  # Cieplejszy poranek
            max_temp=32.0,
            precipitation=0.0,
            sunshine_hours=12.0,
            cloud_cover=5
        ),
        # Różne opady
        WeatherRecord(
            date=date(2023, 7, 12),
            location_id="BESKIDY",
            avg_temp=22.0,
            min_temp=15.0,
            max_temp=28.0,
            precipitation=15.0,  # Duże opady
            sunshine_hours=4.0,
            cloud_cover=80
        ),
        WeatherRecord(
            date=date(2023, 7, 13),
            location_id="BESKIDY",
            avg_temp=23.0,
            min_temp=16.0,
            max_temp=29.0,
            precipitation=5.0,  # Małe opady
            sunshine_hours=8.0,
            cloud_cover=40
        ),
        # Różne nasłonecznienie
        WeatherRecord(
            date=date(2023, 7, 14),
            location_id="SUDETY",
            avg_temp=21.0,
            min_temp=14.0,
            max_temp=27.0,
            precipitation=2.0,
            sunshine_hours=3.0,  # Mało słońca
            cloud_cover=70
        ),
        WeatherRecord(
            date=date(2023, 7, 15),
            location_id="SUDETY",
            avg_temp=24.0,
            min_temp=17.0,
            max_temp=30.0,
            precipitation=0.0,
            sunshine_hours=13.0,  # Dużo słońca
            cloud_cover=10
        ),
    ]
    
    # Ustawienie danych testowych w obiekcie
    weather_data.records = sample_records.copy()
    weather_data.filtered_records = sample_records.copy()
    
    return weather_data


def filter_by_preferences(records, min_temp=0.0, max_precip=float('inf'), min_sunshine=0.0):
    """
    Funkcja pomocnicza symulująca działanie metody _filter_by_preferences z klasy WeatherPage.
    """
    filtered = []
    for record in records:
        if (record.min_temp >= min_temp and
            record.precipitation <= max_precip and
            record.sunshine_hours >= min_sunshine):
            filtered.append(record)
    return filtered


def test_temperature_filter(weather_data):
    """Test filtrowania według minimalnej temperatury."""
    # Filtrowanie
    min_temp = 15.0
    filtered = filter_by_preferences(weather_data.records, min_temp=min_temp)
    
    # Sprawdzenie
    assert len(filtered) == 4  # Powinny zostać rekordy z min_temp >= 15.0
    for record in filtered:
        assert record.min_temp >= min_temp


def test_precipitation_filter(weather_data):
    """Test filtrowania według maksymalnych opadów."""
    # Filtrowanie
    max_precip = 10.0
    filtered = filter_by_preferences(weather_data.records, max_precip=max_precip)
    
    # Sprawdzenie
    assert len(filtered) == 5  # Powinny zostać rekordy z precipitation <= 10.0
    for record in filtered:
        assert record.precipitation <= max_precip


def test_sunshine_filter(weather_data):
    """Test filtrowania według minimalnego nasłonecznienia."""
    # Filtrowanie
    min_sunshine = 8.0
    filtered = filter_by_preferences(weather_data.records, min_sunshine=min_sunshine)
    
    # Sprawdzenie
    assert len(filtered) == 4  # Powinny zostać rekordy z sunshine_hours >= 8.0
    for record in filtered:
        assert record.sunshine_hours >= min_sunshine


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
            
    assert len(filtered) == expected_count  # Liczba rekordów powinna zgadzać się z oczekiwaniami
    for record in filtered:
        assert record.min_temp >= min_temp
        assert record.precipitation <= max_precip
        assert record.sunshine_hours >= min_sunshine


def test_filter_records_with_preferences(weather_data):
    """
    Test symulujący działanie metody _update_statistics z klasy WeatherPage.
    Sprawdza, czy połączenie filtrów podstawowych i preferencji użytkownika działa poprawnie.
    """
    # Najpierw filtruj według podstawowych kryteriów (lokalizacja)
    location_id = "TATRY"
    basic_filtered = weather_data.filter_records(location=location_id)
    
    # Następnie zastosuj preferencje użytkownika
    min_temp = 15.0
    max_precip = 10.0
    min_sunshine = 8.0
    preference_filtered = filter_by_preferences(
        basic_filtered,
        min_temp=min_temp,
        max_precip=max_precip,
        min_sunshine=min_sunshine
    )
    
    # Sprawdzenie
    assert len(preference_filtered) == 1  # Tylko jeden rekord z TATRY spełnia wszystkie kryteria
    record = preference_filtered[0]
    assert record.location_id == "TATRY"
    assert record.min_temp >= min_temp
    assert record.precipitation <= max_precip
    assert record.sunshine_hours >= min_sunshine 