"""
Testy dla modułu api_client.py odpowiedzialnego za komunikację z zewnętrznymi API pogodowymi.
"""

import pytest
import json
import os
from datetime import date
from unittest.mock import patch, MagicMock
from src.core.api_client import ApiClient
from src.core.weather_data import WeatherRecord
import requests

# Przykładowa odpowiedź z API
VISUALCROSSING_RESPONSE = {
    "resolvedAddress": "Test City",
    "days": [
        {
            "datetime": "2021-03-31",
            "temp": 20.0,
            "tempmin": 15.0,
            "tempmax": 25.0,
            "precip": 1.5,
            "cloudcover": 50,
            "conditions": "Partly Cloudy"
        }
    ]
}

@pytest.fixture
def api_client():
    """Fixture tworzący obiekt ApiClient do testów."""
    return ApiClient(
        api_keys={
            "visualcrossing": "test_key"
        },
        cache_dir="test_cache"
    )

@pytest.fixture(autouse=True)
def cleanup_cache():
    """Fixture czyszczący katalog cache po każdym teście."""
    yield
    if os.path.exists("test_cache"):
        for file in os.listdir("test_cache"):
            os.remove(os.path.join("test_cache", file))
        os.rmdir("test_cache")

def test_init():
    """Test inicjalizacji klienta API."""
    client = ApiClient()
    assert client.api_keys == {}
    assert client.cache_dir is None

    client = ApiClient(api_keys={"visualcrossing": "key"}, cache_dir="test_dir")
    assert client.api_keys == {"visualcrossing": "key"}
    assert client.cache_dir == "test_dir"

def test_set_api_key():
    """Test ustawiania klucza API."""
    client = ApiClient()
    client.set_api_key("visualcrossing", "test_key")
    assert client.api_keys["visualcrossing"] == "test_key"

def test_get_weather_forecast_invalid_service(api_client):
    """Test obsługi nieprawidłowego serwisu w get_weather_forecast."""
    with pytest.raises(ValueError, match="Nieobsługiwany serwis pogodowy: invalid_service"):
        api_client.get_weather_forecast("invalid_service", "Test City")

def test_get_weather_forecast_missing_api_key():
    """Test obsługi błędu dla brakującego klucza API."""
    client = ApiClient()
    with pytest.raises(ValueError, match="Brak klucza API dla serwisu"):
        client.get_weather_forecast("visualcrossing", "Test City")

@patch('requests.get')
def test_get_visualcrossing_forecast(mock_get, api_client):
    """Test pobierania prognozy z Visual Crossing."""
    mock_response = MagicMock()
    mock_response.json.return_value = VISUALCROSSING_RESPONSE
    mock_get.return_value = mock_response

    forecast = api_client.get_weather_forecast("visualcrossing", "Test City")
    assert isinstance(forecast, list)
    assert all(isinstance(record, WeatherRecord) for record in forecast)
    assert len(forecast) == 1
    
    record = forecast[0]
    assert record.location_id == "Test City"
    assert record.avg_temp == 20.0
    assert record.min_temp == 15.0
    assert record.max_temp == 25.0
    assert record.precipitation == 1.5
    assert record.cloud_cover == 50

@patch('requests.get')
def test_get_visualcrossing_forecast_with_dates(mock_get, api_client):
    """Test pobierania prognozy z Visual Crossing z określonym zakresem dat."""
    mock_response = MagicMock()
    mock_response.json.return_value = VISUALCROSSING_RESPONSE
    mock_get.return_value = mock_response

    forecast = api_client.get_weather_forecast(
        "visualcrossing", 
        "Test City",
        start_date="2021-03-31",
        end_date="2021-04-01"
    )
    
    assert isinstance(forecast, list)
    assert all(isinstance(record, WeatherRecord) for record in forecast)
    
    # Sprawdź, czy URL zawiera daty
    called_url = mock_get.call_args[0][0]
    assert "2021-03-31/2021-04-01" in called_url

@patch('requests.get')
def test_api_error_handling(mock_get, api_client):
    """Test obsługi błędów API."""
    mock_get.side_effect = Exception("API Error")

    with pytest.raises(ConnectionError):
        api_client.get_weather_forecast("visualcrossing", "Test City")

def test_cache_operations(api_client):
    """Test operacji na cache."""
    test_data = {"test": "data"}
    
    # Test zapisywania do cache
    api_client.save_api_response_to_cache("visualcrossing", "test_query", test_data)
    
    # Test odczytu z cache
    cached_data = api_client.load_api_response_from_cache("visualcrossing", "test_query")
    assert cached_data == test_data

@patch('requests.get')
def test_cache_usage(mock_get, api_client, tmp_path):
    """Test wykorzystania cache przy pobieraniu prognozy."""
    # Konfiguracja cache
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    api_client.cache_dir = str(cache_dir)

    # Pierwsze żądanie - dane pobierane z API
    mock_response = MagicMock()
    mock_response.json.return_value = VISUALCROSSING_RESPONSE
    mock_get.return_value = mock_response

    forecast1 = api_client.get_weather_forecast("visualcrossing", "Test City")
    assert mock_get.call_count == 1

    # Drugie żądanie - dane powinny być pobrane z cache
    forecast2 = api_client.get_weather_forecast("visualcrossing", "Test City")
    assert mock_get.call_count == 1  # Liczba wywołań API nie powinna się zmienić

    assert forecast1 == forecast2

def test_parse_visualcrossing_data(api_client):
    """Test parsowania danych z Visual Crossing."""
    records = api_client._parse_weather_data("visualcrossing", VISUALCROSSING_RESPONSE)
    assert isinstance(records, list)
    assert all(isinstance(record, WeatherRecord) for record in records)
    if records:
        assert records[0].location_id == "Test City"
        assert records[0].avg_temp == 20.0
        assert records[0].min_temp == 15.0
        assert records[0].max_temp == 25.0
        assert records[0].precipitation == 1.5
        assert records[0].cloud_cover == 50

def test_test_weather_api(api_client):
    """Test funkcji testującej połączenie z API."""
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        assert api_client.test_weather_api("visualcrossing") is True

        # Test dla nieprawidłowego serwisu
        assert api_client.test_weather_api("invalid_service") is False

        # Test dla braku klucza API
        client = ApiClient()
        assert client.test_weather_api("visualcrossing") is False

def test_invalid_date_format(api_client):
    """Test obsługi nieprawidłowego formatu daty."""
    with pytest.raises(ValueError, match="Nieprawidłowy format daty"):
        api_client.get_weather_forecast(
            "visualcrossing",
            "Test City",
            start_date="31-03-2021"  # Nieprawidłowy format
        )

def test_invalid_days_range(api_client):
    """Test obsługi nieprawidłowej liczby dni."""
    with pytest.raises(ValueError, match="Liczba dni musi być z zakresu 1-15"):
        api_client.get_weather_forecast(
            "visualcrossing",
            "Test City",
            days=16  # Zbyt duża liczba dni
        ) 