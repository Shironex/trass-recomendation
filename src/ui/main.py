"""
Główny moduł interfejsu użytkownika aplikacji Rekomendator Tras Turystycznych.
"""

import sys
sys.path.append('.')
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QStackedWidget, QMessageBox, QMenuBar, QMenu, QStatusBar,
    QFileDialog
)
from PyQt6.QtCore import QSettings, Qt
from src.ui.pages import ( HomePage, TrailPage, WeatherPage, RecommendationPage )
from src.ui.api_settings_dialog import ApiSettingsDialog
from src.ui.components import MainMenu
from src.core import ( ApiClient, TrailData, WeatherData )
from src.utils import logger


class MainWindow(QMainWindow):
    """Główne okno aplikacji."""
    
    def __init__(self):
        """Inicjalizacja głównego okna aplikacji."""
        super().__init__()
        
        self.setWindowTitle("Rekomendator Tras Turystycznych")
        self.setMinimumSize(900, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
            }
        """)
        
        # Inicjalizacja ustawień
        self.settings = QSettings("TrassRecommendation", "MainApp")
        
        # Inicjalizacja klienta API
        self.api_client = self.initialize_api_client()
        
        # Inicjalizacja obiektów do przechowywania danych
        self.trail_data = TrailData()
        self.weather_data = WeatherData()
        
        logger.debug("Inicjalizacja głównego okna aplikacji")
        self._setup_ui()
    
    def initialize_api_client(self):
        """
        Inicjalizuje klienta API na podstawie zapisanych ustawień.
        
        Returns:
            Obiekt ApiClient.
        """
        # Wczytanie kluczy API
        api_keys = {}
        settings = QSettings("TrassRecommendation", "ApiSettings")
        
        # Usługi pogodowe
        for service in ["openweathermap", "weatherapi", "visualcrossing"]:
            api_key = settings.value(f"api_keys/{service}", "", str)
            if api_key:
                api_keys[service] = api_key
        
        # Konfiguracja pamięci podręcznej
        cache_dir = None
        if settings.value("cache/enabled", False, bool):
            cache_dir = settings.value("cache/directory", "", str)
            if not cache_dir:
                cache_dir = "./cache"
        
        logger.debug(f"Inicjalizacja klienta API z {len(api_keys)} kluczami")
        return ApiClient(api_keys, cache_dir)
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Centralny widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Główny układ
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Utworzenie menu
        self.menu = MainMenu(self)
        self.setMenuBar(self.menu)
        
        # Połączenie sygnałów menu z odpowiednimi slotami
        self.menu.show_home_signal.connect(self.show_home_page)
        self.menu.show_trail_signal.connect(self.show_trail_page)
        self.menu.show_weather_signal.connect(self.show_weather_page)
        self.menu.show_recommendation_signal.connect(self.show_recommendation_page)
        self.menu.show_api_settings_signal.connect(self.show_api_settings)
        self.menu.show_about_signal.connect(self.show_about)
        self.menu.exit_signal.connect(self.close)
        
        # Połączenie sygnałów operacji na danych
        self.menu.load_trails_csv_signal.connect(self.load_trails_csv)
        self.menu.load_trails_json_signal.connect(self.load_trails_json)
        self.menu.load_weather_csv_signal.connect(self.load_weather_csv)
        self.menu.load_weather_json_signal.connect(self.load_weather_json)
        self.menu.export_trails_csv_signal.connect(self.export_trails_csv)
        self.menu.export_trails_json_signal.connect(self.export_trails_json)
        self.menu.export_weather_csv_signal.connect(self.export_weather_csv)
        self.menu.export_weather_json_signal.connect(self.export_weather_json)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Gotowy")
        
        # Stos widgetów na strony
        self.stacked_widget = QStackedWidget()
        
        # Tworzenie stron
        logger.debug("Tworzenie stron aplikacji")
        self.home_page = HomePage(self)
        self.trail_page = TrailPage(self)
        self.weather_page = WeatherPage(self)
        self.recommendation_page = RecommendationPage(self)
        
        # Dodawanie stron do stosu
        self.stacked_widget.addWidget(self.home_page)
        self.stacked_widget.addWidget(self.trail_page)
        self.stacked_widget.addWidget(self.weather_page)
        self.stacked_widget.addWidget(self.recommendation_page)
        
        # Ustawienie strony domowej jako aktywnej
        self.stacked_widget.setCurrentWidget(self.home_page)
        
        # Dodanie stosu do głównego układu
        main_layout.addWidget(self.stacked_widget)
        logger.debug("Interfejs użytkownika skonfigurowany")
    
    # Operacje na danych tras
    def load_trails_csv(self):
        """Wczytuje dane tras z pliku CSV."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wczytaj dane tras", "", "Pliki CSV (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            self.trail_data.load_from_csv(file_path)
            self.show_info(
                "Wczytano dane", 
                f"Pomyślnie wczytano {len(self.trail_data.trails)} tras z pliku CSV."
            )
            self.status_bar.showMessage(f"Wczytano {len(self.trail_data.trails)} tras z CSV", 3000)
            
            # Aktualizacja widoku tras, jeśli jest aktywny
            if self.stacked_widget.currentWidget() == self.trail_page:
                self.trail_page.update_data()
        except Exception as e:
            self.show_error("Błąd wczytywania", f"Nie udało się wczytać danych tras: {str(e)}")
    
    def load_trails_json(self):
        """Wczytuje dane tras z pliku JSON."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wczytaj dane tras", "", "Pliki JSON (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            self.trail_data.load_from_json(file_path)
            self.show_info(
                "Wczytano dane", 
                f"Pomyślnie wczytano {len(self.trail_data.trails)} tras z pliku JSON."
            )
            self.status_bar.showMessage(f"Wczytano {len(self.trail_data.trails)} tras z JSON", 3000)
            
            # Aktualizacja widoku tras, jeśli jest aktywny
            if self.stacked_widget.currentWidget() == self.trail_page:
                self.trail_page.update_data()
        except Exception as e:
            self.show_error("Błąd wczytywania", f"Nie udało się wczytać danych tras: {str(e)}")
    
    def export_trails_csv(self):
        """Eksportuje dane tras do pliku CSV."""
        if not self.trail_data.trails:
            self.show_error("Brak danych", "Brak danych tras do zapisania.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Zapisz dane tras", "", "Pliki CSV (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            self.trail_data.save_to_csv(file_path)
            self.show_info(
                "Zapisano dane", 
                f"Pomyślnie zapisano {len(self.trail_data.trails)} tras do pliku CSV."
            )
            self.status_bar.showMessage(f"Zapisano {len(self.trail_data.trails)} tras do CSV", 3000)
        except Exception as e:
            self.show_error("Błąd zapisywania", f"Nie udało się zapisać danych tras: {str(e)}")
    
    def export_trails_json(self):
        """Eksportuje dane tras do pliku JSON."""
        if not self.trail_data.trails:
            self.show_error("Brak danych", "Brak danych tras do zapisania.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Zapisz dane tras", "", "Pliki JSON (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            self.trail_data.save_to_json(file_path)
            self.show_info(
                "Zapisano dane", 
                f"Pomyślnie zapisano {len(self.trail_data.trails)} tras do pliku JSON."
            )
            self.status_bar.showMessage(f"Zapisano {len(self.trail_data.trails)} tras do JSON", 3000)
        except Exception as e:
            self.show_error("Błąd zapisywania", f"Nie udało się zapisać danych tras: {str(e)}")
    
    # Operacje na danych pogodowych
    def load_weather_csv(self):
        """Wczytuje dane pogodowe z pliku CSV."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wczytaj dane pogodowe", "", "Pliki CSV (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            self.weather_data.load_from_csv(file_path)
            self.show_info(
                "Wczytano dane", 
                f"Pomyślnie wczytano {len(self.weather_data.records)} rekordów pogodowych z pliku CSV."
            )
            self.status_bar.showMessage(f"Wczytano {len(self.weather_data.records)} rekordów pogodowych z CSV", 3000)
            
            # Aktualizacja widoku pogodowego, jeśli jest aktywny
            if self.stacked_widget.currentWidget() == self.weather_page:
                self.weather_page.update_data()
        except Exception as e:
            self.show_error("Błąd wczytywania", f"Nie udało się wczytać danych pogodowych: {str(e)}")
    
    def load_weather_json(self):
        """Wczytuje dane pogodowe z pliku JSON."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wczytaj dane pogodowe", "", "Pliki JSON (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            self.weather_data.load_from_json(file_path)
            self.show_info(
                "Wczytano dane", 
                f"Pomyślnie wczytano {len(self.weather_data.records)} rekordów pogodowych z pliku JSON."
            )
            self.status_bar.showMessage(f"Wczytano {len(self.weather_data.records)} rekordów pogodowych z JSON", 3000)
            
            # Aktualizacja widoku pogodowego, jeśli jest aktywny
            if self.stacked_widget.currentWidget() == self.weather_page:
                self.weather_page.update_data()
        except Exception as e:
            self.show_error("Błąd wczytywania", f"Nie udało się wczytać danych pogodowych: {str(e)}")
    
    def export_weather_csv(self):
        """Eksportuje dane pogodowe do pliku CSV."""
        if not self.weather_data.records:
            self.show_error("Brak danych", "Brak danych pogodowych do zapisania.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Zapisz dane pogodowe", "", "Pliki CSV (*.csv)"
        )
        
        if not file_path:
            return
        
        try:
            self.weather_data.save_to_csv(file_path)
            self.show_info(
                "Zapisano dane", 
                f"Pomyślnie zapisano {len(self.weather_data.records)} rekordów pogodowych do pliku CSV."
            )
            self.status_bar.showMessage(f"Zapisano {len(self.weather_data.records)} rekordów pogodowych do CSV", 3000)
        except Exception as e:
            self.show_error("Błąd zapisywania", f"Nie udało się zapisać danych pogodowych: {str(e)}")
    
    def export_weather_json(self):
        """Eksportuje dane pogodowe do pliku JSON."""
        if not self.weather_data.records:
            self.show_error("Brak danych", "Brak danych pogodowych do zapisania.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Zapisz dane pogodowe", "", "Pliki JSON (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            self.weather_data.save_to_json(file_path)
            self.show_info(
                "Zapisano dane", 
                f"Pomyślnie zapisano {len(self.weather_data.records)} rekordów pogodowych do pliku JSON."
            )
            self.status_bar.showMessage(f"Zapisano {len(self.weather_data.records)} rekordów pogodowych do JSON", 3000)
        except Exception as e:
            self.show_error("Błąd zapisywania", f"Nie udało się zapisać danych pogodowych: {str(e)}")
    
    def show_api_settings(self):
        """Wyświetla dialog konfiguracji API."""
        logger.debug("Wyświetlanie dialogu konfiguracji API")
        dialog = ApiSettingsDialog(self)
        dialog.api_config_saved.connect(self.update_api_client)
        dialog.exec()
    
    def update_api_client(self, config_data):
        """
        Aktualizuje klienta API na podstawie nowych ustawień.
        
        Args:
            config_data: Słownik z nowymi ustawieniami.
        """
        logger.debug("Aktualizacja klienta API")
        api_keys = config_data.get("api_keys", {})
        
        cache_dir = None
        if config_data.get("cache", {}).get("enabled", False):
            cache_dir = config_data.get("cache", {}).get("directory", "")
            if not cache_dir:
                cache_dir = "./cache"
        
        self.api_client = ApiClient(api_keys, cache_dir)
        logger.info(f"Zaktualizowano klienta API z {len(api_keys)} kluczami")
        
        self.status_bar.showMessage("Zaktualizowano konfigurację API", 3000)
    
    def show_about(self):
        """Wyświetla informacje o programie."""
        QMessageBox.about(
            self,
            "O programie",
            """<h2>Rekomendator Tras Turystycznych</h2>
            <p>Wersja: 1.0.0</p>
            <p>System rekomendujący trasy turystyczne w oparciu o preferencje pogodowe.</p>
            <p>© 2025. Wszelkie prawa zastrzeżone.</p>"""
        )
    
    def show_home_page(self):
        """Przejście do strony głównej."""
        logger.debug("Przejście do strony głównej")
        self.stacked_widget.setCurrentWidget(self.home_page)
    
    def show_trail_page(self):
        """Przejście do strony tras."""
        logger.debug("Przejście do strony tras")
        self.stacked_widget.setCurrentWidget(self.trail_page)
    
    def show_weather_page(self):
        """Przejście do strony danych pogodowych."""
        logger.debug("Przejście do strony danych pogodowych")
        self.stacked_widget.setCurrentWidget(self.weather_page)
    
    def show_recommendation_page(self):
        """Przejście do strony rekomendacji."""
        logger.debug("Przejście do strony rekomendacji")
        self.stacked_widget.setCurrentWidget(self.recommendation_page)
    
    def show_error(self, title, message):
        """Wyświetla okno dialogowe z błędem."""
        logger.error(f"{title}: {message}")
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title, message):
        """Wyświetla okno dialogowe z informacją."""
        logger.info(f"{title}: {message}")
        QMessageBox.information(self, title, message)


def run_app():
    """Uruchamia aplikację."""
    logger.info("Uruchamianie aplikacji Rekomendator Tras Turystycznych")
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Styl dla lepszego wyglądu na różnych platformach
    
    # Ustawienie ogólnego stylu aplikacji
    app.setStyleSheet("""
        QWidget {
            background-color: #1e1e1e;
            color: #e0e0e0;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
        }
        QMenuBar {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QMenuBar::item:selected {
            background-color: #3e3e3e;
        }
        QMenu {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QMenu::item:selected {
            background-color: #3e3e3e;
        }
        QStatusBar {
            background-color: #2d2d2d;
            color: #e0e0e0;
        }
        QScrollBar:vertical {
            background-color: #2b2b2b;
            width: 12px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical {
            background-color: #555555;
            min-height: 20px;
            border-radius: 6px;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            border: none;
            background: none;
        }
    """)
    
    window = MainWindow()
    window.show()
    
    try:
        sys.exit(app.exec())
    except Exception as e:
        logger.error(f"Błąd podczas wykonania aplikacji: {str(e)}")
