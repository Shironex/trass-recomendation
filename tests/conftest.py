"""
Konfiguracja testów dla projektu Trass Recommendation System.
"""

import os
import tempfile
import pytest
from unittest.mock import patch, mock_open, MagicMock
from datetime import date

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