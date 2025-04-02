"""
Strona zarządzania trasami aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt

import sys
sys.path.append('.')
from src.ui.components import (
    StyledLabel, BaseButton, PrimaryButton, StyledComboBox,
    StyledDoubleSpinBox, DataTable, CardFrame
)
from src.core.trail_data import TrailData


class TrailPage(QWidget):
    """Strona zarządzania trasami."""
    
    def __init__(self, parent=None):
        """Inicjalizacja strony zarządzania trasami."""
        super().__init__(parent)
        self.main_window = parent
        self.trail_data = TrailData()
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Główny układ
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Górny pasek z tytułem i przyciskiem powrotu
        top_bar = QHBoxLayout()
        
        # Przycisk powrotu
        self.back_btn = BaseButton("Powrót do menu głównego")
        top_bar.addWidget(self.back_btn)
        
        # Tytuł
        title = StyledLabel("Zarządzanie Trasami", is_title=True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_bar.addWidget(title)
        top_bar.setStretchFactor(self.back_btn, 1)
        top_bar.setStretchFactor(title, 3)
        
        layout.addLayout(top_bar)
        
        # Układ dwukolumnowy
        content_layout = QHBoxLayout()
        
        # Lewa kolumna - filtry
        left_column = QVBoxLayout()
        
        # Karta filtrów
        filter_card = CardFrame()
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setSpacing(15)
        
        # Tytuł filtrów
        filter_title = StyledLabel("Filtry")
        font = filter_title.font()
        font.setBold(True)
        filter_title.setFont(font)
        filter_layout.addWidget(filter_title)
        
        # Długość trasy
        length_layout = QVBoxLayout()
        length_layout.addWidget(StyledLabel("Długość trasy (km):"))
        
        length_inputs = QHBoxLayout()
        
        length_inputs.addWidget(StyledLabel("Min:"))
        self.min_length = StyledDoubleSpinBox()
        self.min_length.setRange(0, 1000)
        length_inputs.addWidget(self.min_length)
        
        length_inputs.addWidget(StyledLabel("Max:"))
        self.max_length = StyledDoubleSpinBox()
        self.max_length.setRange(0, 1000)
        self.max_length.setValue(1000)
        length_inputs.addWidget(self.max_length)
        
        length_layout.addLayout(length_inputs)
        filter_layout.addLayout(length_layout)
        
        # Poziom trudności
        difficulty_layout = QVBoxLayout()
        difficulty_layout.addWidget(StyledLabel("Poziom trudności:"))
        self.difficulty = StyledComboBox()
        self.difficulty.addItem("Wszystkie")
        difficulty_layout.addWidget(self.difficulty)
        filter_layout.addLayout(difficulty_layout)
        
        # Region
        region_layout = QVBoxLayout()
        region_layout.addWidget(StyledLabel("Region:"))
        self.region = StyledComboBox()
        self.region.addItem("Wszystkie")
        region_layout.addWidget(self.region)
        filter_layout.addLayout(region_layout)
        
        # Przycisk filtrowania
        self.filter_btn = PrimaryButton("Zastosuj filtry")
        filter_layout.addWidget(self.filter_btn)
        
        # Dodanie karty filtrów do lewej kolumny
        left_column.addWidget(filter_card)
        
        # Przyciski
        buttons_layout = QVBoxLayout()
        
        # Przyciski wczytywania
        self.load_btn = BaseButton("Wczytaj dane o trasach")
        buttons_layout.addWidget(self.load_btn)
        
           # Przyciski operacji na danych
        operations_card = CardFrame()
        operations_layout = QVBoxLayout(operations_card)
        operations_layout.setContentsMargins(15, 15, 15, 15)
        operations_layout.setSpacing(10)
        
        # Nagłówek operacji
        operations_header = StyledLabel("Operacje na danych")
        font = operations_header.font()
        font.setBold(True)
        operations_header.setFont(font)
        operations_layout.addWidget(operations_header)
        
        # Przycisk wczytywania danych
        self.load_btn = BaseButton("Wczytaj dane pogodowe")
        self.load_btn.setMinimumHeight(35)
        operations_layout.addWidget(self.load_btn)
        
        # Przyciski eksportu
        export_layout = QHBoxLayout()
        export_layout.setSpacing(10)
        
        self.export_csv_btn = BaseButton("Eksportuj do CSV")
        self.export_json_btn = BaseButton("Eksportuj do JSON")
        self.export_csv_btn.setMinimumHeight(35)
        self.export_json_btn.setMinimumHeight(35)
        
        export_layout.addWidget(self.export_csv_btn)
        export_layout.addWidget(self.export_json_btn)
        operations_layout.addLayout(export_layout)
        
        # Dodanie karty operacji do lewej kolumny
        left_column.addWidget(operations_card)
        left_column.addStretch()
        
        # Prawa kolumna - tabela z trasami
        right_column = QVBoxLayout()
        
        # Tabela tras
        self.trail_table = DataTable()
        self.trail_table.setColumnCount(6)
        self.trail_table.setHorizontalHeaderLabels([
            "Nazwa", "Region", "Długość (km)", "Trudność", "Teren", "Przewyższenie (m)"
        ])
        
        right_column.addWidget(self.trail_table)
        
        # Dodanie kolumn do głównego układu
        content_layout.addLayout(left_column, 1)
        content_layout.addLayout(right_column, 2)
        
        layout.addLayout(content_layout)
    
    def _connect_signals(self):
        """Połączenie sygnałów z slotami."""
        self.load_btn.clicked.connect(self.load_data)
        self.filter_btn.clicked.connect(self.apply_filters)
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        self.export_json_btn.clicked.connect(self.export_to_json)
        
        if self.main_window:
            self.back_btn.clicked.connect(self.main_window.show_home_page)
    
    def load_data(self):
        """Wczytuje dane o trasach z pliku."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Wczytaj dane o trasach",
            "",
            "Pliki CSV (*.csv);;Pliki JSON (*.json)"
        )
        
        if not filepath:
            return
        
        try:
            if filepath.endswith('.csv'):
                self.trail_data.load_from_csv(filepath)
            else:
                self.trail_data.load_from_json(filepath)
            
            # Aktualizacja filtrów
            self._update_filters()
            
            # Aktualizacja tabeli
            self._update_table()
            
            QMessageBox.information(self, "Sukces", "Dane zostały wczytane pomyślnie!")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wczytać danych: {str(e)}")
    
    def _update_filters(self):
        """Aktualizuje filtry na podstawie wczytanych danych."""
        # Aktualizacja poziomu trudności
        self.difficulty.clear()
        self.difficulty.addItem("Wszystkie")
        for level in self.trail_data.get_difficulty_levels():
            self.difficulty.addItem(str(level))
        
        # Aktualizacja regionów
        self.region.clear()
        self.region.addItem("Wszystkie")
        for region in self.trail_data.get_regions():
            self.region.addItem(region)
        
        # Aktualizacja zakresów długości
        min_len, max_len = self.trail_data.get_length_range()
        self.min_length.setRange(0, max_len)
        self.max_length.setRange(0, max_len)
        self.max_length.setValue(max_len)
    
    def _update_table(self):
        """Aktualizuje tabelę z trasami."""
        trails = self.trail_data.filtered_trails
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
    
    def apply_filters(self):
        """Stosuje filtry do danych o trasach."""
        if not self.trail_data.trails:
            QMessageBox.warning(self, "Ostrzeżenie", "Brak danych do filtrowania!")
            return
        
        # Resetowanie filtrów
        self.trail_data.filtered_trails = self.trail_data.trails.copy()
        
        # Filtrowanie po długości
        min_len = self.min_length.value()
        max_len = self.max_length.value()
        if min_len > 0 or max_len < self.max_length.maximum():
            self.trail_data.filter_by_length(min_len, max_len)
        
        # Filtrowanie po trudności
        difficulty_text = self.difficulty.currentText()
        if difficulty_text != "Wszystkie":
            self.trail_data.filter_by_difficulty(int(difficulty_text))
        
        # Filtrowanie po regionie
        region_text = self.region.currentText()
        if region_text != "Wszystkie":
            self.trail_data.filter_by_region(region_text)
        
        # Aktualizacja tabeli
        self._update_table()
    
    def export_to_csv(self):
        """Eksportuje dane do pliku CSV."""
        if not self.trail_data.filtered_trails:
            QMessageBox.warning(self, "Ostrzeżenie", "Brak danych do eksportu!")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Eksportuj do CSV",
            "",
            "Pliki CSV (*.csv)"
        )
        
        if not filepath:
            return
        
        try:
            self.trail_data.save_to_csv(filepath)
            QMessageBox.information(self, "Sukces", "Dane zostały zapisane pomyślnie!")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać danych: {str(e)}")
    
    def export_to_json(self):
        """Eksportuje dane do pliku JSON."""
        if not self.trail_data.filtered_trails:
            QMessageBox.warning(self, "Ostrzeżenie", "Brak danych do eksportu!")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Eksportuj do JSON",
            "",
            "Pliki JSON (*.json)"
        )
        
        if not filepath:
            return
        
        try:
            self.trail_data.save_to_json(filepath)
            QMessageBox.information(self, "Sukces", "Dane zostały zapisane pomyślnie!")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się zapisać danych: {str(e)}") 