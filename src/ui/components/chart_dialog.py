"""
Moduł zawierający okna dialogowe do wyświetlania wykresów.
"""

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from src.ui.components.charts import WeatherChart, TrailStatisticsChart


class ChartDialog(QDialog):
    """Okno dialogowe do wyświetlania wykresów."""
    
    def __init__(self, chart_type="weather", parent=None):
        """
        Inicjalizacja okna dialogowego.
        
        Args:
            chart_type: Typ wykresu ("weather" lub "trail").
            parent: Rodzic widgetu.
        """
        super().__init__(parent)
        self.chart_type = chart_type
        self._setup_ui()
        
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Ustawienia okna
        self.setWindowTitle("Wizualizacja danych")
        self.setMinimumSize(800, 600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowMaximizeButtonHint)
        
        # Główny układ
        layout = QVBoxLayout(self)
        
        # Utworzenie odpowiedniego wykresu
        if self.chart_type == "weather":
            self.chart = WeatherChart()
        else:
            self.chart = TrailStatisticsChart()
        
        layout.addWidget(self.chart)
        
        # Przycisk zamknięcia
        close_button = QPushButton("Zamknij")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
    def set_data(self, data):
        """
        Ustawia dane do wyświetlenia na wykresie.
        
        Args:
            data: Dane do wyświetlenia (lista obiektów WeatherRecord lub TrailRecord).
        """
        if self.chart_type == "weather":
            self.chart.set_weather_data(data)
        else:
            self.chart.set_trail_data(data) 