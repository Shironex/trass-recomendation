"""
Testy dla modułu main.py - głównego pliku aplikacji.
Testujemy funkcjonalności niezależne od GUI.
"""

import pytest
from unittest.mock import patch, MagicMock
import sys
import importlib
import argparse
from src.utils import LogLevel, ColorLogger
from src.config import Config


class MockMainWindow:
    """Mock dla klasy MainWindow z modułu ui."""
    def __init__(self):
        self.windowIcon = None
    
    def setWindowIcon(self, icon):
        self.windowIcon = icon
    
    def show(self):
        pass


@pytest.fixture(autouse=True)
def mock_imports():
    """Fixture do mockowania wszystkich importów."""
    mock_app = MagicMock()
    mock_icon = MagicMock()
    mock_size = MagicMock()
    MockMainWindow()
    
    with patch.dict('sys.modules', {
        'PyQt6': MagicMock(),
        'PyQt6.QtWidgets': MagicMock(QApplication=mock_app),
        'PyQt6.QtGui': MagicMock(QIcon=mock_icon),
        'PyQt6.QtCore': MagicMock(QSize=mock_size),
        'ui': MagicMock(),
        'ui.main': MagicMock(MainWindow=MockMainWindow),
        'src.hot_reload': MagicMock()
    }):
        yield


@pytest.fixture
def mock_logger():
    """Fixture do mockowania loggera."""
    test_logger = ColorLogger()
    with patch('src.utils.logger', test_logger), \
         patch('src.main.logger', test_logger):
        yield test_logger


def run_main_with_args(args, logger):
    """Uruchamia kod z main.py z podanymi argumentami."""
    config = Config()
    parser = argparse.ArgumentParser(description=config.app_title)
    parser.add_argument("--hot-reload", action="store_true", help="Włącz hot reload (automatyczne przeładowanie przy zmianach)")
    parser.add_argument("--debug", action="store_true", help="Włącz tryb debugowania (więcej logów)")
    parser.add_argument("--hot-reload-level", action="store_true", help="Ustaw poziom logowania na HOT_RELOAD (logi hot reload i wyższe)")
    args = parser.parse_args(args)
    
    if args.debug:
        logger.level = LogLevel.DEBUG
    elif args.hot_reload_level:
        logger.level = LogLevel.HOT_RELOAD
    else:
        logger.level = LogLevel.INFO


def test_try_enable_hot_reload_success():
    """Test pomyślnego włączenia hot reload."""
    mock_reloader = MagicMock()
    mock_enable = MagicMock(return_value=mock_reloader)
    
    with patch.dict('sys.modules', {'src.hot_reload': MagicMock(enable_hot_reload=mock_enable)}):
        import src.main
        importlib.reload(sys.modules['src.main'])
        
        reloader = src.main.try_enable_hot_reload()
        
        assert reloader == mock_reloader
        mock_enable.assert_called_once_with(directories=['src/ui/pages'])


def test_try_enable_hot_reload_import_error():
    """Test obsługi błędu importu przy włączaniu hot reload."""
    with patch.dict('sys.modules', {'src.hot_reload': None}):
        import src.main
        importlib.reload(sys.modules['src.main'])
        
        reloader = src.main.try_enable_hot_reload()
        
        assert reloader is None


def test_command_line_args_debug(mock_logger):
    """Test parsowania argumentów linii poleceń z opcją --debug."""
    run_main_with_args(['--debug'], mock_logger)
    assert mock_logger.level == LogLevel.DEBUG


def test_command_line_args_hot_reload(mock_logger):
    """Test parsowania argumentów linii poleceń z opcją --hot-reload."""
    run_main_with_args(['--hot-reload'], mock_logger)
    assert mock_logger.level == LogLevel.INFO


def test_command_line_args_hot_reload_level(mock_logger):
    """Test parsowania argumentów linii poleceń z opcją --hot-reload-level."""
    run_main_with_args(['--hot-reload-level'], mock_logger)
    assert mock_logger.level == LogLevel.HOT_RELOAD


def test_command_line_args_no_options(mock_logger):
    """Test parsowania argumentów linii poleceń bez opcji."""
    run_main_with_args([], mock_logger)
    assert mock_logger.level == LogLevel.INFO 