"""
Strona danych pogodowych aplikacji.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidgetItem
)
from PyQt6.QtCore import Qt, QDate
from src.utils import logger
from src.ui.components import (
    StyledLabel, DataForm, FilterGroup, DataTable,
    WeatherChart
)
from src.ui.components.chart_dialog import ChartDialog


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
        title_label = StyledLabel("Zarządzanie danymi pogodowymi", is_title=True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Grupa pobierania danych z API
        self.api_form = DataForm("Pobieranie danych z API", self)
        self.api_form.submitClicked.connect(self.fetch_forecast)
        main_layout.addWidget(self.api_form)
        
        # Wybór serwisu API
        self.api_service_combo = self.api_form.add_combo_field(
            "api_service", 
            "Serwis API", 
            ["visualcrossing"]
        )
        
        # Lokalizacja
        self.location_combo = self.api_form.add_combo_field(
            "location", 
            "Lokalizacja", 
            ["Warszawa", "Kraków", "Wrocław", "Tatry", "Bieszczady", "Sudety"],
            editable=True
        )
        
        # Daty
        self.start_date_edit, self.end_date_edit = self.api_form.add_date_range(
            "date_range",
            "Zakres dat",
            default_start_days=0,  # Dzisiaj
            default_end_days=14    # Domyślnie 15 dni dla Visual Crossing
        )
        
        # Podłączenie sygnałów zmiany dat
        self.start_date_edit.dateChanged.connect(self.validate_date_range)
        self.end_date_edit.dateChanged.connect(self.validate_date_range)
        
        # Przycisk pobierania
        self.api_form.add_submit_button("Pobierz prognozę")
        
        # Dodajemy grupę filtrów
        self.filter_group = FilterGroup("Filtrowanie danych", self)
        self.filter_group.filterApplied.connect(self.apply_filters)
        self.filter_group.filterReset.connect(self.reset_filters)
        main_layout.addWidget(self.filter_group)
        
        # Filtrowanie po lokalizacji
        self.filter_location_combo = self.filter_group.add_combo_filter(
            "location", 
            "Lokalizacja"
        )
        
        # Filtrowanie po datach
        self.filter_start_date, self.filter_end_date = self.filter_group.add_date_range_filter(
            "date_range",
            "Zakres dat"
        )
        
        # Filtrowanie po temperaturze
        self.filter_min_temp, self.filter_max_temp = self.filter_group.add_slider_filter(
            "temp",
            "Temperatura (°C)",
            -30, 50, -10, 30
        )
        
        # Filtrowanie po opadach
        self.filter_min_precip, self.filter_max_precip = self.filter_group.add_slider_filter(
            "precip",
            "Opady (mm)",
            0, 100, 0, 50
        )
        
        # Filtrowanie po nasłonecznieniu
        self.filter_min_sunshine, self.filter_max_sunshine = self.filter_group.add_slider_filter(
            "sunshine",
            "Nasłonecznienie (h)",
            0, 24, 0, 12
        )
        
        # Filtrowanie po zachmurzeniu
        self.filter_min_cloud, self.filter_max_cloud = self.filter_group.add_slider_filter(
            "cloud",
            "Zachmurzenie (%)",
            0, 100, 0, 100
        )
        
        # Dodanie przycisków filtrowania
        self.filter_group.add_buttons_row()
        
        # Tabela danych
        table_label = QLabel("Dane pogodowe:")
        main_layout.addWidget(table_label)
        
        self.weather_table = DataTable()
        self.weather_table.setColumnCount(8)
        self.weather_table.setHorizontalHeaderLabels([
            "Data", "Lokalizacja", "Śr. temp (°C)", "Min temp (°C)", 
            "Max temp (°C)", "Opady (mm)", "Godz. słoneczne", "Zachmurzenie (%)"
        ])
        main_layout.addWidget(self.weather_table)
        
        # Przyciski
        buttons_layout = QHBoxLayout()
        main_layout.addLayout(buttons_layout)
        
        # Przycisk wykresu
        chart_button = QPushButton("Pokaż wykres")
        chart_button.clicked.connect(self.show_chart_dialog)
        buttons_layout.addWidget(chart_button)
        
        buttons_layout.addStretch()
        
        # Przycisk powrotu
        close_button = QPushButton("Powrót")
        close_button.clicked.connect(self.parent.show_home_page)
        buttons_layout.addWidget(close_button)
        
        # Ukryty wykres do przechowywania danych
        self.weather_chart = WeatherChart()
        self.weather_chart.hide()
    
    def validate_date_range(self):
        """Sprawdza i koryguje zakres dat."""
        start_date = self.start_date_edit.date()
        end_date = self.end_date_edit.date()
        today = QDate.currentDate()
        
        # Sprawdzenie czy daty nie są z przeszłości
        if start_date < today:
            self.start_date_edit.setDate(today)
            start_date = today
        
        if end_date < today:
            self.end_date_edit.setDate(today)
            end_date = today
        
        # Maksymalna liczba dni dla Visual Crossing API
        max_days = 15
        max_allowed_date = today.addDays(max_days - 1)
        
        # Sprawdzenie czy końcowa data nie przekracza maksymalnej
        if end_date > max_allowed_date:
            self.end_date_edit.setDate(max_allowed_date)
            end_date = max_allowed_date
        
        # Sprawdzenie czy data początkowa nie jest późniejsza niż końcowa
        if start_date > end_date:
            self.start_date_edit.setDate(end_date)
    
    def fetch_forecast(self, data=None):
        """
        Pobiera prognozę pogody z wybranego API.
        
        Args:
            data: Dane z formularza (opcjonalne).
        """
        # Jeśli dane są przekazane z sygnału formularza
        if data:
            service = data.get('api_service')
            location = data.get('location')
            start_date = data.get('date_range_start')
            end_date = data.get('date_range_end')
        else:
            # Użyj danych z kontrolek (starszy sposób)
            service = self.api_service_combo.currentText()
            location = self.location_combo.currentText()
            start_date = self.start_date_edit.date().toPyDate()
            end_date = self.end_date_edit.date().toPyDate()
        
        # Sprawdzenie zakresu dat
        days_diff = (end_date - start_date).days + 1
        max_days = 15
        
        if days_diff > max_days:
            self.parent.show_error(
                "Nieprawidłowy zakres dat",
                f"Serwis {service} pozwala na maksymalnie {max_days} dni prognozy.\n"
                f"Wybrany zakres to {days_diff} dni."
            )
            return
        
        if not self.parent.api_client.api_keys.get(service):
            self.parent.show_error(
                "Brak klucza API",
                f"Nie skonfigurowano klucza API dla serwisu {service}. "
                "Przejdź do menu Narzędzia > Konfiguracja API, aby dodać klucz."
            )
            return
        
        try:
            # Dla Visual Crossing używamy zakresu dat
            weather_records = self.parent.api_client.get_weather_forecast(
                service, 
                location, 
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d")
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
                f"({len(weather_records)} {self._get_days_word(len(weather_records))})."
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
    
    def _get_days_word(self, number: int) -> str:
        """
        Zwraca odpowiednią formę słowa 'dzień' w zależności od liczby.
        
        Args:
            number: Liczba dni.
            
        Returns:
            Odpowiednia forma słowa 'dzień'.
        """
        if number == 1:
            return "dzień"
        elif 2 <= number <= 4:
            return "dni"
        else:
            return "dni"
    
    def update_data(self):
        """Aktualizuje dane w tabeli i na wykresie."""
        self.update_weather_table()
        self.weather_chart.set_weather_data(self.parent.weather_data.records)
        self.sync_api_dates_with_data()
        self.update_filter_locations()
    
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
        """Stosuje filtry do danych."""
        # Resetowanie filtrowanych danych
        self.parent.weather_data.filtered_records = self.parent.weather_data.records.copy()
        
        # Filtrowanie po lokalizacji
        location = self.filter_location_combo.currentText()
        if location and location != "Wszystkie":
            self.parent.weather_data.filtered_records = [
                record for record in self.parent.weather_data.filtered_records
                if record.location == location
            ]
        
        # Filtrowanie po datach
        start_date = self.filter_start_date.date().toPyDate()
        end_date = self.filter_end_date.date().toPyDate()
        self.parent.weather_data.filtered_records = [
            record for record in self.parent.weather_data.filtered_records
            if start_date <= record.date <= end_date
        ]
        
        # Filtrowanie po temperaturze
        min_temp = self.filter_min_temp.value()
        max_temp = self.filter_max_temp.value()
        self.filter_by_temperature(min_temp, max_temp)
        
        # Filtrowanie po opadach
        min_precip = self.filter_min_precip.value()
        max_precip = self.filter_max_precip.value()
        self.filter_by_precipitation(min_precip, max_precip)
        
        # Filtrowanie po nasłonecznieniu
        min_sunshine = self.filter_min_sunshine.value()
        max_sunshine = self.filter_max_sunshine.value()
        self.filter_by_sunshine(min_sunshine, max_sunshine)
        
        # Filtrowanie po zachmurzeniu
        min_cloud = self.filter_min_cloud.value()
        max_cloud = self.filter_max_cloud.value()
        self.filter_by_cloud_cover(min_cloud, max_cloud)
        
        # Aktualizacja widoku
        self.update_weather_table(use_filtered=True)
        self.weather_chart.set_weather_data(self.parent.weather_data.filtered_records)
    
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
        """Resetuje wszystkie filtry do wartości domyślnych."""
        # Reset filtra lokalizacji
        self.filter_location_combo.setCurrentText("Wszystkie")
        
        # Reset filtra dat
        if self.parent.weather_data.records:
            min_date, max_date = self.parent.weather_data.get_date_range()
            self.filter_start_date.setDate(min_date)
            self.filter_end_date.setDate(max_date)
        
        # Reset filtra temperatury
        self.filter_min_temp.setValue(-10)
        self.filter_max_temp.setValue(30)
        
        # Reset filtra opadów
        self.filter_min_precip.setValue(0)
        self.filter_max_precip.setValue(50)
        
        # Reset filtra nasłonecznienia
        self.filter_min_sunshine.setValue(0)
        self.filter_max_sunshine.setValue(12)
        
        # Reset filtra zachmurzenia
        self.filter_min_cloud.setValue(0)
        self.filter_max_cloud.setValue(100)
        
        # Aktualizacja widoku
        self.update_weather_table()
        self.weather_chart.set_weather_data(self.parent.weather_data.records)
    
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
    
    def show_chart_dialog(self):
        """Wyświetla okno dialogowe z wykresem."""
        if not self.parent.weather_data.records:
            self.parent.show_error("Brak danych", "Brak danych do wyświetlenia na wykresie.")
            return
            
        dialog = ChartDialog("weather", self)
        dialog.set_data(self.parent.weather_data.filtered_records)
        dialog.exec() 