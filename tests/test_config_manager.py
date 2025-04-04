"""
Testy dla klasy Config zarządzającej konfiguracją aplikacji.
"""
import os
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock
from src.config.config import Config


@pytest.fixture
def config(mock_fernet_config):
    """Fixture zwracający instancję Config z mockowanym katalogiem konfiguracyjnym."""
    with patch('src.config.config.Config._get_config_dir') as mock_get_dir:
        mock_get_dir.return_value = "/mock/config/dir"
        config = Config()
        return config


def test_init(config):
    """Test inicjalizacji klasy Config."""
    assert config.config_dir == "/mock/config/dir"
    assert config.APP_TITLE == "Rekomendator Tras Turystycznych"
    assert config.APP_NAME == "TrassRecommendation"
    assert config.CONFIG_FILE == "config.json"
    assert config.ENCRYPTION_KEY_FILE == ".key"


def test_get_config_dir_windows(mock_fernet_config):
    """Test pobierania ścieżki konfiguracji w systemie Windows."""
    with patch('os.name', 'nt'), \
         patch('os.getenv') as mock_getenv, \
         patch('os.path.join') as mock_join:
        mock_getenv.return_value = "C:\\Users\\Test\\AppData\\Roaming"
        mock_join.return_value = "C:\\Users\\Test\\AppData\\Roaming\\TrassRecommendation"
        config = Config()
        assert config._get_config_dir() == "C:\\Users\\Test\\AppData\\Roaming\\TrassRecommendation"


def test_get_config_dir_unix(mock_fernet_config):
    """Test pobierania ścieżki konfiguracji w systemie Unix."""
    with patch('os.name', 'posix'), \
         patch('os.path.expanduser') as mock_expand, \
         patch('os.path.join') as mock_join:
        mock_expand.return_value = "/home/test"
        mock_join.return_value = "/home/test/.config/TrassRecommendation"
        config = Config()
        assert config._get_config_dir() == "/home/test/.config/TrassRecommendation"


def test_ensure_config_dir(config):
    """Test tworzenia katalogu konfiguracyjnego."""
    with patch('os.path.exists') as mock_exists, patch('os.makedirs') as mock_makedirs:
        mock_exists.return_value = False
        config._ensure_config_dir()
        mock_makedirs.assert_called_once_with("/mock/config/dir")


def test_get_or_create_key_existing(config):
    """Test pobierania istniejącego klucza szyfrowania."""
    mock_key = b"MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE="
    with patch('os.path.exists') as mock_exists, patch('builtins.open', mock_open(read_data=mock_key)):
        mock_exists.return_value = True
        key = config._get_or_create_key()
        assert key == mock_key


def test_get_or_create_key_new(mock_fernet_config):
    """Test tworzenia nowego klucza szyfrowania."""
    mock_exists, mock_urandom, mock_pbkdf2, mock_b64encode, mock_fernet = mock_fernet_config
    config = Config()
    key = config._get_or_create_key()
    assert isinstance(key, bytes)


def test_load_config_new(config):
    """Test wczytywania nowej konfiguracji."""
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = False
        config_data = config._load_config()
        assert config_data == {
            "api_keys": {},
            "cache": {
                "enabled": False,
                "directory": ""
            }
        }


def test_load_config_existing(config):
    """Test wczytywania istniejącej konfiguracji."""
    mock_encrypted_data = {
        "api_keys": {
            "test_api": "encrypted_key"
        },
        "cache": {
            "enabled": True,
            "directory": "/test/cache"
        }
    }
    
    with patch('os.path.exists') as mock_exists, \
         patch('builtins.open', mock_open(read_data=json.dumps(mock_encrypted_data))), \
         patch.object(config, '_fernet') as mock_fernet:
        mock_exists.return_value = True
        mock_fernet.decrypt.return_value = b"decrypted_key"
        
        config_data = config._load_config()
        assert config_data["cache"] == mock_encrypted_data["cache"]
        assert config_data["api_keys"]["test_api"] == "decrypted_key"


def test_save_config(config):
    """Test zapisywania konfiguracji."""
    config._config = {
        "api_keys": {
            "test_api": "test_key"
        },
        "cache": {
            "enabled": True,
            "directory": "/test/cache"
        }
    }
    
    with patch('builtins.open', mock_open()) as mock_file, \
         patch.object(config, '_fernet') as mock_fernet:
        mock_fernet.encrypt.return_value = b"encrypted_key"
        config.save()
        mock_file.assert_called_once()


def test_get_api_key(config):
    """Test pobierania klucza API."""
    config._config = {
        "api_keys": {
            "test_api": "test_key"
        }
    }
    assert config.get_api_key("test_api") == "test_key"
    assert config.get_api_key("nonexistent") == ""


def test_set_api_key(config):
    """Test ustawiania klucza API."""
    config.set_api_key("test_api", "test_key")
    assert config._config["api_keys"]["test_api"] == "test_key"


def test_get_cache_settings(config):
    """Test pobierania ustawień pamięci podręcznej."""
    config._config = {
        "cache": {
            "enabled": True,
            "directory": "/test/cache"
        }
    }
    settings = config.get_cache_settings()
    assert settings["enabled"] is True
    assert settings["directory"] == "/test/cache"


def test_set_cache_settings(config):
    """Test ustawiania konfiguracji pamięci podręcznej."""
    config.set_cache_settings(True, "/test/cache")
    assert config._config["cache"]["enabled"] is True
    assert config._config["cache"]["directory"] == "/test/cache"


def test_app_title_property(config):
    """Test właściwości app_title."""
    assert config.app_title == "Rekomendator Tras Turystycznych" 