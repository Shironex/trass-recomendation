"""
Dialog konfiguracji ustawień API dla pogody i tras turystycznych.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTabWidget, QWidget, QFormLayout,
    QGroupBox, QCheckBox, QMessageBox, QFileDialog,
    QScrollArea, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from urllib.parse import urlencode
from src.core import ApiClient
from src.config import Config


class ApiSettingsDialog(QDialog):
    """Dialog konfiguracji API pogodowego i trasowego."""
    
    # Sygnał emitowany po zapisaniu konfiguracji
    api_config_saved = pyqtSignal(ApiClient)
    
    def __init__(self, parent=None):
        """
        Inicjalizacja dialogu konfiguracji API.
        
        Args:
            parent: Rodzic widgetu.
        """
        super().__init__(parent)
        self.config = Config()
        self.api_widgets = {}
        
        self.setWindowTitle("Konfiguracja API")
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
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
            lambda: self.test_api_connection("visualcrossing", visualcrossing_key.text())
        )
        visualcrossing_layout.addRow("", visualcrossing_test_btn)
        
        self.api_widgets["visualcrossing"] = visualcrossing_key
        
        # Dodanie elastycznego odstępu na końcu
        weather_layout.addStretch()
        
        # Zakładka informacji o API
        info_tab = QWidget()
        tab_widget.addTab(info_tab, "Informacje o API")
        
        info_layout = QVBoxLayout(info_tab)
        
        # Dodanie obszaru przewijania
        info_scroll = QScrollArea()
        info_scroll.setWidgetResizable(True)
        info_scroll.setFrameShape(QFrame.Shape.NoFrame)
        info_layout.addWidget(info_scroll)
        
        info_content = QWidget()
        info_content_layout = QVBoxLayout(info_content)
        info_scroll.setWidget(info_content)
        
        # Sekcja Visual Crossing
        vc_info = QGroupBox("Visual Crossing Weather")
        info_content_layout.addWidget(vc_info)
        vc_info_layout = QVBoxLayout(vc_info)
        vc_info_text = QLabel(
            "<h3>Visual Crossing Weather</h3>"
            "<p>Zaawansowane API pogodowe z dokładnymi prognozami długoterminowymi.</p>"
            "<p><b>Główne cechy:</b></p>"
            "<ul>"
            "<li>Darmowy plan: 1000 zapytań dziennie</li>"
            "<li>15-dniowa prognoza pogody</li>"
            "<li>Szczegółowe dane meteorologiczne</li>"
            "<li>Dostęp do danych historycznych</li>"
            "<li>Zaawansowane metryki pogodowe</li>"
            "</ul>"
            "<p><b>Jak zdobyć klucz API:</b></p>"
            "<ol>"
            "<li>Wejdź na <a href='https://www.visualcrossing.com/weather-api'>Visual Crossing Weather API</a></li>"
            "<li>Kliknij 'Sign Up For Free'</li>"
            "<li>Wybierz darmowy plan</li>"
            "<li>Po rejestracji otrzymasz klucz API</li>"
            "</ol>"
            "<p><b>Zalecenia:</b></p>"
            "<ul>"
            "<li>Najlepsza opcja dla dokładnych prognoz długoterminowych</li>"
            "<li>Idealne do planowania tras w górach</li>"
            "<li>Warto używać z pamięcią podręczną dla optymalizacji limitów</li>"
            "</ul>"
        )
        vc_info_text.setWordWrap(True)
        vc_info_text.setTextFormat(Qt.TextFormat.RichText)
        vc_info_text.setOpenExternalLinks(True)
        vc_info_layout.addWidget(vc_info_text)
        
        # Dodanie elastycznego odstępu
        info_content_layout.addStretch()
        
        # Zakładka ustawień pamięci podręcznej
        cache_tab = QWidget()
        tab_widget.addTab(cache_tab, "Pamięć podręczna")
        
        cache_layout = QVBoxLayout(cache_tab)
        
        # Informacje o pamięci podręcznej
        cache_info = QLabel(
            "<h3>Pamięć podręczna API</h3>"
            "<p>Włączenie pamięci podręcznej pozwala na:</p>"
            "<ul>"
            "<li>Szybszy dostęp do często używanych danych</li>"
            "<li>Zmniejszenie liczby zapytań do API</li>"
            "<li>Oszczędność limitu zapytań</li>"
            "<li>Działanie aplikacji offline (dla zapisanych danych)</li>"
            "</ul>"
            "<p>Zalecane jest włączenie pamięci podręcznej i wybranie folderu na dysku lokalnym.</p>"
        )
        cache_info.setWordWrap(True)
        cache_info.setTextFormat(Qt.TextFormat.RichText)
        cache_layout.addWidget(cache_info)
        
        enable_cache = QCheckBox("Używaj pamięci podręcznej dla zapytań API")
        cache_settings = self.config.get_cache_settings()
        enable_cache.setChecked(cache_settings["enabled"])
        cache_layout.addWidget(enable_cache)
        
        cache_dir_layout = QHBoxLayout()
        cache_layout.addLayout(cache_dir_layout)
        
        cache_dir_label = QLabel("Folder pamięci podręcznej:")
        cache_dir_layout.addWidget(cache_dir_label)
        
        cache_dir_edit = QLineEdit()
        cache_dir_edit.setText(cache_settings["directory"])
        cache_dir_layout.addWidget(cache_dir_edit)
        
        cache_dir_btn = QPushButton("Przeglądaj...")
        cache_dir_btn.clicked.connect(lambda: self.select_cache_directory(cache_dir_edit))
        cache_dir_layout.addWidget(cache_dir_btn)
        
        self.api_widgets["cache_enabled"] = enable_cache
        self.api_widgets["cache_directory"] = cache_dir_edit
        
        # Dodanie elastycznego odstępu
        cache_layout.addStretch()
        
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
                widget.setText(self.config.get_api_key(service_name))
    
    def save_and_close(self):
        """Zapisuje ustawienia i zamyka dialog."""
        # Zapisz klucze API
        api_keys = {}
        for service_name, widget in self.api_widgets.items():
            if service_name not in ["cache_enabled", "cache_directory"]:
                key = widget.text()
                self.config.set_api_key(service_name, key)
                if key:
                    api_keys[service_name] = key
        
        # Zapisz ustawienia pamięci podręcznej
        cache_enabled = self.api_widgets["cache_enabled"].isChecked()
        cache_dir = self.api_widgets["cache_directory"].text()
        
        self.config.set_cache_settings(
            enabled=cache_enabled,
            directory=cache_dir
        )
        
        # Zapisz konfigurację
        self.config.save()
        
        # Utwórz nowego klienta API
        cache_dir = cache_dir if cache_enabled else None
        api_client = ApiClient(api_keys, cache_dir)
        
        # Emituj sygnał z nowym klientem API
        self.api_config_saved.emit(api_client)
        
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
    
    def test_api_connection(self, service: str, api_key: str):
        """
        Testuje połączenie z API.
        
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
            
            # Używamy metody test_weather_api z ApiClient
            if api_client.test_weather_api(service):
                QMessageBox.information(
                    self,
                    "Test udany",
                    f"Połączenie z API {service} działa poprawnie."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Test nieudany",
                    f"Połączenie z API {service} nie działa poprawnie."
                )
        
        except Exception as e:
            QMessageBox.critical(
                self,
                "Błąd połączenia",
                f"Nie udało się połączyć z API {service}.\nBłąd: {str(e)}"
            ) 