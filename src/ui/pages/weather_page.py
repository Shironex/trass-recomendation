"""
Strona zarządzania danymi pogodowymi aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox,
    QTableWidgetItem, QGridLayout
)
from PyQt6.QtCore import Qt

import sys
sys.path.append('.')
from src.ui.components import (
    StyledLabel, BaseButton, PrimaryButton, StyledComboBox,
    StyledDateEdit, CardFrame, StyledDoubleSpinBox, DataTable
)
from src.core.weather_data import WeatherData
from src.utils import logger


class WeatherPage(QWidget):
    """Strona zarządzania danymi pogodowymi."""
    
    def __init__(self, parent=None):
        """Inicjalizacja strony zarządzania danymi pogodowymi."""
        super().__init__(parent)
        self.main_window = parent
        self.weather_data = WeatherData()
        logger.debug("Inicjalizacja strony zarządzania danymi pogodowymi")
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Główny układ
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)
        
        # Inicjalizacja układu głównego
        self.content_layout = QHBoxLayout()
        self.left_column = QVBoxLayout()
        self.right_column = QVBoxLayout()
        
        # Konfiguracja poszczególnych części UI
        self._setup_top_bar()
        self._setup_filters()
        self._setup_statistics()
        self._setup_operations()
        self._setup_data_table()
        
        # Finalizacja układu
        self.content_layout.addLayout(self.left_column, 1)
        self.content_layout.addLayout(self.right_column, 2)
        self.layout.addLayout(self.content_layout)
    
    def _setup_top_bar(self):
        """Konfiguracja górnego paska z tytułem i przyciskiem powrotu."""
        # Górny pasek z tytułem i przyciskiem powrotu
        top_bar = QHBoxLayout()
        
        # Przycisk powrotu
        self.back_btn = BaseButton("Powrót do menu głównego")
        top_bar.addWidget(self.back_btn)
        
        # Tytuł
        title = StyledLabel("Dane Pogodowe", is_title=True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_bar.addWidget(title)
        top_bar.setStretchFactor(self.back_btn, 1)
        top_bar.setStretchFactor(title, 3)
        
        self.layout.addLayout(top_bar)
    
    def _setup_filters(self):
        """Konfiguracja filtrów danych pogodowych."""
        # Karta filtrów
        filter_card = CardFrame()
        filter_layout = QVBoxLayout(filter_card)
        filter_layout.setContentsMargins(15, 15, 15, 15)
        filter_layout.setSpacing(10)
        
        # Tytuł filtrów
        filter_title = StyledLabel("Filtry")
        font = filter_title.font()
        font.setBold(True)
        filter_title.setFont(font)
        filter_layout.addWidget(filter_title)
        
        # Kontrolka wyboru lokalizacji
        loc_layout = QVBoxLayout()
        
        self.location = StyledComboBox()
        self.location.addItem("Wszystkie")
        loc_layout.addWidget(self.location)
        filter_layout.addLayout(loc_layout)
        
        # Kontrolki wyboru zakresu dat
        date_layout = QVBoxLayout()
        date_layout.setSpacing(5)
        date_label = StyledLabel("Zakres dat:")
        date_layout.addWidget(date_label)
        
        date_range = QHBoxLayout()
        date_range.setSpacing(10)
        
        start_date_layout = QVBoxLayout()
        start_date_layout.setSpacing(3)
        start_label = StyledLabel("Od:")
        start_date_layout.addWidget(start_label)
        self.start_date = StyledDateEdit()
        start_date_layout.addWidget(self.start_date)
        date_range.addLayout(start_date_layout)
        
        end_date_layout = QVBoxLayout()
        end_date_layout.setSpacing(3)
        end_label = StyledLabel("Do:")
        end_date_layout.addWidget(end_label)
        self.end_date = StyledDateEdit()
        end_date_layout.addWidget(self.end_date)
        date_range.addLayout(end_date_layout)
        
        date_layout.addLayout(date_range)
        filter_layout.addLayout(date_layout)
        
        # Minimalna temperatura
        temp_layout = QHBoxLayout()
        temp_layout.setSpacing(5)
        temp_label = StyledLabel("Min. temperatura:")
        temp_layout.addWidget(temp_label)
        
        self.min_pref_temp = StyledDoubleSpinBox()
        self.min_pref_temp.setRange(-30, 40)
        self.min_pref_temp.setValue(15)
        self.min_pref_temp.setSuffix(" °C")
        self.min_pref_temp.setMinimumHeight(30)
        temp_layout.addWidget(self.min_pref_temp)
        filter_layout.addLayout(temp_layout)
        
        # Maksymalne opady
        precip_layout = QHBoxLayout()
        precip_layout.setSpacing(5)
        precip_label = StyledLabel("Maks. opady:")
        precip_layout.addWidget(precip_label)
        
        self.max_precip = StyledDoubleSpinBox()
        self.max_precip.setRange(0, 100)
        self.max_precip.setValue(10)
        self.max_precip.setSuffix(" mm")
        self.max_precip.setMinimumHeight(30)
        precip_layout.addWidget(self.max_precip)
        filter_layout.addLayout(precip_layout)
        
        # Minimalne nasłonecznienie
        sunshine_layout = QHBoxLayout()
        sunshine_layout.setSpacing(5)
        sunshine_label = StyledLabel("Min. nasłonecznienie:")
        sunshine_layout.addWidget(sunshine_label)
        
        self.min_sunshine = StyledDoubleSpinBox()
        self.min_sunshine.setRange(0, 24)
        self.min_sunshine.setValue(5)
        self.min_sunshine.setSuffix(" h")
        self.min_sunshine.setMinimumHeight(30)
        sunshine_layout.addWidget(self.min_sunshine)
        filter_layout.addLayout(sunshine_layout)
        
        # Przycisk zastosowania filtrów
        self.filter_btn = PrimaryButton("Zastosuj filtry")
        self.filter_btn.setMinimumHeight(35)
        filter_layout.addWidget(self.filter_btn)
        
        # Dodanie karty filtrów do lewej kolumny
        self.left_column.addWidget(filter_card)
    
    def _setup_statistics(self):
        """Konfiguracja karty statystyk."""
        # Karta statystyk
        stats_card = CardFrame()
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(15, 15, 15, 15)
        stats_layout.setSpacing(10)
        
        # Nagłówek statystyk
        stats_header = StyledLabel("Statystyki pogodowe")
        font = stats_header.font()
        font.setBold(True)
        stats_header.setFont(font)
        stats_layout.addWidget(stats_header)
        
        # Grid ze statystykami
        stats_grid = QGridLayout()
        stats_grid.setSpacing(10)
        stats_grid.setColumnStretch(0, 1)
        stats_grid.setColumnStretch(1, 1)
        
        # Etykiety statystyk
        stats_grid.addWidget(StyledLabel("Średnia temperatura:"), 0, 0)
        stats_grid.addWidget(StyledLabel("Suma opadów:"), 1, 0)
        stats_grid.addWidget(StyledLabel("Liczba dni słonecznych:"), 2, 0)
        
        # Wartości statystyk
        self.avg_temp = StyledLabel("0.0 °C")
        self.avg_temp.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.total_precip = StyledLabel("0.0 mm")
        self.total_precip.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.sunny_days = StyledLabel("0")
        self.sunny_days.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        stats_grid.addWidget(self.avg_temp, 0, 1)
        stats_grid.addWidget(self.total_precip, 1, 1)
        stats_grid.addWidget(self.sunny_days, 2, 1)
        
        stats_layout.addLayout(stats_grid)
        
        # Dodanie karty statystyk do lewej kolumny
        self.left_column.addWidget(stats_card)
    
    def _setup_operations(self):
        """Konfiguracja karty operacji na danych."""
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
        self.left_column.addWidget(operations_card)
        self.left_column.addStretch()
    
    def _setup_data_table(self):
        """Konfiguracja tabeli danych pogodowych."""
        # Tabela danych pogodowych
        self.weather_table = DataTable()
        self.weather_table.setColumnCount(7)
        self.weather_table.setHorizontalHeaderLabels([
            "Data", "Lokalizacja", "Śr. temp. (°C)", "Min. temp. (°C)", 
            "Maks. temp. (°C)", "Opady (mm)", "Nasł. (h)"
        ])
        
        self.right_column.addWidget(self.weather_table)
        
        # Status label pod tabelą
        self.status_label = StyledLabel("")
        self.right_column.addWidget(self.status_label)
    
    def _connect_signals(self):
        """Połączenie sygnałów z slotami."""
        self.load_btn.clicked.connect(self.load_data)
        self.filter_btn.clicked.connect(self.apply_filters)
        self.export_csv_btn.clicked.connect(self.export_to_csv)
        self.export_json_btn.clicked.connect(self.export_to_json)
        
        # Aktualizacja statystyk przy zmianie preferencji
        self.min_pref_temp.valueChanged.connect(self._update_statistics)
        self.max_precip.valueChanged.connect(self._update_statistics)
        self.min_sunshine.valueChanged.connect(self._update_statistics)
        
        # Aktualizacja przy zmianie lokalizacji lub daty
        self.location.currentIndexChanged.connect(self._update_statistics)
        self.start_date.dateChanged.connect(self._update_statistics)
        self.end_date.dateChanged.connect(self._update_statistics)
        
        if self.main_window:
            self.back_btn.clicked.connect(self.main_window.show_home_page)
    
    def load_data(self):
        """Wczytuje dane pogodowe z pliku."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Wczytaj dane pogodowe",
            "",
            "Pliki CSV (*.csv);;Pliki JSON (*.json)"
        )
        
        if not filepath:
            return
        
        try:
            if filepath.endswith('.csv'):
                self.weather_data.load_from_csv(filepath)
            else:
                self.weather_data.load_from_json(filepath)
            
            # Aktualizacja kontrolek filtrów
            self._update_filters()
            
            # Aktualizacja tabeli
            self._update_table()
            
            logger.info(f"Dane pogodowe wczytane pomyślnie z pliku {filepath}")
            QMessageBox.information(self, "Sukces", "Dane zostały wczytane pomyślnie!")
        except Exception as e:
            logger.error(f"Błąd wczytywania danych pogodowych: {str(e)}")
            QMessageBox.critical(self, "Błąd", f"Nie udało się wczytać danych: {str(e)}")
    
    def _update_filters(self):
        """Aktualizuje kontrolki filtrów na podstawie wczytanych danych."""
        if not self.weather_data.records:
            return
        
        # Aktualizacja listy lokalizacji
        self.location.clear()
        self.location.addItem("Wszystkie")
        for location in self.weather_data.get_locations():
            self.location.addItem(location)
        
        logger.debug(f"Zaktualizowano filtry pogodowe, dodano {self.location.count() - 1} lokalizacji")
    
    def _update_table(self, records=None):
        """Aktualizuje tabelę danych pogodowych."""
        if records is None:
            records = self.weather_data.filtered_records
        
        self.weather_table.setRowCount(len(records))
        
        for i, record in enumerate(records):
            # Data
            self.weather_table.setItem(i, 0, QTableWidgetItem(record.date.strftime('%Y-%m-%d')))
            # Lokalizacja
            self.weather_table.setItem(i, 1, QTableWidgetItem(record.location_id))
            # Średnia temperatura
            self.weather_table.setItem(i, 2, QTableWidgetItem(f"{record.avg_temp:.1f}"))
            # Minimalna temperatura
            self.weather_table.setItem(i, 3, QTableWidgetItem(f"{record.min_temp:.1f}"))
            # Maksymalna temperatura
            self.weather_table.setItem(i, 4, QTableWidgetItem(f"{record.max_temp:.1f}"))
            # Opady
            self.weather_table.setItem(i, 5, QTableWidgetItem(f"{record.precipitation:.1f}"))
            # Nasłonecznienie
            self.weather_table.setItem(i, 6, QTableWidgetItem(f"{record.sunshine_hours:.1f}"))
    
    def _filter_by_preferences(self, records):
        """Filtruje rekordy pogodowe według preferencji użytkownika."""
        min_temp = self.min_pref_temp.value()
        max_precip = self.max_precip.value()
        min_sunshine = self.min_sunshine.value()
        
        filtered = []
        for record in records:
            if (record.min_temp >= min_temp and
                record.precipitation <= max_precip and
                record.sunshine_hours >= min_sunshine):
                filtered.append(record)
        
        return filtered

    def _update_statistics(self):
        """Aktualizuje statystyki pogodowe i tabelę."""
        if not self.weather_data.records:
            logger.debug("Próba aktualizacji statystyk bez wczytanych danych")
            return
            
        location_id = None
        if self.location.currentText() != "Wszystkie":
            location_id = self.location.currentText()
        
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        # Podstawowe filtry
        filters = {}
        if location_id:
            filters['location'] = location_id
        if start_date and end_date and start_date <= end_date:
            filters['date_range'] = (start_date, end_date)
            
        # Pobierz rekordy z podstawowymi filtrami
        filtered_records = self.weather_data.filter_records(**filters)
        
        # Następnie zastosuj preferencje pogodowe
        preference_filtered = self._filter_by_preferences(filtered_records)
        
        # Zaktualizuj tabelę z wynikami filtrowania
        self._update_table(preference_filtered)
        
        # Aktualizuj status
        status_msg = f"Wyświetlanie {len(preference_filtered)} z {len(self.weather_data.records)} rekordów"
        self.status_label.setText(status_msg)
        
        # Oblicz statystyki na przefiltrowanych danych
        if preference_filtered:
            avg_temp = sum(r.avg_temp for r in preference_filtered) / len(preference_filtered)
            total_precip = sum(r.precipitation for r in preference_filtered)
            sunny_days = sum(1 for r in preference_filtered if r.sunshine_hours >= self.min_sunshine.value())
            
            self.avg_temp.setText(f"{avg_temp:.1f} °C")
            self.total_precip.setText(f"{total_precip:.1f} mm")
            self.sunny_days.setText(f"{sunny_days}")
            logger.debug(f"Zaktualizowano statystyki: temp={avg_temp:.1f}°C, opady={total_precip:.1f}mm, słoneczne dni={sunny_days}")
        else:
            self.avg_temp.setText("0.0 °C")
            self.total_precip.setText("0.0 mm")
            self.sunny_days.setText("0")
            logger.debug("Brak rekordów spełniających kryteria filtrowania")
    
    def apply_filters(self):
        """Stosuje wybrane filtry do danych pogodowych."""
        if not self.weather_data.records:
            logger.warn("Próba filtrowania pustych danych pogodowych")
            QMessageBox.warning(self, "Ostrzeżenie", "Brak danych do filtrowania!")
            return
        
        # Pobranie wartości filtrów
        filters = {}
        
        # Lokalizacja
        if self.location.currentText() != "Wszystkie":
            filters['location'] = self.location.currentText()
        
        # Zakres dat
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        if start_date and end_date:
            if start_date > end_date:
                logger.warn("Niepoprawny zakres dat w filtrach pogodowych")
                QMessageBox.warning(self, "Ostrzeżenie", "Data początkowa nie może być późniejsza niż data końcowa!")
                return
            
            filters['date_range'] = (start_date, end_date)
        
        logger.debug(f"Zastosowano filtry pogodowe: {filters}")
        
        # Filtrowanie danych i aktualizacja tabeli
        filtered_records = self.weather_data.filter_records(**filters)
        
        # Zastosuj dodatkowe preferencje użytkownika
        filtered_records = self._filter_by_preferences(filtered_records)
        
        self._update_table(filtered_records)
        self._update_statistics()
        
        status_msg = f"Wyświetlanie {len(filtered_records)} z {len(self.weather_data.records)} rekordów"
        self.status_label.setText(status_msg)
        logger.info(status_msg)
    
    def export_to_csv(self):
        """Eksportuje dane pogodowe do pliku CSV."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Eksportuj do CSV",
            "",
            "Pliki CSV (*.csv)"
        )
        
        if not filepath:
            return
        
        try:
            self.weather_data.save_to_csv(filepath)
            logger.info(f"Dane pogodowe wyeksportowane do pliku CSV: {filepath}")
            QMessageBox.information(self, "Sukces", "Dane zostały wyeksportowane pomyślnie!")
        except Exception as e:
            logger.error(f"Błąd eksportu do CSV: {str(e)}")
            QMessageBox.critical(self, "Błąd", f"Nie udało się wyeksportować danych: {str(e)}")
    
    def export_to_json(self):
        """Eksportuje dane pogodowe do pliku JSON."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Eksportuj do JSON",
            "",
            "Pliki JSON (*.json)"
        )
        
        if not filepath:
            return
        
        try:
            self.weather_data.save_to_json(filepath)
            logger.info(f"Dane pogodowe wyeksportowane do pliku JSON: {filepath}")
            QMessageBox.information(self, "Sukces", "Dane zostały wyeksportowane pomyślnie!")
        except Exception as e:
            logger.error(f"Błąd eksportu do JSON: {str(e)}")
            QMessageBox.critical(self, "Błąd", f"Nie udało się wyeksportować danych: {str(e)}")
    
    def resizeEvent(self, event):
        """Obsługa zmiany rozmiaru okna."""
        super().resizeEvent(event)
        # Podczas zmiany rozmiaru okna nie zmieniamy szerokości kolumn 