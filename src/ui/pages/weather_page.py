"""
Strona danych pogodowych aplikacji.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QDateEdit, QTableWidget, QTableWidgetItem,
    QGroupBox, QFormLayout, QMessageBox, QHeaderView, QFileDialog,
    QLineEdit, QCheckBox, QSlider
)
from PyQt6.QtCore import Qt, QDate
from datetime import date, timedelta
from src.utils.logger import logger


class WeatherPage(QWidget):
    """Strona do zarządzania danymi pogodowymi."""
    
    def __init__(self, parent=None):
        """
        Inicjalizacja strony danych pogodowych.
        
        Args:
            parent: Rodzic widgetu.
        """
        super().__init__(parent)
        self.parent = parent
        
        logger.debug("Inicjalizacja strony danych pogodowych")
        self.setup_ui()
    
    def setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        main_layout = QVBoxLayout(self)
        
        # Tytuł strony
        title_label = QLabel("Zarządzanie danymi pogodowymi")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        main_layout.addWidget(title_label)
        
        # Grupa pobierania danych z API
        api_group = QGroupBox("Pobieranie danych z API")
        main_layout.addWidget(api_group)
        
        api_layout = QFormLayout(api_group)
        
        # Wybór serwisu API
        self.api_service_combo = QComboBox()
        self.api_service_combo.addItems(["openweathermap", "weatherapi", "visualcrossing"])
        api_layout.addRow("Serwis API:", self.api_service_combo)
        
        # Lokalizacja
        self.location_combo = QComboBox()
        self.location_combo.setEditable(True)
        self.location_combo.addItems(["Warszawa", "Kraków", "Wrocław", "Tatry", "Bieszczady", "Sudety"])
        api_layout.addRow("Lokalizacja:", self.location_combo)
        
        # Daty
        dates_layout = QHBoxLayout()
        api_layout.addRow("Zakres dat:", dates_layout)
        
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addDays(-7))
        self.start_date_edit.setCalendarPopup(True)
        dates_layout.addWidget(self.start_date_edit)
        
        dates_layout.addWidget(QLabel("do"))
        
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        dates_layout.addWidget(self.end_date_edit)
        
        # Przycisk pobierania
        fetch_button_layout = QHBoxLayout()
        api_layout.addRow("", fetch_button_layout)
        
        fetch_forecast_button = QPushButton("Pobierz prognozę")
        fetch_forecast_button.clicked.connect(self.fetch_forecast)
        fetch_button_layout.addWidget(fetch_forecast_button)
        
        fetch_historical_button = QPushButton("Pobierz dane historyczne")
        fetch_historical_button.clicked.connect(self.fetch_historical)
        fetch_button_layout.addWidget(fetch_historical_button)
        
        # Dodajemy grupę filtrów
        filter_group = QGroupBox("Filtrowanie danych")
        main_layout.addWidget(filter_group)
        
        filter_layout = QFormLayout(filter_group)
        
        # Filtrowanie po lokalizacji
        self.filter_location_combo = QComboBox()
        self.filter_location_combo.addItem("Wszystkie lokalizacje")
        filter_layout.addRow("Lokalizacja:", self.filter_location_combo)
        
        # Filtrowanie po datach
        filter_dates_layout = QHBoxLayout()
        filter_layout.addRow("Zakres dat:", filter_dates_layout)
        
        self.filter_start_date = QDateEdit()
        self.filter_start_date.setDate(QDate.currentDate().addDays(-30))
        self.filter_start_date.setCalendarPopup(True)
        filter_dates_layout.addWidget(self.filter_start_date)
        
        filter_dates_layout.addWidget(QLabel("do"))
        
        self.filter_end_date = QDateEdit()
        self.filter_end_date.setDate(QDate.currentDate().addDays(30))
        self.filter_end_date.setCalendarPopup(True)
        filter_dates_layout.addWidget(self.filter_end_date)
        
        # Filtrowanie po temperaturze
        temp_filter_layout = QHBoxLayout()
        filter_layout.addRow("Temperatura (°C):", temp_filter_layout)
        
        self.filter_min_temp = QSlider(Qt.Orientation.Horizontal)
        self.filter_min_temp.setRange(-30, 50)
        self.filter_min_temp.setValue(-10)
        temp_filter_layout.addWidget(self.filter_min_temp)
        
        self.min_temp_label = QLabel(f"{self.filter_min_temp.value()}")
        temp_filter_layout.addWidget(self.min_temp_label)
        self.filter_min_temp.valueChanged.connect(lambda v: self.min_temp_label.setText(f"{v}"))
        
        temp_filter_layout.addWidget(QLabel("do"))
        
        self.filter_max_temp = QSlider(Qt.Orientation.Horizontal)
        self.filter_max_temp.setRange(-30, 50)
        self.filter_max_temp.setValue(30)
        temp_filter_layout.addWidget(self.filter_max_temp)
        
        self.max_temp_label = QLabel(f"{self.filter_max_temp.value()}")
        temp_filter_layout.addWidget(self.max_temp_label)
        self.filter_max_temp.valueChanged.connect(lambda v: self.max_temp_label.setText(f"{v}"))
        
        # Filtrowanie po opadach
        precip_filter_layout = QHBoxLayout()
        filter_layout.addRow("Opady (mm):", precip_filter_layout)
        
        self.filter_min_precip = QSlider(Qt.Orientation.Horizontal)
        self.filter_min_precip.setRange(0, 100)
        self.filter_min_precip.setValue(0)
        precip_filter_layout.addWidget(self.filter_min_precip)
        
        self.min_precip_label = QLabel(f"{self.filter_min_precip.value()}")
        precip_filter_layout.addWidget(self.min_precip_label)
        self.filter_min_precip.valueChanged.connect(lambda v: self.min_precip_label.setText(f"{v}"))
        
        precip_filter_layout.addWidget(QLabel("do"))
        
        self.filter_max_precip = QSlider(Qt.Orientation.Horizontal)
        self.filter_max_precip.setRange(0, 100)
        self.filter_max_precip.setValue(50)
        precip_filter_layout.addWidget(self.filter_max_precip)
        
        self.max_precip_label = QLabel(f"{self.filter_max_precip.value()}")
        precip_filter_layout.addWidget(self.max_precip_label)
        self.filter_max_precip.valueChanged.connect(lambda v: self.max_precip_label.setText(f"{v}"))
        
        # Filtrowanie po nasłonecznieniu
        sunshine_filter_layout = QHBoxLayout()
        filter_layout.addRow("Nasłonecznienie (h):", sunshine_filter_layout)
        
        self.filter_min_sunshine = QSlider(Qt.Orientation.Horizontal)
        self.filter_min_sunshine.setRange(0, 24)
        self.filter_min_sunshine.setValue(0)
        sunshine_filter_layout.addWidget(self.filter_min_sunshine)
        
        self.min_sunshine_label = QLabel(f"{self.filter_min_sunshine.value()}")
        sunshine_filter_layout.addWidget(self.min_sunshine_label)
        self.filter_min_sunshine.valueChanged.connect(lambda v: self.min_sunshine_label.setText(f"{v}"))
        
        sunshine_filter_layout.addWidget(QLabel("do"))
        
        self.filter_max_sunshine = QSlider(Qt.Orientation.Horizontal)
        self.filter_max_sunshine.setRange(0, 24)
        self.filter_max_sunshine.setValue(12)
        sunshine_filter_layout.addWidget(self.filter_max_sunshine)
        
        self.max_sunshine_label = QLabel(f"{self.filter_max_sunshine.value()}")
        sunshine_filter_layout.addWidget(self.max_sunshine_label)
        self.filter_max_sunshine.valueChanged.connect(lambda v: self.max_sunshine_label.setText(f"{v}"))
        
        # Filtrowanie po zachmurzeniu
        cloud_filter_layout = QHBoxLayout()
        filter_layout.addRow("Zachmurzenie (%):", cloud_filter_layout)
        
        self.filter_min_cloud = QSlider(Qt.Orientation.Horizontal)
        self.filter_min_cloud.setRange(0, 100)
        self.filter_min_cloud.setValue(0)
        cloud_filter_layout.addWidget(self.filter_min_cloud)
        
        self.min_cloud_label = QLabel(f"{self.filter_min_cloud.value()}")
        cloud_filter_layout.addWidget(self.min_cloud_label)
        self.filter_min_cloud.valueChanged.connect(lambda v: self.min_cloud_label.setText(f"{v}"))
        
        cloud_filter_layout.addWidget(QLabel("do"))
        
        self.filter_max_cloud = QSlider(Qt.Orientation.Horizontal)
        self.filter_max_cloud.setRange(0, 100)
        self.filter_max_cloud.setValue(100)
        cloud_filter_layout.addWidget(self.filter_max_cloud)
        
        self.max_cloud_label = QLabel(f"{self.filter_max_cloud.value()}")
        cloud_filter_layout.addWidget(self.max_cloud_label)
        self.filter_max_cloud.valueChanged.connect(lambda v: self.max_cloud_label.setText(f"{v}"))
        
        # Przycisk filtrowania
        filter_buttons_layout = QHBoxLayout()
        filter_layout.addRow("", filter_buttons_layout)
        
        apply_filter_button = QPushButton("Zastosuj filtry")
        apply_filter_button.clicked.connect(self.apply_filters)
        filter_buttons_layout.addWidget(apply_filter_button)
        
        reset_filter_button = QPushButton("Resetuj filtry")
        reset_filter_button.clicked.connect(self.reset_filters)
        filter_buttons_layout.addWidget(reset_filter_button)
        
        # Tabela danych
        table_label = QLabel("Dane pogodowe:")
        main_layout.addWidget(table_label)
        
        self.weather_table = QTableWidget(0, 8)
        self.weather_table.setHorizontalHeaderLabels([
            "Data", "Lokalizacja", "Śr. temp (°C)", "Min temp (°C)", 
            "Max temp (°C)", "Opady (mm)", "Godz. słoneczne", "Zachmurzenie (%)"
        ])
        self.weather_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.weather_table)
        
        # Przyciski eksportu i powrotu
        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)
        
        buttons_layout.addStretch()
        
        close_button = QPushButton("Powrót")
        close_button.clicked.connect(self.parent.show_home_page)
        buttons_layout.addWidget(close_button)
    
    def fetch_forecast(self):
        """Pobiera prognozę pogody z wybranego API."""
        service = self.api_service_combo.currentText()
        location = self.location_combo.currentText()
        
        # Pobierz wybrane daty
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        
        # Oblicz liczbę dni między datami
        days = (end_date - start_date).days + 1
        
        if not self.parent.api_client.api_keys.get(service):
            self.parent.show_error(
                "Brak klucza API",
                f"Nie skonfigurowano klucza API dla serwisu {service}. "
                "Przejdź do menu Narzędzia > Konfiguracja API, aby dodać klucz."
            )
            return
        
        try:
            # Pobieranie prognozy na wskazaną liczbę dni
            weather_records = self.parent.api_client.get_weather_forecast(
                service, location, days=days
            )
            
            if not weather_records:
                self.parent.show_error(
                    "Brak danych",
                    f"Nie otrzymano żadnych danych prognozy dla lokalizacji {location}."
                )
                return
                
            # Aktualizacja danych
            self.parent.weather_data.records = weather_records
            self.parent.weather_data.filtered_records = weather_records.copy()
            
            # Aktualizacja tabeli
            self.update_data()
            
            # Dodanie lokalizacji do filtra
            self.update_filter_locations()
            
            # Wyświetl informację o różnicy w datach (jeśli występuje)
            min_date, max_date = self.parent.weather_data.get_date_range()
            date_mismatch = (min_date != start_date or max_date != end_date)
            
            info_message = (
                f"Pomyślnie pobrano prognozę pogody dla lokalizacji {location} "
                f"na okres od {min_date.strftime('%d.%m.%Y')} do {max_date.strftime('%d.%m.%Y')} "
                f"({len(weather_records)} dni)."
            )
            
            if date_mismatch:
                info_message += (
                    f"\n\nUwaga: Otrzymany zakres dat różni się od żądanego "
                    f"({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}). "
                    f"API pogodowe mogło zwrócić tylko dostępne dane."
                )
            
            self.parent.show_info("Pobrano prognozę", info_message)
        except Exception as e:
            self.parent.show_error(
                "Błąd pobierania danych", 
                f"Nie udało się pobrać prognozy pogody: {str(e)}"
            )
    
    def fetch_historical(self):
        """Pobiera historyczne dane pogodowe z wybranego API."""
        service = self.api_service_combo.currentText()
        location = self.location_combo.currentText()
        
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        
        # Sprawdzenie, czy start_date nie jest późniejsza niż end_date
        if start_date > end_date:
            self.parent.show_error(
                "Błędny zakres dat",
                "Data początkowa nie może być późniejsza niż data końcowa."
            )
            return
        
        # Sprawdzenie, czy zakres dat nie jest zbyt duży (limit 30 dni dla wielu API)
        if (end_date - start_date).days > 30:
            result = QMessageBox.question(
                self,
                "Duży zakres dat",
                "Wybrany zakres dat przekracza 30 dni, co może spowodować wiele zapytań do API. Kontynuować?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if result == QMessageBox.StandardButton.No:
                return
        
        if not self.parent.api_client.api_keys.get(service):
            self.parent.show_error(
                "Brak klucza API",
                f"Nie skonfigurowano klucza API dla serwisu {service}. "
                "Przejdź do menu Narzędzia > Konfiguracja API, aby dodać klucz."
            )
            return
        
        try:
            # Pobieranie historycznych danych
            weather_records = self.parent.api_client.get_historical_weather(
                service, location, start_date, end_date
            )
            
            if not weather_records:
                self.parent.show_error(
                    "Brak danych",
                    f"Nie otrzymano żadnych danych historycznych dla lokalizacji {location}."
                )
                return
            
            # Aktualizacja danych
            self.parent.weather_data.records = weather_records
            self.parent.weather_data.filtered_records = weather_records.copy()
            
            # Aktualizacja tabeli
            self.update_data()
            
            # Dodanie lokalizacji do filtra
            self.update_filter_locations()
            
            # Wyświetl informację o różnicy w datach (jeśli występuje)
            min_date, max_date = self.parent.weather_data.get_date_range()
            date_mismatch = (min_date != start_date or max_date != end_date)
            
            info_message = (
                f"Pomyślnie pobrano historyczne dane pogodowe dla lokalizacji {location} "
                f"za okres od {min_date.strftime('%d.%m.%Y')} do {max_date.strftime('%d.%m.%Y')} "
                f"({len(weather_records)} dni)."
            )
            
            if date_mismatch:
                info_message += (
                    f"\n\nUwaga: Otrzymany zakres dat różni się od żądanego "
                    f"({start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}). "
                    f"API pogodowe mogło zwrócić tylko dostępne dane."
                )
            
            self.parent.show_info("Pobrano dane historyczne", info_message)
        except Exception as e:
            self.parent.show_error(
                "Błąd pobierania danych", 
                f"Nie udało się pobrać historycznych danych pogodowych: {str(e)}"
            )
    
    def update_data(self):
        """Aktualizuje dane na stronie, w tym tabelę i filtry."""
        self.update_weather_table()
        self.update_filter_locations()
        
        # Aktualizacja zakresu dat w filtrach
        if self.parent.weather_data.records:
            min_date, max_date = self.parent.weather_data.get_date_range()
            self.filter_start_date.setDate(QDate.fromString(min_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
            self.filter_end_date.setDate(QDate.fromString(max_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
            
            # Aktualizacja dat w panelu pobierania, aby odzwierciedlały faktycznie otrzymane daty
            self.sync_api_dates_with_data()
    
    def sync_api_dates_with_data(self):
        """Synchronizuje daty w panelu pobierania z faktycznie otrzymanymi danymi."""
        if not self.parent.weather_data.records:
            return
            
        min_date, max_date = self.parent.weather_data.get_date_range()
        self.start_date_edit.setDate(QDate.fromString(min_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        self.end_date_edit.setDate(QDate.fromString(max_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
    
    def update_filter_locations(self):
        """Aktualizuje listę lokalizacji w filtrze."""
        # Zapamiętaj aktualnie wybraną lokalizację
        current_location = self.filter_location_combo.currentText()
        
        # Wyczyszczenie i dodanie domyślnej opcji
        self.filter_location_combo.clear()
        self.filter_location_combo.addItem("Wszystkie lokalizacje")
        
        # Dodanie dostępnych lokalizacji
        if self.parent.weather_data.records:
            locations = self.parent.weather_data.get_locations()
            self.filter_location_combo.addItems(locations)
            
            # Przywróć wcześniejszą lokalizację, jeśli istnieje
            index = self.filter_location_combo.findText(current_location)
            if index >= 0:
                self.filter_location_combo.setCurrentIndex(index)
    
    def apply_filters(self):
        """Zastosowanie filtrów do danych pogodowych."""
        if not self.parent.weather_data.records:
            self.parent.show_error("Brak danych", "Brak danych pogodowych do filtrowania.")
            return
        
        # Pobieranie wybranych filtrów
        location = self.filter_location_combo.currentText()
        start_date = self.filter_start_date.date().toPyDate()
        end_date = self.filter_end_date.date().toPyDate()
        min_temp = self.filter_min_temp.value()
        max_temp = self.filter_max_temp.value()
        min_precip = self.filter_min_precip.value()
        max_precip = self.filter_max_precip.value()
        min_sunshine = self.filter_min_sunshine.value()
        max_sunshine = self.filter_max_sunshine.value()
        min_cloud = self.filter_min_cloud.value()
        max_cloud = self.filter_max_cloud.value()
        
        # Resetowanie filtrowanych rekordów
        self.parent.weather_data.filtered_records = self.parent.weather_data.records.copy()
        
        # Filtrowanie po lokalizacji
        if location != "Wszystkie lokalizacje":
            self.parent.weather_data.filter_by_location(location)
        
        # Filtrowanie po zakresie dat
        if start_date and end_date:
            self.parent.weather_data.filter_by_date_range(start_date, end_date)
        
        # Filtrowanie po temperaturze
        self.filter_by_temperature(min_temp, max_temp)
        
        # Filtrowanie po opadach
        self.filter_by_precipitation(min_precip, max_precip)
        
        # Filtrowanie po nasłonecznieniu
        self.filter_by_sunshine(min_sunshine, max_sunshine)
        
        # Filtrowanie po zachmurzeniu
        self.filter_by_cloud_cover(min_cloud, max_cloud)
        
        # Aktualizacja tabeli
        self.update_weather_table(use_filtered=True)
        
        # Informacja o liczbie wyników
        self.parent.status_bar.showMessage(
            f"Zastosowano filtry: znaleziono {len(self.parent.weather_data.filtered_records)} rekordów", 
            3000
        )
    
    def filter_by_temperature(self, min_temp, max_temp):
        """
        Filtruje rekordy pogodowe według zakresu temperatur.
        
        Args:
            min_temp: Minimalna temperatura.
            max_temp: Maksymalna temperatura.
        """
        self.parent.weather_data.filtered_records = [
            record for record in self.parent.weather_data.filtered_records
            if min_temp <= record.avg_temp <= max_temp
        ]
    
    def filter_by_precipitation(self, min_precip, max_precip):
        """
        Filtruje rekordy pogodowe według zakresu opadów.
        
        Args:
            min_precip: Minimalne opady w mm.
            max_precip: Maksymalne opady w mm.
        """
        self.parent.weather_data.filtered_records = [
            record for record in self.parent.weather_data.filtered_records
            if min_precip <= record.precipitation <= max_precip
        ]
    
    def filter_by_sunshine(self, min_sunshine, max_sunshine):
        """
        Filtruje rekordy pogodowe według zakresu godzin słonecznych.
        
        Args:
            min_sunshine: Minimalna liczba godzin słonecznych.
            max_sunshine: Maksymalna liczba godzin słonecznych.
        """
        self.parent.weather_data.filtered_records = [
            record for record in self.parent.weather_data.filtered_records
            if min_sunshine <= record.sunshine_hours <= max_sunshine
        ]
    
    def filter_by_cloud_cover(self, min_cloud, max_cloud):
        """
        Filtruje rekordy pogodowe według zakresu zachmurzenia.
        
        Args:
            min_cloud: Minimalne zachmurzenie w %.
            max_cloud: Maksymalne zachmurzenie w %.
        """
        self.parent.weather_data.filtered_records = [
            record for record in self.parent.weather_data.filtered_records
            if min_cloud <= record.cloud_cover <= max_cloud
        ]
    
    def reset_filters(self):
        """Resetuje filtry i przywraca wszystkie dane."""
        if not self.parent.weather_data.records:
            return
        
        # Resetowanie kontrolek filtrów
        self.filter_location_combo.setCurrentIndex(0)  # "Wszystkie lokalizacje"
        
        # Resetowanie zakresu dat
        min_date, max_date = self.parent.weather_data.get_date_range()
        self.filter_start_date.setDate(QDate.fromString(min_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        self.filter_end_date.setDate(QDate.fromString(max_date.strftime('%Y-%m-%d'), 'yyyy-MM-dd'))
        
        # Resetowanie zakresu temperatur
        self.filter_min_temp.setValue(-10)
        self.filter_max_temp.setValue(30)
        
        # Resetowanie zakresu opadów
        self.filter_min_precip.setValue(0)
        self.filter_max_precip.setValue(50)
        
        # Resetowanie zakresu nasłonecznienia
        self.filter_min_sunshine.setValue(0)
        self.filter_max_sunshine.setValue(12)
        
        # Resetowanie zakresu zachmurzenia
        self.filter_min_cloud.setValue(0)
        self.filter_max_cloud.setValue(100)
        
        # Resetowanie filtrowanych rekordów
        self.parent.weather_data.filtered_records = self.parent.weather_data.records.copy()
        
        # Aktualizacja tabeli
        self.update_weather_table()
        
        # Komunikat o zresetowaniu
        self.parent.status_bar.showMessage("Zresetowano filtry", 3000)
    
    def update_weather_table(self, use_filtered=False):
        """
        Aktualizuje tabelę danych pogodowych.
        
        Args:
            use_filtered: Czy używać filtrowanych rekordów zamiast wszystkich.
        """
        records = self.parent.weather_data.filtered_records if use_filtered else self.parent.weather_data.records
        
        # Czyszczenie tabeli
        self.weather_table.setRowCount(0)
        
        # Dodawanie rekordów
        for i, record in enumerate(records):
            self.weather_table.insertRow(i)
            
            # Data
            date_item = QTableWidgetItem(record.date.strftime("%Y-%m-%d"))
            date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weather_table.setItem(i, 0, date_item)
            
            # Lokalizacja
            location_item = QTableWidgetItem(record.location_id)
            location_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weather_table.setItem(i, 1, location_item)
            
            # Średnia temperatura
            avg_temp_item = QTableWidgetItem(f"{record.avg_temp:.1f}")
            avg_temp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weather_table.setItem(i, 2, avg_temp_item)
            
            # Minimalna temperatura
            min_temp_item = QTableWidgetItem(f"{record.min_temp:.1f}")
            min_temp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weather_table.setItem(i, 3, min_temp_item)
            
            # Maksymalna temperatura
            max_temp_item = QTableWidgetItem(f"{record.max_temp:.1f}")
            max_temp_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weather_table.setItem(i, 4, max_temp_item)
            
            # Opady
            precip_item = QTableWidgetItem(f"{record.precipitation:.1f}")
            precip_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weather_table.setItem(i, 5, precip_item)
            
            # Godziny słoneczne
            sunshine_item = QTableWidgetItem(f"{record.sunshine_hours:.1f}")
            sunshine_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weather_table.setItem(i, 6, sunshine_item)
            
            # Zachmurzenie
            cloud_item = QTableWidgetItem(f"{record.cloud_cover}")
            cloud_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.weather_table.setItem(i, 7, cloud_item) 