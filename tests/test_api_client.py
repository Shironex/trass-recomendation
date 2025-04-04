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

# Przykładowe odpowiedzi z API
OPENWEATHERMAP_RESPONSE = {
    "city": {"name": "Test City"},
    "list": [
        {
            "dt": 1617184800,  # 2021-03-31 12:00:00
            "main": {
                "temp": 20.0,
                "temp_min": 15.0,
                "temp_max": 25.0
            },
            "clouds": {"all": 50},
            "rain": {"3h": 1.5} if True else {}
        }
    ]
}

WEATHERAPI_RESPONSE = {
    "location": {"name": "Test City"},
    "forecast": {
        "forecastday": [
            {
                "date": "2021-03-31",
                "day": {
                    "avgtemp_c": 20.0,
                    "mintemp_c": 15.0,
                    "maxtemp_c": 25.0,
                    "totalprecip_mm": 1.5,
                    "avghumidity": 70,
                    "condition": {"text": "Partly cloudy"}
                },
                "astro": {
                    "sunrise": "06:00 AM",
                    "sunset": "06:00 PM"
                }
            }
        ]
    }
}

VISUALCROSSING_RESPONSE = {
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
            "openweathermap": "test_key",
            "weatherapi": "test_key",
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

    client = ApiClient(api_keys={"test": "key"}, cache_dir="test_dir")
    assert client.api_keys == {"test": "key"}
    assert client.cache_dir == "test_dir"

def test_set_api_key():
    """Test ustawiania klucza API."""
    client = ApiClient()
    client.set_api_key("test_service", "test_key")
    assert client.api_keys["test_service"] == "test_key"

def test_get_weather_forecast_invalid_service(api_client):
    """Test obsługi błędu dla nieprawidłowego serwisu."""
    with pytest.raises(ValueError, match="Nieobsługiwany serwis pogodowy"):
        api_client.get_weather_forecast("invalid_service", "Test City")

def test_get_weather_forecast_missing_api_key():
    """Test obsługi błędu dla brakującego klucza API."""
    client = ApiClient()
    with pytest.raises(ValueError, match="Brak klucza API dla serwisu"):
        client.get_weather_forecast("openweathermap", "Test City")

@patch('requests.get')
def test_get_openweathermap_forecast(mock_get, api_client):
    """Test pobierania prognozy z OpenWeatherMap."""
    mock_response = MagicMock()
    mock_response.json.return_value = OPENWEATHERMAP_RESPONSE
    mock_get.return_value = mock_response

    forecast = api_client.get_weather_forecast("openweathermap", "Test City")
    assert isinstance(forecast, list)
    assert all(isinstance(record, WeatherRecord) for record in forecast)

@patch('requests.get')
def test_get_weatherapi_forecast(mock_get, api_client):
    """Test pobierania prognozy z WeatherAPI."""
    mock_response = MagicMock()
    mock_response.json.return_value = WEATHERAPI_RESPONSE
    mock_get.return_value = mock_response

    forecast = api_client.get_weather_forecast("weatherapi", "Test City")
    assert isinstance(forecast, list)
    assert all(isinstance(record, WeatherRecord) for record in forecast)

@patch('requests.get')
def test_get_visualcrossing_forecast(mock_get, api_client):
    """Test pobierania prognozy z Visual Crossing."""
    mock_response = MagicMock()
    mock_response.json.return_value = VISUALCROSSING_RESPONSE
    mock_get.return_value = mock_response

    forecast = api_client.get_weather_forecast("visualcrossing", "Test City")
    assert isinstance(forecast, list)
    assert all(isinstance(record, WeatherRecord) for record in forecast)

@patch('requests.get')
def test_api_error_handling(mock_get, api_client):
    """Test obsługi błędów API."""
    mock_get.side_effect = Exception("API Error")

    with pytest.raises(ConnectionError):
        api_client.get_weather_forecast("openweathermap", "Test City")

def test_cache_operations(api_client):
    """Test operacji na cache."""
    test_data = {"test": "data"}
    
    # Test zapisywania do cache
    api_client.save_api_response_to_cache("test_service", "test_query", test_data)
    
    # Test odczytu z cache
    cached_data = api_client.load_api_response_from_cache("test_service", "test_query")
    assert cached_data == test_data

@patch('requests.get')
def test_cache_usage(mock_get, api_client):
    """Test wykorzystania cache przy pobieraniu prognozy."""
    # Pierwsze żądanie - dane pobierane z API
    mock_response = MagicMock()
    mock_response.json.return_value = OPENWEATHERMAP_RESPONSE
    mock_get.return_value = mock_response

    forecast1 = api_client.get_weather_forecast("openweathermap", "Test City")
    assert mock_get.call_count == 1

    # Drugie żądanie - dane powinny być pobrane z cache
    forecast2 = api_client.get_weather_forecast("openweathermap", "Test City")
    assert mock_get.call_count == 1  # Liczba wywołań API nie powinna się zmienić

    assert forecast1 == forecast2

def test_parse_openweathermap_data(api_client):
    """Test parsowania danych z OpenWeatherMap."""
    records = api_client._parse_weather_data("openweathermap", OPENWEATHERMAP_RESPONSE)
    assert isinstance(records, list)
    assert all(isinstance(record, WeatherRecord) for record in records)
    if records:
        assert records[0].location_id == "Test City"
        assert records[0].avg_temp == 20.0

def test_parse_weatherapi_data(api_client):
    """Test parsowania danych z WeatherAPI."""
    records = api_client._parse_weather_data("weatherapi", WEATHERAPI_RESPONSE)
    assert isinstance(records, list)
    assert all(isinstance(record, WeatherRecord) for record in records)
    if records:
        assert records[0].location_id == "Test City"
        assert records[0].avg_temp == 20.0

def test_parse_visualcrossing_data(api_client):
    """Test parsowania danych z Visual Crossing."""
    records = api_client._parse_weather_data("visualcrossing", VISUALCROSSING_RESPONSE)
    assert isinstance(records, list)
    assert all(isinstance(record, WeatherRecord) for record in records)
    if records:
        assert records[0].avg_temp == 20.0 