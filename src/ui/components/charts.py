"""
Moduł zawierający komponenty do wyświetlania wykresów i statystyk.
"""

import numpy as np
import pyqtgraph as pg
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox
from PyQt6.QtCore import Qt
from src.utils import logger

class WeatherChart(QWidget):
    """Komponent wyświetlający wykresy danych pogodowych."""
    
    def __init__(self, parent=None):
        """Inicjalizacja komponentu."""
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Główny układ
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Kontrolki
        controls_layout = QHBoxLayout()
        
        # Wybór typu wykresu
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems([
            "Temperatura",
            "Opady",
            "Zachmurzenie",
            "Godziny słoneczne"
        ])
        self.chart_type_combo.currentTextChanged.connect(self._update_chart)
        controls_layout.addWidget(QLabel("Typ wykresu:"))
        controls_layout.addWidget(self.chart_type_combo)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Widget wykresu
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#2d2d2d')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Style dla wykresu
        self.plot_widget.getAxis('left').setTextPen('w')
        self.plot_widget.getAxis('bottom').setTextPen('w')
        
        layout.addWidget(self.plot_widget)
        
        # Domyślne dane
        self.weather_data = []
        
    def set_weather_data(self, weather_data):
        """
        Ustawia dane pogodowe do wyświetlenia.
        
        Args:
            weather_data: Lista obiektów WeatherRecord.
        """
        self.weather_data = sorted(weather_data, key=lambda x: x.date)
        self._update_chart()
        
    def _update_chart(self):
        """Aktualizuje wykres na podstawie wybranych danych."""
        if not self.weather_data:
            return
            
        self.plot_widget.clear()
        chart_type = self.chart_type_combo.currentText()
        
        # Przygotowanie danych
        dates = [record.date.toordinal() for record in self.weather_data]
        
        if chart_type == "Temperatura":
            avg_temp = [record.avg_temp for record in self.weather_data]
            min_temp = [record.min_temp for record in self.weather_data]
            max_temp = [record.max_temp for record in self.weather_data]
            
            # Wykres temperatur
            self.plot_widget.plot(dates, avg_temp, pen='y', name='Średnia')
            self.plot_widget.plot(dates, min_temp, pen='b', name='Minimalna')
            self.plot_widget.plot(dates, max_temp, pen='r', name='Maksymalna')
            self.plot_widget.setLabel('left', 'Temperatura', units='°C')
            
        elif chart_type == "Opady":
            precip = [record.precipitation for record in self.weather_data]
            
            # Wykres opadów
            self.plot_widget.plot(dates, precip, pen='c', fillLevel=0, brush=(0, 255, 255, 50))
            self.plot_widget.setLabel('left', 'Opady', units='mm')
            
        elif chart_type == "Zachmurzenie":
            cloud = [record.cloud_cover for record in self.weather_data]
            
            # Wykres zachmurzenia
            self.plot_widget.plot(dates, cloud, pen='w', fillLevel=0, brush=(255, 255, 255, 30))
            self.plot_widget.setLabel('left', 'Zachmurzenie', units='%')
            
        elif chart_type == "Godziny słoneczne":
            sunshine = [record.sunshine_hours for record in self.weather_data]
            
            # Wykres godzin słonecznych
            self.plot_widget.plot(dates, sunshine, pen='y', fillLevel=0, brush=(255, 255, 0, 30))
            self.plot_widget.setLabel('left', 'Godziny słoneczne', units='h')
        
        # Konfiguracja osi X
        self.plot_widget.setLabel('bottom', 'Data')
        axis = self.plot_widget.getAxis('bottom')
        axis.setTicks([[(date, self.weather_data[i].date.strftime('%Y-%m-%d')) 
                       for i, date in enumerate(dates)]])
        
        logger.debug(f"Zaktualizowano wykres: {chart_type}")


class TrailStatisticsChart(QWidget):
    """Komponent wyświetlający statystyki tras."""
    
    def __init__(self, parent=None):
        """Inicjalizacja komponentu."""
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Główny układ
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Kontrolki
        controls_layout = QHBoxLayout()
        
        # Wybór typu statystyki
        self.stats_type_combo = QComboBox()
        self.stats_type_combo.addItems([
            "Długość tras",
            "Przewyższenie",
            "Poziom trudności",
            "Typ terenu"
        ])
        self.stats_type_combo.currentTextChanged.connect(self._update_chart)
        controls_layout.addWidget(QLabel("Typ statystyki:"))
        controls_layout.addWidget(self.stats_type_combo)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Widget wykresu
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('#2d2d2d')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        
        # Style dla wykresu
        self.plot_widget.getAxis('left').setTextPen('w')
        self.plot_widget.getAxis('bottom').setTextPen('w')
        
        layout.addWidget(self.plot_widget)
        
        # Domyślne dane
        self.trail_data = []
        
    def set_trail_data(self, trail_data):
        """
        Ustawia dane o trasach do wyświetlenia.
        
        Args:
            trail_data: Lista obiektów TrailRecord.
        """
        self.trail_data = trail_data
        self._update_chart()
        
    def _update_chart(self):
        """Aktualizuje wykres na podstawie wybranych danych."""
        if not self.trail_data:
            return
            
        self.plot_widget.clear()
        stats_type = self.stats_type_combo.currentText()
        
        if stats_type == "Długość tras":
            # Histogram długości tras
            lengths = [trail.length_km for trail in self.trail_data]
            y, x = np.histogram(lengths, bins=20)
            self.plot_widget.plot(x, y, stepMode=True, fillLevel=0, brush=(0, 255, 0, 50))
            self.plot_widget.setLabel('left', 'Liczba tras')
            self.plot_widget.setLabel('bottom', 'Długość', units='km')
            
        elif stats_type == "Przewyższenie":
            # Wykres przewyższeń
            elevations = [trail.elevation_gain for trail in self.trail_data]
            y, x = np.histogram(elevations, bins=20)
            self.plot_widget.plot(x, y, stepMode=True, fillLevel=0, brush=(255, 165, 0, 50))
            self.plot_widget.setLabel('left', 'Liczba tras')
            self.plot_widget.setLabel('bottom', 'Przewyższenie', units='m')
            
        elif stats_type == "Poziom trudności":
            # Wykres słupkowy poziomów trudności
            difficulties = [trail.difficulty for trail in self.trail_data]
            unique_diff = sorted(set(difficulties))
            counts = [difficulties.count(d) for d in unique_diff]
            
            bargraph = pg.BarGraphItem(x=unique_diff, height=counts, width=0.6, brush='b')
            self.plot_widget.addItem(bargraph)
            self.plot_widget.setLabel('left', 'Liczba tras')
            self.plot_widget.setLabel('bottom', 'Poziom trudności')
            
        elif stats_type == "Typ terenu":
            # Wykres słupkowy typów terenu
            terrain_types = [trail.terrain_type for trail in self.trail_data]
            unique_types = sorted(set(terrain_types))
            counts = [terrain_types.count(t) for t in unique_types]
            
            bargraph = pg.BarGraphItem(x=range(len(unique_types)), height=counts, width=0.6, brush='r')
            self.plot_widget.addItem(bargraph)
            self.plot_widget.setLabel('left', 'Liczba tras')
            
            axis = self.plot_widget.getAxis('bottom')
            axis.setTicks([[(i, t) for i, t in enumerate(unique_types)]])
            
        logger.debug(f"Zaktualizowano statystyki: {stats_type}") 