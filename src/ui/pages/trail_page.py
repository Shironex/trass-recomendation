"""
Strona zarządzania trasami aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QTableWidgetItem,
    QLabel, QGroupBox, QPushButton, QComboBox, QSlider, QFormLayout
)
from PyQt6.QtCore import Qt, QDate

import sys
sys.path.append('.')
from src.ui.components import (
    StyledLabel, BaseButton, PrimaryButton, StyledComboBox,
    StyledDoubleSpinBox, DataTable, CardFrame
)
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
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Grupa filtrów tras
        filter_group = QGroupBox("Filtrowanie danych")
        layout.addWidget(filter_group)
        filter_layout = QFormLayout(filter_group)
        
        # Filtr długości trasy - suwak
        length_filter_layout = QHBoxLayout()
        filter_layout.addRow("Długość trasy (km):", length_filter_layout)
        
        self.filter_min_length = QSlider(Qt.Orientation.Horizontal)
        self.filter_min_length.setRange(0, 50)
        self.filter_min_length.setValue(0)
        length_filter_layout.addWidget(self.filter_min_length)
        
        self.min_length_label = QLabel(f"{self.filter_min_length.value()}")
        length_filter_layout.addWidget(self.min_length_label)
        self.filter_min_length.valueChanged.connect(lambda v: self.min_length_label.setText(f"{v}"))
        
        length_filter_layout.addWidget(QLabel("do"))
        
        self.filter_max_length = QSlider(Qt.Orientation.Horizontal)
        self.filter_max_length.setRange(0, 50)
        self.filter_max_length.setValue(30)
        length_filter_layout.addWidget(self.filter_max_length)
        
        self.max_length_label = QLabel(f"{self.filter_max_length.value()}")
        length_filter_layout.addWidget(self.max_length_label)
        self.filter_max_length.valueChanged.connect(lambda v: self.max_length_label.setText(f"{v}"))
        
        # Filtr przewyższenia
        elevation_filter_layout = QHBoxLayout()
        filter_layout.addRow("Przewyższenie (m):", elevation_filter_layout)
        
        self.filter_min_elevation = QSlider(Qt.Orientation.Horizontal)
        self.filter_min_elevation.setRange(0, 2000)
        self.filter_min_elevation.setValue(0)
        elevation_filter_layout.addWidget(self.filter_min_elevation)
        
        self.min_elevation_label = QLabel(f"{self.filter_min_elevation.value()}")
        elevation_filter_layout.addWidget(self.min_elevation_label)
        self.filter_min_elevation.valueChanged.connect(lambda v: self.min_elevation_label.setText(f"{v}"))
        
        elevation_filter_layout.addWidget(QLabel("do"))
        
        self.filter_max_elevation = QSlider(Qt.Orientation.Horizontal)
        self.filter_max_elevation.setRange(0, 2000)
        self.filter_max_elevation.setValue(1000)
        elevation_filter_layout.addWidget(self.filter_max_elevation)
        
        self.max_elevation_label = QLabel(f"{self.filter_max_elevation.value()}")
        elevation_filter_layout.addWidget(self.max_elevation_label)
        self.filter_max_elevation.valueChanged.connect(lambda v: self.max_elevation_label.setText(f"{v}"))
        
        # Filtr poziomu trudności - suwak
        difficulty_filter_layout = QHBoxLayout()
        filter_layout.addRow("Poziom trudności:", difficulty_filter_layout)
        
        self.filter_min_difficulty = QSlider(Qt.Orientation.Horizontal)
        self.filter_min_difficulty.setRange(1, 5)
        self.filter_min_difficulty.setValue(1)
        difficulty_filter_layout.addWidget(self.filter_min_difficulty)
        
        self.min_difficulty_label = QLabel(f"{self.filter_min_difficulty.value()}")
        difficulty_filter_layout.addWidget(self.min_difficulty_label)
        self.filter_min_difficulty.valueChanged.connect(lambda v: self.min_difficulty_label.setText(f"{v}"))
        
        difficulty_filter_layout.addWidget(QLabel("do"))
        
        self.filter_max_difficulty = QSlider(Qt.Orientation.Horizontal)
        self.filter_max_difficulty.setRange(1, 5)
        self.filter_max_difficulty.setValue(5)
        difficulty_filter_layout.addWidget(self.filter_max_difficulty)
        
        self.max_difficulty_label = QLabel(f"{self.filter_max_difficulty.value()}")
        difficulty_filter_layout.addWidget(self.max_difficulty_label)
        self.filter_max_difficulty.valueChanged.connect(lambda v: self.max_difficulty_label.setText(f"{v}"))
        
        # Filtr regionu
        self.filter_region_combo = QComboBox()
        self.filter_region_combo.addItem("Wszystkie regiony")
        filter_layout.addRow("Region:", self.filter_region_combo)
        
        # Filtr typu terenu
        self.filter_terrain_combo = QComboBox()
        self.filter_terrain_combo.addItem("Wszystkie tereny")
        filter_layout.addRow("Typ terenu:", self.filter_terrain_combo)
        
        # Przyciski filtrowania
        filter_buttons_layout = QHBoxLayout()
        filter_layout.addRow("", filter_buttons_layout)
        
        self.filter_btn = QPushButton("Zastosuj filtry")
        self.filter_btn.clicked.connect(self.apply_filters)
        filter_buttons_layout.addWidget(self.filter_btn)
        
        self.reset_filter_btn = QPushButton("Resetuj filtry")
        self.reset_filter_btn.clicked.connect(self.reset_filters)
        filter_buttons_layout.addWidget(self.reset_filter_btn)
        
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
        
        # Statystyki
        stats_group = QGroupBox("Statystyki")
        layout.addWidget(stats_group)
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_label = QLabel("Brak danych")
        stats_layout.addWidget(self.stats_label)
        
        # Przyciski eksportu i powrotu
        buttons_layout = QHBoxLayout()
        layout.addLayout(buttons_layout)
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("Powrót")
        close_button.clicked.connect(self.main_window.show_home_page)
        buttons_layout.addWidget(close_button)
    
    def _connect_signals(self):
        """Połączenie sygnałów z slotami."""
        # Nie ma już potrzeby definiowania sygnałów, są już dodane w funkcji _setup_ui
        pass
        
    def update_data(self):
        """Aktualizuje wszystkie dane na stronie."""
        self._update_filters()
        self._update_table()
        self._update_stats()
    
    def _update_filters(self):
        """Aktualizuje filtry na podstawie wczytanych danych."""
        # Sprawdzenie, czy są dane
        if not self.main_window.trail_data.trails:
            return
            
        # Aktualizacja regionów
        self.filter_region_combo.clear()
        self.filter_region_combo.addItem("Wszystkie regiony")
        regions = self.main_window.trail_data.get_regions()
        self.filter_region_combo.addItems(regions)
        
        # Aktualizacja typów terenu
        self.filter_terrain_combo.clear()
        self.filter_terrain_combo.addItem("Wszystkie tereny")
        terrain_types = self.main_window.trail_data.get_terrain_types()
        self.filter_terrain_combo.addItems(terrain_types)
        
        # Aktualizacja zakresów długości
        min_len, max_len = self.main_window.trail_data.get_length_range()
        self.filter_min_length.setRange(0, int(max_len) + 1)
        self.filter_max_length.setRange(0, int(max_len) + 1)
        self.filter_max_length.setValue(int(max_len))
        self.min_length_label.setText(f"{self.filter_min_length.value()}")
        self.max_length_label.setText(f"{self.filter_max_length.value()}")
        
        # Znajdowanie maksymalnego przewyższenia
        max_elevation = max(trail.elevation_gain for trail in self.main_window.trail_data.trails)
        self.filter_min_elevation.setRange(0, int(max_elevation) + 100)
        self.filter_max_elevation.setRange(0, int(max_elevation) + 100)
        self.filter_max_elevation.setValue(int(max_elevation))
        self.min_elevation_label.setText(f"{self.filter_min_elevation.value()}")
        self.max_elevation_label.setText(f"{self.filter_max_elevation.value()}")
    
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
            self.stats_label.setText("Brak danych")
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
        
        stats_text = f"Liczba tras: {total}\n"
        stats_text += f"Średnia długość: {avg_length:.1f} km\n"
        stats_text += f"Średnie przewyższenie: {avg_elevation:.0f} m\n"
        
        # Dodanie informacji o najczęstszym regionie
        if regions:
            most_common_region = max(regions.items(), key=lambda x: x[1])
            stats_text += f"\nNajpopularniejszy region: {most_common_region[0]} ({most_common_region[1]} tras)"
        
        self.stats_label.setText(stats_text)
        
    def apply_filters(self):
        """Stosuje filtry do danych o trasach."""
        if not self.main_window.trail_data.trails:
            logger.warn("Próba filtrowania pustych danych o trasach")
            self.main_window.show_error("Ostrzeżenie", "Brak danych do filtrowania!")
            return
        
        # Resetowanie filtrów
        self.main_window.trail_data.filtered_trails = self.main_window.trail_data.trails.copy()
        
        # Filtrowanie po długości
        min_len = self.filter_min_length.value()
        max_len = self.filter_max_length.value()
        self.main_window.trail_data.filtered_trails = [
            trail for trail in self.main_window.trail_data.filtered_trails
            if min_len <= trail.length_km <= max_len
        ]
        
        # Filtrowanie po przewyższeniu
        min_elev = self.filter_min_elevation.value()
        max_elev = self.filter_max_elevation.value()
        self.main_window.trail_data.filtered_trails = [
            trail for trail in self.main_window.trail_data.filtered_trails
            if min_elev <= trail.elevation_gain <= max_elev
        ]
        
        # Filtrowanie po trudności
        min_diff = self.filter_min_difficulty.value()
        max_diff = self.filter_max_difficulty.value()
        self.main_window.trail_data.filtered_trails = [
            trail for trail in self.main_window.trail_data.filtered_trails
            if min_diff <= trail.difficulty <= max_diff
        ]
        
        # Filtrowanie po regionie
        region_text = self.filter_region_combo.currentText()
        if region_text != "Wszystkie regiony":
            self.main_window.trail_data.filtered_trails = [
                trail for trail in self.main_window.trail_data.filtered_trails
                if trail.region == region_text
            ]
        
        # Filtrowanie po terenie
        terrain_text = self.filter_terrain_combo.currentText()
        if terrain_text != "Wszystkie tereny":
            self.main_window.trail_data.filtered_trails = [
                trail for trail in self.main_window.trail_data.filtered_trails
                if trail.terrain_type == terrain_text
            ]
        
        # Aktualizacja tabeli i statystyk
        self._update_table()
        self._update_stats()
        
        # Informacja w statusbarze
        self.main_window.status_bar.showMessage(
            f"Zastosowano filtry: znaleziono {len(self.main_window.trail_data.filtered_trails)} tras",
            3000
        )
    
    def reset_filters(self):
        """Resetuje filtry i przywraca wszystkie dane."""
        if not self.main_window.trail_data.trails:
            return
            
        # Resetowanie kontrolek filtrów
        self.filter_region_combo.setCurrentIndex(0)  # "Wszystkie regiony"
        self.filter_terrain_combo.setCurrentIndex(0)  # "Wszystkie tereny"
        
        # Resetowanie suwaków
        min_len, max_len = self.main_window.trail_data.get_length_range()
        self.filter_min_length.setValue(0)
        self.filter_max_length.setValue(int(max_len))
        
        # Resetowanie przewyższenia
        max_elevation = max(trail.elevation_gain for trail in self.main_window.trail_data.trails)
        self.filter_min_elevation.setValue(0)
        self.filter_max_elevation.setValue(int(max_elevation))
        
        # Resetowanie trudności
        self.filter_min_difficulty.setValue(1)
        self.filter_max_difficulty.setValue(5)
        
        # Resetowanie filtrowanych tras
        self.main_window.trail_data.filtered_trails = self.main_window.trail_data.trails.copy()
        
        # Aktualizacja tabeli
        self._update_table()
        self._update_stats()
        
        # Komunikat
        self.main_window.status_bar.showMessage("Zresetowano filtry", 3000) 