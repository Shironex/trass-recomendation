"""
Moduł do globalnej konfiguracji aplikacji.
"""
import json
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from src.utils import logger


class Config:
    """
    Klasa do globalnej konfiguracji.
    
    Zarządza konfiguracją aplikacji, w tym kluczami API i ustawieniami pamięci podręcznej.
    Zapisuje dane w pliku config.json w bezpieczny sposób.
    """
    
    APP_TITLE = "Rekomendator Tras Turystycznych"
    APP_NAME = "TrassRecommendation"
    CONFIG_FILE = "config.json"
    ENCRYPTION_KEY_FILE = ".key"
    
    def __init__(self):
        """Inicjalizacja konfiguracji."""
        self.config_dir = self._get_config_dir()
        self._ensure_config_dir()
        self._encryption_key = self._get_or_create_key()
        self._fernet = Fernet(self._encryption_key)
        self._config = self._load_config()
    
    def _get_config_dir(self) -> str:
        """
        Zwraca ścieżkę do katalogu konfiguracji.
        
        Returns:
            str: Ścieżka do katalogu konfiguracji
        """
        # W systemie Windows używamy APPDATA, w innych ~/.config
        if os.name == 'nt':
            base_dir = os.getenv('APPDATA')
        else:
            base_dir = os.path.expanduser('~/.config')
        
        return os.path.join(base_dir, self.APP_NAME)
    
    def _ensure_config_dir(self):
        """Tworzy katalog konfiguracji, jeśli nie istnieje."""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def _get_or_create_key(self) -> bytes:
        """
        Pobiera lub tworzy klucz szyfrowania.
        
        Returns:
            bytes: Klucz szyfrowania
        """
        key_path = os.path.join(self.config_dir, self.ENCRYPTION_KEY_FILE)
        
        if os.path.exists(key_path):
            with open(key_path, 'rb') as f:
                return f.read()
        
        # Generowanie nowego klucza
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.APP_NAME.encode()))
        
        # Zapisanie klucza
        with open(key_path, 'wb') as f:
            f.write(key)
        
        return key
    
    def _load_config(self) -> dict:
        """
        Wczytuje konfigurację z pliku.
        
        Returns:
            dict: Słownik z konfiguracją
        """
        config_path = os.path.join(self.config_dir, self.CONFIG_FILE)
        if not os.path.exists(config_path):
            return {
                "api_keys": {},
                "cache": {
                    "enabled": False,
                    "directory": ""
                }
            }
        
        try:
            with open(config_path, 'r') as f:
                encrypted_data = json.load(f)
                
            # Odszyfruj dane
            decrypted_data = {}
            for key, value in encrypted_data.items():
                if key == "api_keys":
                    decrypted_data[key] = {}
                    for api_name, encrypted_key in value.items():
                        try:
                            decrypted_key = self._fernet.decrypt(encrypted_key.encode()).decode()
                            decrypted_data[key][api_name] = decrypted_key
                        except Exception as e:
                            logger.error(f"Błąd podczas odszyfrowywania klucza API {api_name}: {str(e)}")
                            decrypted_data[key][api_name] = ""
                else:
                    decrypted_data[key] = value
            
            return decrypted_data
            
        except Exception as e:
            logger.error(f"Błąd podczas wczytywania konfiguracji: {str(e)}")
            return {
                "api_keys": {},
                "cache": {
                    "enabled": False,
                    "directory": ""
                }
            }
    
    def save(self):
        """Zapisuje konfigurację do pliku."""
        try:
            # Zaszyfruj klucze API przed zapisem
            encrypted_data = {}
            for key, value in self._config.items():
                if key == "api_keys":
                    encrypted_data[key] = {}
                    for api_name, api_key in value.items():
                        if api_key:  # Szyfruj tylko niepuste klucze
                            encrypted_key = self._fernet.encrypt(api_key.encode()).decode()
                            encrypted_data[key][api_name] = encrypted_key
                else:
                    encrypted_data[key] = value
            
            # Zapisz zaszyfrowane dane
            config_path = os.path.join(self.config_dir, self.CONFIG_FILE)
            with open(config_path, 'w') as f:
                json.dump(encrypted_data, f, indent=4)
                
        except Exception as e:
            logger.error(f"Błąd podczas zapisywania konfiguracji: {str(e)}")
    
    def get_api_key(self, service: str) -> str:
        """
        Pobiera klucz API dla danego serwisu.
        
        Args:
            service: Nazwa serwisu API
            
        Returns:
            str: Klucz API lub pusty string jeśli nie znaleziono
        """
        return self._config.get("api_keys", {}).get(service, "")
    
    def set_api_key(self, service: str, key: str):
        """
        Ustawia klucz API dla danego serwisu.
        
        Args:
            service: Nazwa serwisu API
            key: Klucz API
        """
        if "api_keys" not in self._config:
            self._config["api_keys"] = {}
        self._config["api_keys"][service] = key
    
    def get_cache_settings(self) -> dict:
        """
        Pobiera ustawienia pamięci podręcznej.
        
        Returns:
            dict: Słownik z ustawieniami pamięci podręcznej
        """
        return self._config.get("cache", {
            "enabled": False,
            "directory": ""
        })
    
    def set_cache_settings(self, enabled: bool, directory: str):
        """
        Ustawia konfigurację pamięci podręcznej.
        
        Args:
            enabled: Czy pamięć podręczna jest włączona
            directory: Ścieżka do katalogu pamięci podręcznej
        """
        self._config["cache"] = {
            "enabled": enabled,
            "directory": directory
        }
    
    @property
    def app_title(self) -> str:
        """Zwraca tytuł aplikacji."""
        return self.APP_TITLE