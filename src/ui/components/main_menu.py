"""
Moduł zawierający klasę głównego menu aplikacji.
"""

from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtCore import pyqtSignal
from src.utils.logger import logger


class MainMenu(QMenuBar):
    """
    Klasa reprezentująca menu główne aplikacji.
    
    Zawiera wszystkie menu i akcje dostępne w głównym oknie aplikacji.
    """
    
    # Sygnały emitowane przez menu
    show_home_signal = pyqtSignal()
    show_trail_signal = pyqtSignal()
    show_weather_signal = pyqtSignal()
    show_recommendation_signal = pyqtSignal()
    show_api_settings_signal = pyqtSignal()
    show_about_signal = pyqtSignal()
    exit_signal = pyqtSignal()
    
    # Sygnały dla operacji na danych
    load_trails_csv_signal = pyqtSignal()
    load_trails_json_signal = pyqtSignal()
    load_weather_csv_signal = pyqtSignal()
    load_weather_json_signal = pyqtSignal()
    export_trails_csv_signal = pyqtSignal()
    export_trails_json_signal = pyqtSignal()
    export_weather_csv_signal = pyqtSignal()
    export_weather_json_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        """
        Inicjalizacja menu głównego.
        
        Args:
            parent: Rodzic widgetu (główne okno).
        """
        super().__init__(parent)
        
        logger.debug("Inicjalizacja menu głównego")
        self._create_menu()
    
    def _create_menu(self):
        """Tworzy strukturę menu aplikacji."""
        # Menu Plik
        file_menu = self.addMenu("&Plik")
        
        # Podmenu Wczytaj dane
        load_menu = file_menu.addMenu("Wczytaj dane")
        
        # Opcje wczytywania tras
        load_trails_menu = load_menu.addMenu("Trasy")
        load_trails_csv = load_trails_menu.addAction("Z pliku CSV")
        load_trails_csv.triggered.connect(self.load_trails_csv_signal.emit)
        load_trails_json = load_trails_menu.addAction("Z pliku JSON")
        load_trails_json.triggered.connect(self.load_trails_json_signal.emit)
        
        # Opcje wczytywania danych pogodowych
        load_weather_menu = load_menu.addMenu("Pogoda")
        load_weather_csv = load_weather_menu.addAction("Z pliku CSV")
        load_weather_csv.triggered.connect(self.load_weather_csv_signal.emit)
        load_weather_json = load_weather_menu.addAction("Z pliku JSON")
        load_weather_json.triggered.connect(self.load_weather_json_signal.emit)
        
        # Podmenu Eksportuj dane
        export_menu = file_menu.addMenu("Eksportuj dane")
        
        # Opcje eksportowania tras
        export_trails_menu = export_menu.addMenu("Trasy")
        export_trails_csv = export_trails_menu.addAction("Do pliku CSV")
        export_trails_csv.triggered.connect(self.export_trails_csv_signal.emit)
        export_trails_json = export_trails_menu.addAction("Do pliku JSON")
        export_trails_json.triggered.connect(self.export_trails_json_signal.emit)
        
        # Opcje eksportowania danych pogodowych
        export_weather_menu = export_menu.addMenu("Pogoda")
        export_weather_csv = export_weather_menu.addAction("Do pliku CSV")
        export_weather_csv.triggered.connect(self.export_weather_csv_signal.emit)
        export_weather_json = export_weather_menu.addAction("Do pliku JSON")
        export_weather_json.triggered.connect(self.export_weather_json_signal.emit)
        
        file_menu.addSeparator()
        
        # Akcja wyjścia
        exit_action = file_menu.addAction("Zakończ")
        exit_action.triggered.connect(self.exit_signal.emit)
        
        # Menu Narzędzia
        tools_menu = self.addMenu("&Narzędzia")
        
        # Akcja konfiguracji API
        api_settings_action = tools_menu.addAction("Konfiguracja API")
        api_settings_action.triggered.connect(self.show_api_settings_signal.emit)
        
        # Menu Widok
        view_menu = self.addMenu("&Widok")
        
        # Akcje przełączania stron
        home_action = view_menu.addAction("Strona główna")
        home_action.triggered.connect(self.show_home_signal.emit)
        
        trail_action = view_menu.addAction("Zarządzanie trasami")
        trail_action.triggered.connect(self.show_trail_signal.emit)
        
        weather_action = view_menu.addAction("Dane pogodowe")
        weather_action.triggered.connect(self.show_weather_signal.emit)
        
        recommendation_action = view_menu.addAction("Rekomendacje")
        recommendation_action.triggered.connect(self.show_recommendation_signal.emit)
        
        # Menu Pomoc
        help_menu = self.addMenu("&Pomoc")
        
        # Akcja Informacje
        about_action = help_menu.addAction("O programie")
        about_action.triggered.connect(self.show_about_signal.emit) 