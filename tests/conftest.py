"""
Konfiguracja testów dla projektu Trass Recommendation System.

Ten plik zawiera elementy wspólne dla wszystkich testów, takie jak
fixtures i konfiguracja środowiska testowego.
"""

import os
import tempfile
import pytest
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