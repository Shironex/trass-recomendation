"""
Konfiguracja testów dla projektu Trass Recommendation System.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, mock_open, MagicMock
from datetime import date
from src.core.trail_data import TrailData, TrailRecord
from src.core.weather_data import WeatherData, WeatherRecord

# Definicja ścieżek do plików testowych
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test_data')

@pytest.fixture(scope="session")
def ensure_test_data_dir():
    """Tworzy katalog na dane testowe, jeśli nie istnieje."""
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    return TEST_DATA_DIR

@pytest.fixture
def temp_file():
    """Tworzy tymczasowy plik i zwraca jego ścieżkę, a po teście usuwa go."""
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp_path = temp.name
    temp.close()
    
    yield temp_path
    
    # Usuń plik po teście
    try:
        os.unlink(temp_path)
    except:
        pass

@pytest.fixture
def sample_date():
    """Zwraca przykładową datę do testów."""
    return date(2023, 7, 15)

@pytest.fixture
def mock_fernet_config():
    """
    Fixture do mockowania konfiguracji Fernet.
    
    Zwraca:
        tuple: (mock_exists, mock_urandom, mock_pbkdf2, mock_b64encode, mock_fernet)
    """
    with patch('os.makedirs') as mock_makedirs, \
         patch('os.path.exists') as mock_exists, \
         patch('builtins.open', mock_open()), \
         patch('os.urandom') as mock_urandom, \
         patch('cryptography.hazmat.primitives.kdf.pbkdf2.PBKDF2HMAC') as mock_pbkdf2, \
         patch('base64.urlsafe_b64encode') as mock_b64encode, \
         patch('cryptography.fernet.Fernet') as mock_fernet:
        
        mock_exists.return_value = False
        mock_urandom.return_value = b"test_salt"
        mock_pbkdf2_instance = MagicMock()
        mock_pbkdf2.return_value = mock_pbkdf2_instance
        mock_pbkdf2_instance.derive.return_value = b"01234567890123456789012345678901"
        mock_b64encode.return_value = b"MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE="
        mock_fernet_instance = MagicMock()
        mock_fernet.return_value = mock_fernet_instance
        
        yield (mock_exists, mock_urandom, mock_pbkdf2, mock_b64encode, mock_fernet)

@pytest.fixture
def sample_trail():
    """Fixture zwracający przykładową trasę do testów."""
    return TrailRecord(
        id="1",
        name="Test Trail",
        region="Test Region",
        start_lat=50.0,
        start_lon=20.0,
        end_lat=50.1,
        end_lon=20.1,
        length_km=10.0,
        elevation_gain=500,
        difficulty=3,
        terrain_type="mountain",
        tags=["scenic", "challenging"]
    )

@pytest.fixture
def sample_trail_data(sample_trail):
    """Fixture zwracający przykładowy obiekt TrailData."""
    trail_data = TrailData()
    trail_data.trails = [sample_trail]
    return trail_data

@pytest.fixture
def sample_weather_record():
    """Fixture zwracający przykładowy rekord pogodowy."""
    return WeatherRecord(
        date=date(2023, 7, 15),
        location_id="Test Region",
        avg_temp=20.0,
        min_temp=15.0,
        max_temp=25.0,
        precipitation=0.0,
        sunshine_hours=8.0,
        cloud_cover=20
    )

@pytest.fixture
def sample_weather_data(sample_weather_record):
    """Fixture zwracający przykładowy obiekt WeatherData."""
    weather_data = WeatherData()
    weather_data.records = [sample_weather_record]
    return weather_data

@pytest.fixture
def route_recommender(sample_trail_data, sample_weather_data):
    """Fixture zwracający obiekt RouteRecommender z przykładowymi danymi."""
    from src.core.data_processor import RouteRecommender
    return RouteRecommender(sample_trail_data, sample_weather_data)