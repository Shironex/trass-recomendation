"""
Główny moduł interfejsu użytkownika aplikacji Rekomendator Tras Turystycznych.
"""

import sys
sys.path.append('.')
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from src.ui.pages.home_page import HomePage
from src.ui.pages.trail_page import TrailPage
from src.ui.pages.weather_page import WeatherPage
from src.ui.pages.recommendation_page import RecommendationPage


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
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Centralny widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Główny układ
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Stos widgetów na strony
        self.stacked_widget = QStackedWidget()
        
        # Tworzenie stron
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
    
    def show_home_page(self):
        """Przejście do strony głównej."""
        self.stacked_widget.setCurrentWidget(self.home_page)
    
    def show_trail_page(self):
        """Przejście do strony tras."""
        self.stacked_widget.setCurrentWidget(self.trail_page)
    
    def show_weather_page(self):
        """Przejście do strony danych pogodowych."""
        self.stacked_widget.setCurrentWidget(self.weather_page)
    
    def show_recommendation_page(self):
        """Przejście do strony rekomendacji."""
        self.stacked_widget.setCurrentWidget(self.recommendation_page)
    
    def show_error(self, title, message):
        """Wyświetla okno dialogowe z błędem."""
        QMessageBox.critical(self, title, message)
    
    def show_info(self, title, message):
        """Wyświetla okno dialogowe z informacją."""
        QMessageBox.information(self, title, message)


def run_app():
    """Uruchamia aplikację."""
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
    
    sys.exit(app.exec())
