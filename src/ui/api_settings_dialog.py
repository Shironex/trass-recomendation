"""
Dialog konfiguracji ustawień API dla pogody i tras turystycznych.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QFormLayout,
    QGroupBox, QCheckBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import pyqtSignal, QSettings
from src.core import ApiClient


class ApiSettingsDialog(QDialog):
    """Dialog konfiguracji API pogodowego i trasowego."""
    
    # Sygnał emitowany po zapisaniu konfiguracji
    api_config_saved = pyqtSignal(dict)
    
    def __init__(self, parent=None, settings=None):
        """
        Inicjalizacja dialogu konfiguracji API.
        
        Args:
            parent: Rodzic widgetu.
            settings: Obiekt QSettings do przechowywania konfiguracji.
        """
        super().__init__(parent)
        self.settings = settings or QSettings("TrassRecommendation", "ApiSettings")
        self.api_widgets = {}
        
        self.setWindowTitle("Konfiguracja API")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        self.init_ui()
        self.load_saved_settings()
    
    def init_ui(self):
        """Inicjalizacja interfejsu użytkownika."""
        main_layout = QVBoxLayout(self)
        
        # Tworzenie zakładek
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Zakładka API pogodowego
        weather_tab = QWidget()
        tab_widget.addTab(weather_tab, "API Pogodowe")
        
        weather_layout = QVBoxLayout(weather_tab)
        
        # OpenWeatherMap
        owm_group = QGroupBox("OpenWeatherMap")
        weather_layout.addWidget(owm_group)
        
        owm_layout = QFormLayout(owm_group)
        owm_key = QLineEdit()
        owm_key.setEchoMode(QLineEdit.EchoMode.Password)
        owm_key.setPlaceholderText("Wprowadź klucz API")
        owm_layout.addRow("Klucz API:", owm_key)
        
        owm_test_btn = QPushButton("Testuj połączenie")
        owm_test_btn.clicked.connect(
            lambda: self.test_weather_api("openweathermap", owm_key.text())
        )
        owm_layout.addRow("", owm_test_btn)
        
        self.api_widgets["openweathermap"] = owm_key
        
        # WeatherAPI
        weatherapi_group = QGroupBox("WeatherAPI.com")
        weather_layout.addWidget(weatherapi_group)
        
        weatherapi_layout = QFormLayout(weatherapi_group)
        weatherapi_key = QLineEdit()
        weatherapi_key.setEchoMode(QLineEdit.EchoMode.Password)
        weatherapi_key.setPlaceholderText("Wprowadź klucz API")
        weatherapi_layout.addRow("Klucz API:", weatherapi_key)
        
        weatherapi_test_btn = QPushButton("Testuj połączenie")
        weatherapi_test_btn.clicked.connect(
            lambda: self.test_weather_api("weatherapi", weatherapi_key.text())
        )
        weatherapi_layout.addRow("", weatherapi_test_btn)
        
        self.api_widgets["weatherapi"] = weatherapi_key
        
        # Visual Crossing
        visualcrossing_group = QGroupBox("Visual Crossing Weather")
        weather_layout.addWidget(visualcrossing_group)
        
        visualcrossing_layout = QFormLayout(visualcrossing_group)
        visualcrossing_key = QLineEdit()
        visualcrossing_key.setEchoMode(QLineEdit.EchoMode.Password)
        visualcrossing_key.setPlaceholderText("Wprowadź klucz API")
        visualcrossing_layout.addRow("Klucz API:", visualcrossing_key)
        
        visualcrossing_test_btn = QPushButton("Testuj połączenie")
        visualcrossing_test_btn.clicked.connect(
            lambda: self.test_weather_api("visualcrossing", visualcrossing_key.text())
        )
        visualcrossing_layout.addRow("", visualcrossing_test_btn)
        
        self.api_widgets["visualcrossing"] = visualcrossing_key
        
        # Informacja o przykładowych danych
        example_group = QGroupBox("Informacja o trasach")
        weather_layout.addWidget(example_group)
        
        example_layout = QFormLayout(example_group)
        example_label = QLabel("Funkcja pobierania tras z API została usunięta. " 
                             "W przyszłej wersji zostanie zaimplementowane generowanie " 
                             "danych o trasach za pomocą OpenAI.")
        example_layout.addRow("", example_label)
        
        # Zakładka ustawień pamięci podręcznej
        cache_tab = QWidget()
        tab_widget.addTab(cache_tab, "Pamięć podręczna")
        
        cache_layout = QVBoxLayout(cache_tab)
        
        enable_cache = QCheckBox("Używaj pamięci podręcznej dla zapytań API")
        enable_cache.setChecked(self.settings.value("cache/enabled", False, bool))
        cache_layout.addWidget(enable_cache)
        
        cache_dir_layout = QHBoxLayout()
        cache_layout.addLayout(cache_dir_layout)
        
        cache_dir_label = QLabel("Folder pamięci podręcznej:")
        cache_dir_layout.addWidget(cache_dir_label)
        
        cache_dir_edit = QLineEdit()
        cache_dir_edit.setText(self.settings.value("cache/directory", "", str))
        cache_dir_layout.addWidget(cache_dir_edit)
        
        cache_dir_btn = QPushButton("Przeglądaj...")
        cache_dir_btn.clicked.connect(lambda: self.select_cache_directory(cache_dir_edit))
        cache_dir_layout.addWidget(cache_dir_btn)
        
        self.api_widgets["cache_enabled"] = enable_cache
        self.api_widgets["cache_directory"] = cache_dir_edit
        
        # Przyciski OK/Anuluj
        button_layout = QHBoxLayout()
        main_layout.addLayout(button_layout)
        
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.save_and_close)
        button_layout.addWidget(ok_button)
        
        cancel_button = QPushButton("Anuluj")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
    
    def load_saved_settings(self):
        """Wczytuje zapisane ustawienia API."""
        for service_name, widget in self.api_widgets.items():
            if service_name not in ["cache_enabled", "cache_directory"]:
                widget.setText(self.settings.value(f"api_keys/{service_name}", "", str))
    
    def save_and_close(self):
        """Zapisuje ustawienia i zamyka dialog."""
        # Zapisz klucze API
        for service_name, widget in self.api_widgets.items():
            if service_name not in ["cache_enabled", "cache_directory"]:
                if widget.text():
                    self.settings.setValue(f"api_keys/{service_name}", widget.text())
        
        # Zapisz ustawienia pamięci podręcznej
        self.settings.setValue("cache/enabled", self.api_widgets["cache_enabled"].isChecked())
        self.settings.setValue("cache/directory", self.api_widgets["cache_directory"].text())
        
        # Przygotuj dane konfiguracyjne do przekazania
        config_data = {
            "api_keys": {
                service: widget.text() 
                for service, widget in self.api_widgets.items()
                if service not in ["cache_enabled", "cache_directory"] and widget.text()
            },
            "cache": {
                "enabled": self.api_widgets["cache_enabled"].isChecked(),
                "directory": self.api_widgets["cache_directory"].text()
            }
        }
        
        # Emituj sygnał z nowymi ustawieniami
        self.api_config_saved.emit(config_data)
        
        self.accept()
    
    def select_cache_directory(self, line_edit):
        """Otwiera dialog wyboru katalogu pamięci podręcznej."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Wybierz katalog pamięci podręcznej",
            line_edit.text() or "."
        )
        
        if directory:
            line_edit.setText(directory)
    
    def test_weather_api(self, service, api_key):
        """
        Testuje połączenie z API pogodowym.
        
        Args:
            service: Nazwa serwisu API.
            api_key: Klucz API do przetestowania.
        """
        if not api_key:
            QMessageBox.warning(
                self,
                "Brak klucza API",
                f"Wprowadź klucz API dla serwisu {service}."
            )
            return
        
        try:
            # Tymczasowy klient API do testów
            api_client = ApiClient({service: api_key})
            
            # Sprawdzenie dostępności API poprzez proste zapytanie
            if service == "openweathermap":
                # Używamy prostego zapytania o aktualne warunki pogodowe zamiast prognozy
                import requests
                url = f"https://api.openweathermap.org/data/2.5/weather?q=Warsaw&appid={api_key}&units=metric"
                response = requests.get(url)
                response.raise_for_status()
                QMessageBox.information(
                    self,
                    "Test udany",
                    f"Połączenie z API {service} działa poprawnie."
                )
            else:
                # Dla innych API używamy standardowej metody
                records = api_client.get_weather_forecast(service, "Warszawa", 1)
                
                if records:
                    QMessageBox.information(
                        self,
                        "Test udany",
                        f"Połączenie z API {service} działa poprawnie."
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Test nieudany",
                        f"Połączenie z API {service} nie zwróciło wyników."
                    )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Błąd połączenia",
                f"Nie udało się połączyć z API {service}.\nBłąd: {str(e)}"
            ) 