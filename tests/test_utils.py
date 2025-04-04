import pytest
from unittest.mock import patch
from src.utils.logger import ColorLogger, LogLevel
from src.utils.file import prepare_file_path, handle_save_error, safe_file_operation


# Testy dla logger.py
def test_logger_initialization():
    logger = ColorLogger(level=LogLevel.DEBUG, show_timestamps=False)
    assert logger.level == LogLevel.DEBUG
    assert not logger.show_timestamps

def test_logger_levels():
    logger = ColorLogger(level=LogLevel.INFO, show_timestamps=False)
    assert logger.level == LogLevel.INFO
    assert LogLevel.DEBUG.value < LogLevel.INFO.value < LogLevel.ERROR.value

@pytest.mark.parametrize("log_method,expected_prefix,min_level", [
    ("debug", "[DEBUG]", LogLevel.DEBUG),
    ("info", "[INFO]", LogLevel.INFO),
    ("warn", "[UWAGA]", LogLevel.WARN),
    ("error", "[BŁĄD]", LogLevel.ERROR),
    ("hot_reload", "[HOT-RELOAD]", LogLevel.DEBUG)
])

def test_logger_methods(capsys, log_method, expected_prefix, min_level):
    logger = ColorLogger(level=min_level, show_timestamps=False)
    message = "Test message"
    getattr(logger, log_method)(message)
    captured = capsys.readouterr()
    assert expected_prefix in captured.out
    assert message in captured.out

def test_logger_timestamp():
    logger = ColorLogger(show_timestamps=True)
    assert logger._get_timestamp().startswith("[")
    assert logger._get_timestamp().endswith("] ")

def test_logger_level_filtering():
    logger = ColorLogger(level=LogLevel.WARN, show_timestamps=False)
    with patch('builtins.print') as mock_print:
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warn("Warning message")
        logger.error("Error message")
        
        # Tylko warn i error powinny być wyświetlone
        assert mock_print.call_count == 2

# Testy dla file.py
def test_prepare_file_path(tmp_path):
    test_path = tmp_path / "test_dir" / "test_file.txt"
    prepare_file_path(str(test_path))
    assert test_path.parent.exists()

def test_handle_save_error():
    test_error = Exception("Test error")
    with pytest.raises(ValueError) as exc_info:
        handle_save_error(test_error, "TEST")
    assert "Błąd podczas zapisywania danych do TEST" in str(exc_info.value)

def test_safe_file_operation_success(tmp_path):
    test_file = tmp_path / "test.txt"
    
    def mock_operation(filepath):
        with open(filepath, 'w') as f:
            f.write("test")
        return True

    result = safe_file_operation(mock_operation, str(test_file), "TEST")
    assert result is True
    assert test_file.exists()
    assert test_file.read_text() == "test"

def test_safe_file_operation_failure():
    def mock_operation(_):
        raise Exception("Test error")

    with pytest.raises(ValueError) as exc_info:
        safe_file_operation(mock_operation, "nonexistent/path", "TEST")
    assert "Błąd podczas zapisywania danych do TEST" in str(exc_info.value) 