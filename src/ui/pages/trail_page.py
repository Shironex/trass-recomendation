"""
Strona zarządzania trasami aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidgetItem,
    QLabel, QPushButton, QSplitter
)
from PyQt6.QtCore import Qt

import sys
sys.path.append('.')
from src.ui.components import (
    StyledLabel, DataTable, FilterGroup, StatsDisplay,
    TrailStatisticsChart
)
from src.ui.components.chart_dialog import ChartDialog
from src.utils import logger


class TrailPage(QWidget):
    """Strona zarządzania trasami."""
    
    def __init__(self, parent=None):
        """Inicjalizacja strony zarządzania trasami."""
        super().__init__(parent)
        self.main_window = parent
        logger.debug("Inicjalizacja strony zarządzania trasami")
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Główny układ
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Tytuł strony
        title_label = StyledLabel("Zarządzanie Trasami", is_title=True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Grupa filtrów tras
        self.filter_group = FilterGroup("Filtrowanie danych", self)
        self.filter_group.filterApplied.connect(self.apply_filters)
        self.filter_group.filterReset.connect(self.reset_filters)
        layout.addWidget(self.filter_group)
        
        # Filtr długości trasy - suwak
        self.filter_min_length, self.filter_max_length = self.filter_group.add_slider_filter(
            "length",
            "Długość trasy",
            0, 50, 0, 30,
            " km"
        )
        
        # Filtr przewyższenia
        self.filter_min_elevation, self.filter_max_elevation = self.filter_group.add_slider_filter(
            "elevation",
            "Przewyższenie",
            0, 2000, 0, 1000,
            " m"
        )
        
        # Filtr poziomu trudności - suwak
        self.filter_min_difficulty, self.filter_max_difficulty = self.filter_group.add_slider_filter(
            "difficulty",
            "Poziom trudności",
            1, 5, 1, 5
        )
        
        # Filtr regionu
        self.filter_region_combo = self.filter_group.add_combo_filter(
            "region", "Region"
        )
        
        # Filtr typu terenu
        self.filter_terrain_combo = self.filter_group.add_combo_filter(
            "terrain", "Typ terenu"
        )
        
        # Przyciski filtrowania
        self.filter_group.add_buttons_row()
        
        # Tabela danych
        table_label = QLabel("Dane tras:")
        layout.addWidget(table_label)
        
        # Tabela tras
        self.trail_table = DataTable()
        self.trail_table.setColumnCount(6)
        self.trail_table.setHorizontalHeaderLabels([
            "Nazwa", "Region", "Długość (km)", "Trudność", "Teren", "Przewyższenie (m)"
        ])
        layout.addWidget(self.trail_table)
        
        # Statystyki tekstowe
        self.stats_display = StatsDisplay("Statystyki", self)
        layout.addWidget(self.stats_display)
        
        # Przyciski
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)
        
        # Przycisk wykresu
        chart_button = QPushButton("Pokaż statystyki graficzne")
        chart_button.clicked.connect(self.show_chart_dialog)
        buttons_layout.addWidget(chart_button)
        
        buttons_layout.addStretch()
        
        # Przycisk powrotu
        close_button = QPushButton("Powrót")
        close_button.clicked.connect(self.main_window.show_home_page)
        buttons_layout.addWidget(close_button)
        
        # Ukryty wykres do przechowywania danych
        self.trail_chart = TrailStatisticsChart()
        self.trail_chart.hide()
    
    def _connect_signals(self):
        """Połączenie sygnałów z slotami."""
        # Nie ma już potrzeby definiowania sygnałów, są już dodane w funkcji _setup_ui
        pass
        
    def update_data(self):
        """Aktualizuje wszystkie dane na stronie."""
        self._update_filters()
        self._update_table()
        self._update_stats()
        self.trail_chart.set_trail_data(self.main_window.trail_data.trails)
    
    def _update_filters(self):
        """Aktualizuje filtry na podstawie wczytanych danych."""
        # Sprawdzenie, czy są dane
        if not self.main_window.trail_data.trails:
            return
            
        # Aktualizacja regionów
        regions = self.main_window.trail_data.get_regions()
        self.filter_region_combo.clear()
        self.filter_region_combo.addItem("Wszystkie regiony")
        self.filter_region_combo.addItems(regions)
        
        # Aktualizacja typów terenu
        terrain_types = self.main_window.trail_data.get_terrain_types()
        self.filter_terrain_combo.clear()
        self.filter_terrain_combo.addItem("Wszystkie tereny")
        self.filter_terrain_combo.addItems(terrain_types)
        
        # Aktualizacja zakresów długości
        min_len, max_len = self.main_window.trail_data.get_length_range()
        self.filter_min_length.setRange(0, int(max_len) + 1)
        self.filter_max_length.setRange(0, int(max_len) + 1)
        self.filter_max_length.setValue(int(max_len))
        
        # Znajdowanie maksymalnego przewyższenia
        max_elevation = max(trail.elevation_gain for trail in self.main_window.trail_data.trails)
        self.filter_min_elevation.setRange(0, int(max_elevation) + 100)
        self.filter_max_elevation.setRange(0, int(max_elevation) + 100)
        self.filter_max_elevation.setValue(int(max_elevation))
    
    def _update_table(self):
        """Aktualizuje tabelę z trasami."""
        trails = self.main_window.trail_data.filtered_trails
        self.trail_table.setRowCount(len(trails))
        
        for i, trail in enumerate(trails):
            # Nazwa
            self.trail_table.setItem(i, 0, QTableWidgetItem(trail.name))
            # Region
            self.trail_table.setItem(i, 1, QTableWidgetItem(trail.region))
            # Długość
            self.trail_table.setItem(i, 2, QTableWidgetItem(f"{trail.length_km:.1f}"))
            # Trudność
            self.trail_table.setItem(i, 3, QTableWidgetItem(str(trail.difficulty)))
            # Teren
            self.trail_table.setItem(i, 4, QTableWidgetItem(trail.terrain_type))
            # Przewyższenie
            self.trail_table.setItem(i, 5, QTableWidgetItem(f"{trail.elevation_gain:.0f}"))
    
    def _update_stats(self):
        """Aktualizuje statystyki na podstawie filtrowanych danych."""
        if not self.main_window.trail_data.filtered_trails:
            self.stats_display.update_stats("Brak danych")
            return
            
        trails = self.main_window.trail_data.filtered_trails
        total = len(trails)
        avg_length = sum(t.length_km for t in trails) / total if total > 0 else 0
        avg_elevation = sum(t.elevation_gain for t in trails) / total if total > 0 else 0
        
        regions = {}
        difficulties = {}
        terrain_types = {}
        
        for trail in trails:
            regions[trail.region] = regions.get(trail.region, 0) + 1
            difficulties[trail.difficulty] = difficulties.get(trail.difficulty, 0) + 1
            terrain_types[trail.terrain_type] = terrain_types.get(trail.terrain_type, 0) + 1
        
        stats_dict = {
            "Liczba tras": total,
            "Średnia długość": f"{avg_length:.1f} km",
            "Średnie przewyższenie": f"{avg_elevation:.0f} m"
        }
        
        # Dodanie informacji o najczęstszym regionie
        if regions:
            most_common_region = max(regions.items(), key=lambda x: x[1])
            stats_dict["Najpopularniejszy region"] = f"{most_common_region[0]} ({most_common_region[1]} tras)"
        
        self.stats_display.set_stats(stats_dict)
        
    def apply_filters(self):
        """Stosuje filtry do danych."""
        if not self.main_window.trail_data.trails:
            self.main_window.show_error("Brak danych", "Brak danych tras do filtrowania.")
            return
            
        # Resetowanie filtrowanych tras
        self.main_window.trail_data.filtered_trails = self.main_window.trail_data.trails.copy()
        
        # Filtrowanie po regionie
        region = self.filter_region_combo.currentText()
        if region != "Wszystkie regiony":
            self.main_window.trail_data.filtered_trails = [
                trail for trail in self.main_window.trail_data.filtered_trails
                if trail.region == region
            ]
        
        # Filtrowanie po typie terenu
        terrain = self.filter_terrain_combo.currentText()
        if terrain != "Wszystkie tereny":
            self.main_window.trail_data.filtered_trails = [
                trail for trail in self.main_window.trail_data.filtered_trails
                if trail.terrain_type == terrain
            ]
        
        # Filtrowanie po długości
        min_length = self.filter_min_length.value()
        max_length = self.filter_max_length.value()
        self.main_window.trail_data.filtered_trails = [
            trail for trail in self.main_window.trail_data.filtered_trails
            if min_length <= trail.length_km <= max_length
        ]
        
        # Filtrowanie po przewyższeniu
        min_elevation = self.filter_min_elevation.value()
        max_elevation = self.filter_max_elevation.value()
        self.main_window.trail_data.filtered_trails = [
            trail for trail in self.main_window.trail_data.filtered_trails
            if min_elevation <= trail.elevation_gain <= max_elevation
        ]
        
        # Filtrowanie po trudności
        min_difficulty = self.filter_min_difficulty.value()
        max_difficulty = self.filter_max_difficulty.value()
        self.main_window.trail_data.filtered_trails = [
            trail for trail in self.main_window.trail_data.filtered_trails
            if min_difficulty <= trail.difficulty <= max_difficulty
        ]
        
        # Aktualizacja widoku
        self._update_table()
        self._update_stats()
        self.trail_chart.set_trail_data(self.main_window.trail_data.filtered_trails)
        
        # Informacja o liczbie wyników
        self.main_window.status_bar.showMessage(
            f"Zastosowano filtry: znaleziono {len(self.main_window.trail_data.filtered_trails)} tras", 
            3000
        )
    
    def reset_filters(self):
        """Resetuje filtry i przywraca wszystkie dane."""
        if not self.main_window.trail_data.trails:
            return
            
        # Reset filtra regionu
        self.filter_region_combo.setCurrentText("Wszystkie regiony")
        
        # Reset filtra terenu
        self.filter_terrain_combo.setCurrentText("Wszystkie tereny")
        
        # Reset filtra długości
        min_len, max_len = self.main_window.trail_data.get_length_range()
        self.filter_min_length.setValue(0)
        self.filter_max_length.setValue(int(max_len))
        
        # Reset filtra przewyższenia
        max_elevation = max(trail.elevation_gain for trail in self.main_window.trail_data.trails)
        self.filter_min_elevation.setValue(0)
        self.filter_max_elevation.setValue(int(max_elevation))
        
        # Reset filtra trudności
        self.filter_min_difficulty.setValue(1)
        self.filter_max_difficulty.setValue(5)
        
        # Resetowanie filtrowanych tras
        self.main_window.trail_data.filtered_trails = self.main_window.trail_data.trails.copy()
        
        # Aktualizacja widoku
        self._update_table()
        self._update_stats()
        self.trail_chart.set_trail_data(self.main_window.trail_data.trails)
        
        # Komunikat o zresetowaniu
        self.main_window.status_bar.showMessage("Zresetowano filtry", 3000) 
    
    def show_chart_dialog(self):
        """Wyświetla okno dialogowe z wykresem statystyk."""
        if not self.main_window.trail_data.trails:
            self.main_window.show_error("Brak danych", "Brak danych do wyświetlenia na wykresie.")
            return
            
        dialog = ChartDialog("trail", self)
        dialog.set_data(self.main_window.trail_data.filtered_trails)
        dialog.exec() 