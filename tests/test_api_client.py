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
    """Test obsługi nieprawidłowego serwisu w get_weather_forecast."""
    with pytest.raises(ValueError, match="Nieobsługiwany serwis pogodowy: invalid_service"):
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
def test_cache_usage(mock_get, api_client, tmp_path):
    """Test wykorzystania cache przy pobieraniu prognozy."""
    # Konfiguracja cache
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    api_client.cache_dir = str(cache_dir)

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

def test_cache_error_handling(api_client):
    """Test obsługi błędów przy operacjach na cache."""
    # Test błędu przy wczytywaniu z cache
    with patch('json.load', side_effect=Exception("Test error")):
        result = api_client.load_api_response_from_cache("test_service", "test_query")
        assert result is None

    # Test błędu przy zapisie do cache
    with patch('builtins.open', side_effect=Exception("Test error")):
        api_client.save_api_response_to_cache("test_service", "test_query", {"test": "data"})
        # Sprawdzamy, że metoda nie rzuca wyjątku

def test_test_weather_api(api_client):
    """Test metody testującej połączenie z API."""
    # Test nieznanego serwisu
    assert not api_client.test_weather_api("unknown_service")

    # Test braku klucza API
    assert not api_client.test_weather_api("weatherapi")

    # Test udanego połączenia z OpenWeatherMap
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        assert api_client.test_weather_api("openweathermap")

    # Test nieudanego połączenia z OpenWeatherMap
    with patch('requests.get', side_effect=Exception("Connection error")):
        assert not api_client.test_weather_api("openweathermap")

    # Test udanego połączenia z innym serwisem
    api_client.set_api_key("weatherapi", "test_key")
    with patch.object(api_client, 'get_weather_forecast', return_value=[WeatherRecord(
        date=date(2021, 1, 1),
        location_id="Warsaw",
        avg_temp=20.0,
        min_temp=15.0,
        max_temp=25.0,
        precipitation=0.0,
        sunshine_hours=12.0,
        cloud_cover=50
    )]):
        assert api_client.test_weather_api("weatherapi")

    # Test nieudanego połączenia z innym serwisem
    with patch.object(api_client, 'get_weather_forecast', side_effect=Exception("API error")):
        assert not api_client.test_weather_api("weatherapi")

def test_get_weather_forecast_cache_error(api_client):
    """Test obsługi błędów przy przetwarzaniu danych z cache."""
    api_client.set_api_key("openweathermap", "test_key")
    
    with patch.object(api_client, 'load_api_response_from_cache', return_value={"invalid": "data"}), \
         patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = OPENWEATHERMAP_RESPONSE
        mock_get.return_value = mock_response
        
        # Dane z cache są nieprawidłowe, ale zapytanie do API powinno się udać
        records = api_client.get_weather_forecast("openweathermap", "Test City")
        assert len(records) > 0

def test_parse_weather_data_error(api_client):
    """Test obsługi błędów przy parsowaniu danych."""
    with pytest.raises(ValueError):
        api_client._parse_weather_data("invalid_service", {})

def test_api_error_handling_detailed(api_client):
    """Test szczegółowej obsługi błędów API."""
    # Test błędu żądania dla OpenWeatherMap
    with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")):
        with pytest.raises(ConnectionError):
            api_client._get_openweathermap_forecast("Test City", 5)

    # Test nieoczekiwanego błędu dla WeatherAPI
    with patch('requests.get', side_effect=Exception("Unexpected error")):
        with pytest.raises(ConnectionError):
            api_client._get_weatherapi_forecast("Test City", 5)

    # Test błędu żądania dla Visual Crossing
    with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")):
        with pytest.raises(ConnectionError):
            api_client._get_visualcrossing_forecast("Test City", 5)

def test_parse_openweathermap_data_error(api_client):
    """Test obsługi błędów przy parsowaniu danych z OpenWeatherMap."""
    with pytest.raises(KeyError):
        api_client._parse_openweathermap_data({})

def test_test_weather_api_detailed(api_client):
    """Test szczegółowej obsługi błędów w test_weather_api."""
    # Test nieznanego serwisu
    assert not api_client.test_weather_api("invalid_service")

    # Test braku klucza API
    assert not api_client.test_weather_api("weatherapi")

    # Test błędu połączenia
    with patch('requests.get', side_effect=Exception("Connection timeout")):
        assert not api_client.test_weather_api("openweathermap")

    # Test błędu w get_weather_forecast
    api_client.set_api_key("weatherapi", "test_key")
    with patch.object(api_client, 'get_weather_forecast', side_effect=Exception("API error")):
        assert not api_client.test_weather_api("weatherapi")

def test_get_weather_forecast_cache_parse_error(api_client):
    """Test obsługi błędów przy parsowaniu danych z cache."""
    api_client.set_api_key("openweathermap", "test_key")
    
    with patch.object(api_client, 'load_api_response_from_cache', return_value={"invalid": "data"}), \
         patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = OPENWEATHERMAP_RESPONSE
        mock_get.return_value = mock_response
        
        # Parsowanie danych z cache nie powiedzie się, ale zapytanie do API powinno się udać
        records = api_client.get_weather_forecast("openweathermap", "Test City")
        assert len(records) > 0

def test_parse_openweathermap_data_empty(api_client):
    """Test parsowania pustych danych z OpenWeatherMap."""
    records = api_client._parse_openweathermap_data({"list": [], "city": {"name": "Test City"}})
    assert len(records) == 0

def test_visualcrossing_error_handling(api_client):
    """Test obsługi błędów przy pobieraniu danych z Visual Crossing."""
    api_client.set_api_key("visualcrossing", "test_key")
    
    # Test błędu żądania
    with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")):
        with pytest.raises(ConnectionError):
            api_client._get_visualcrossing_forecast("Test City", 5)
    
    # Test nieoczekiwanego błędu
    with patch('requests.get', side_effect=Exception("Unexpected error")):
        with pytest.raises(ConnectionError):
            api_client._get_visualcrossing_forecast("Test City", 5)

def test_cache_operations_no_cache_dir(api_client):
    """Test operacji na cache gdy katalog cache jest wyłączony."""
    api_client.cache_dir = None
    
    # Test zapisu do cache
    api_client.save_api_response_to_cache("test_service", "test_query", {"test": "data"})
    
    # Test odczytu z cache
    result = api_client.load_api_response_from_cache("test_service", "test_query")
    assert result is None

def test_test_weather_api_edge_cases(api_client):
    """Test przypadków brzegowych w metodzie test_weather_api."""
    # Test nieznanego serwisu
    assert not api_client.test_weather_api("invalid_service")
    
    # Test braku klucza API
    assert not api_client.test_weather_api("weatherapi")
    
    # Test błędu w OpenWeatherMap
    with patch('requests.get', side_effect=Exception("Connection timeout")):
        assert not api_client.test_weather_api("openweathermap")
    
    # Test błędu w innym serwisie
    api_client.set_api_key("weatherapi", "test_key")
    with patch.object(api_client, 'get_weather_forecast', side_effect=Exception("API error")):
        assert not api_client.test_weather_api("weatherapi")

def test_get_weather_forecast_cache_parse_error_fallback(api_client):
    """Test obsługi błędów przy parsowaniu danych z cache z awaryjnym przejściem na API."""
    api_client.set_api_key("openweathermap", "test_key")
    
    with patch.object(api_client, 'load_api_response_from_cache', return_value={"invalid": "data"}), \
         patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = {"invalid": "data"}  # Nieprawidłowe dane z API
        mock_get.return_value = mock_response
        
        # Zarówno cache jak i API zwracają nieprawidłowe dane
        with pytest.raises(KeyError):
            api_client.get_weather_forecast("openweathermap", "Test City")

def test_parse_openweathermap_data_invalid(api_client):
    """Test parsowania nieprawidłowych danych z OpenWeatherMap."""
    with pytest.raises(KeyError):
        api_client._parse_openweathermap_data({"list": [{"invalid": "data"}]})

def test_test_weather_api_complete(api_client):
    """Test wszystkich ścieżek w metodzie test_weather_api."""
    # Test nieznanego serwisu
    assert not api_client.test_weather_api("invalid_service")
    
    # Test braku klucza API
    assert not api_client.test_weather_api("weatherapi")
    
    # Test błędu w OpenWeatherMap
    with patch('requests.get', side_effect=requests.exceptions.RequestException("Network error")):
        assert not api_client.test_weather_api("openweathermap")
    
    # Test błędu w innym serwisie
    api_client.set_api_key("weatherapi", "test_key")
    with patch.object(api_client, 'get_weather_forecast', side_effect=Exception("API error")):
        assert not api_client.test_weather_api("weatherapi")
    
    # Test udanego połączenia z OpenWeatherMap
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        assert api_client.test_weather_api("openweathermap")
    
    # Test udanego połączenia z innym serwisem
    with patch.object(api_client, 'get_weather_forecast', return_value=[WeatherRecord(
        date=date(2021, 1, 1),
        location_id="Warsaw",
        avg_temp=20.0,
        min_temp=15.0,
        max_temp=25.0,
        precipitation=0.0,
        sunshine_hours=12.0,
        cloud_cover=50
    )]):
        assert api_client.test_weather_api("weatherapi")

def test_parse_weather_data_invalid_service(api_client):
    """Test obsługi nieprawidłowego serwisu w _parse_weather_data."""
    with pytest.raises(ValueError, match="Brak implementacji parsera dla serwisu: invalid_service"):
        api_client._parse_weather_data("invalid_service", {})

def test_load_api_response_from_cache_error(api_client):
    """Test obsługi błędów przy wczytywaniu z cache."""
    with patch('builtins.open', side_effect=Exception("Test error")):
        result = api_client.load_api_response_from_cache("test_service", "test_query")
        assert result is None

def test_test_weather_api_error(api_client):
    """Test obsługi błędów w test_weather_api."""
    api_client.set_api_key("openweathermap", "test_key")
    
    # Test błędu połączenia
    with patch('requests.get', side_effect=Exception("Connection error")):
        assert not api_client.test_weather_api("openweathermap")
    
    # Test błędu w get_weather_forecast
    with patch.object(api_client, 'get_weather_forecast', side_effect=Exception("API error")):
        assert not api_client.test_weather_api("weatherapi")

def test_get_weather_forecast_invalid_service_no_api(api_client):
    """Test obsługi nieprawidłowego serwisu w get_weather_forecast."""
    with pytest.raises(ValueError) as exc_info:
        api_client.get_weather_forecast("invalid_service", "Test City")
    assert str(exc_info.value) == "Nieobsługiwany serwis pogodowy: invalid_service"

def test_parse_weather_data_invalid_service_no_parser(api_client):
    """Test obsługi nieprawidłowego serwisu w _parse_weather_data."""
    with pytest.raises(ValueError) as exc_info:
        api_client._parse_weather_data("invalid_service", {})
    assert str(exc_info.value) == "Brak implementacji parsera dla serwisu: invalid_service"

def test_load_api_response_from_cache_error_handling(api_client):
    """Test obsługi błędów przy wczytywaniu z cache."""
    # Test błędu otwarcia pliku
    with patch('builtins.open', side_effect=Exception("File error")):
        result = api_client.load_api_response_from_cache("test_service", "test_query")
        assert result is None

    # Test błędu wczytywania JSON
    mock_file = MagicMock()
    mock_file.__enter__ = MagicMock(return_value=mock_file)
    mock_file.__exit__ = MagicMock(return_value=None)
    with patch('builtins.open', return_value=mock_file), \
         patch('json.load', side_effect=Exception("JSON error")):
        result = api_client.load_api_response_from_cache("test_service", "test_query")
        assert result is None

def test_test_weather_api_error_handling(api_client):
    """Test obsługi błędów w test_weather_api."""
    api_client.set_api_key("openweathermap", "test_key")
    
    # Test błędu połączenia z OpenWeatherMap
    with patch('requests.get', side_effect=Exception("Connection error")):
        assert not api_client.test_weather_api("openweathermap")
    
    # Test błędu w get_weather_forecast dla innych serwisów
    api_client.set_api_key("weatherapi", "test_key")
    with patch.object(api_client, 'get_weather_forecast', side_effect=Exception("API error")):
        assert not api_client.test_weather_api("weatherapi")

def test_get_weather_forecast_invalid_service_error(api_client):
    """Test sprawdzający obsługę błędu dla nieprawidłowego serwisu w get_weather_forecast."""
    with pytest.raises(ValueError, match="Nieobsługiwany serwis pogodowy: invalid_service"):
        api_client.get_weather_forecast("invalid_service", "Warsaw", 1)

def test_parse_weather_data_invalid_service_error(api_client):
    """Test sprawdzający obsługę błędu dla nieprawidłowego serwisu w _parse_weather_data."""
    with pytest.raises(ValueError, match="Brak implementacji parsera dla serwisu: invalid_service"):
        api_client._parse_weather_data("invalid_service", {})

def test_load_api_response_from_cache_json_error(api_client, tmp_path):
    """Test sprawdzający obsługę błędu przy wczytywaniu uszkodzonych danych JSON z cache."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    api_client.cache_dir = str(cache_dir)
    
    # Tworzenie nieprawidłowego pliku JSON
    cache_file = cache_dir / "weatherapi_Warsaw_1.json"
    cache_file.write_text("{invalid json")
    
    result = api_client.load_api_response_from_cache("weatherapi", "Warsaw_1")
    assert result is None

def test_test_weather_api_no_api_key_error(api_client):
    """Test sprawdzający obsługę błędu braku klucza API w test_weather_api."""
    api_client.api_keys = {}  # Usuwamy wszystkie klucze API
    assert not api_client.test_weather_api("weatherapi")

def test_test_weather_api_invalid_service_error(api_client):
    """Test sprawdzający obsługę błędu dla nieprawidłowego serwisu w test_weather_api."""
    assert not api_client.test_weather_api("invalid_service")

def test_get_weather_forecast_unknown_service_error(api_client):
    """Test sprawdzający obsługę błędu dla nieznanego serwisu w get_weather_forecast."""
    api_client.WEATHER_APIS["test_service"] = "http://test.api"
    api_client.api_keys["test_service"] = "test_key"
    with pytest.raises(ValueError, match="Brak implementacji dla serwisu: test_service"):
        api_client.get_weather_forecast("test_service", "Warsaw", 1)

def test_parse_weather_data_unknown_service_error(api_client):
    """Test sprawdzający obsługę błędu dla nieznanego serwisu w _parse_weather_data."""
    with pytest.raises(ValueError, match="Brak implementacji parsera dla serwisu: test_service"):
        api_client._parse_weather_data("test_service", {"test": "data"})

def test_parse_weather_data_unknown_service_error_direct(api_client):
    """Test sprawdzający obsługę błędu dla nieznanego serwisu bezpośrednio w _parse_weather_data."""
    with pytest.raises(ValueError, match="Brak implementacji parsera dla serwisu: unknown_service"):
        api_client._parse_weather_data("unknown_service", {"test": "data"}) 