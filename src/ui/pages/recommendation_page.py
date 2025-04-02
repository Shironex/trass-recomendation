"""
Strona rekomendacji tras turystycznych.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QGridLayout,
    QTableWidgetItem, QScrollArea
)
from PyQt6.QtCore import Qt, QDate

import sys
sys.path.append('.')
from src.ui.components import (
    StyledLabel, BaseButton, PrimaryButton, StyledComboBox,
    StyledDoubleSpinBox, StyledDateEdit, DataTable, CardFrame
)
from src.core.trail_data import TrailData
from src.core.weather_data import WeatherData
from src.core.data_processor import RouteRecommender


class RecommendationPage(QWidget):
    """Strona rekomendacji tras turystycznych."""
    
    def __init__(self, parent=None):
        """Inicjalizacja strony rekomendacji."""
        super().__init__(parent)
        self.main_window = parent
        self.trail_data = TrailData()
        self.weather_data = WeatherData()
        self.recommender = None
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Główny układ
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Tytuł
        title = StyledLabel("Rekomendacje Tras", is_title=True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Układ dwukolumnowy
        content_layout = QHBoxLayout()
        
        # Lewa kolumna - parametry rekomendacji
        left_column = QVBoxLayout()
        
        # Panel ładowania danych
        data_card = CardFrame()
        data_layout = QVBoxLayout(data_card)
        data_layout.setSpacing(15)
        
        # Tytuł panelu
        data_title = StyledLabel("Dane")
        font = data_title.font()
        font.setBold(True)
        data_title.setFont(font)
        data_layout.addWidget(data_title)
        
        # Przyciski ładowania danych
        data_btn_layout = QHBoxLayout()
        self.load_trails_btn = BaseButton("Wczytaj dane o trasach")
        self.load_weather_btn = BaseButton("Wczytaj dane pogodowe")
        data_btn_layout.addWidget(self.load_trails_btn)
        data_btn_layout.addWidget(self.load_weather_btn)
        data_layout.addLayout(data_btn_layout)
        
        # Status danych
        status_layout = QGridLayout()
        status_layout.addWidget(StyledLabel("Trasy:"), 0, 0)
        status_layout.addWidget(StyledLabel("Dane pogodowe:"), 1, 0)
        
        self.trails_status = StyledLabel("Nie wczytano")
        self.weather_status = StyledLabel("Nie wczytano")
        
        status_layout.addWidget(self.trails_status, 0, 1)
        status_layout.addWidget(self.weather_status, 1, 1)
        
        data_layout.addLayout(status_layout)
        
        # Karta parametrów tras
        trail_params_card = CardFrame()
        trail_params_layout = QVBoxLayout(trail_params_card)
        trail_params_layout.setSpacing(15)
        
        # Tytuł parametrów tras
        trail_params_title = StyledLabel("Parametry tras")
        font = trail_params_title.font()
        font.setBold(True)
        trail_params_title.setFont(font)
        trail_params_layout.addWidget(trail_params_title)
        
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
        self.max_length.setValue(50)
        length_inputs.addWidget(self.max_length)
        
        length_layout.addLayout(length_inputs)
        trail_params_layout.addLayout(length_layout)
        
        # Poziom trudności
        difficulty_layout = QVBoxLayout()
        difficulty_layout.addWidget(StyledLabel("Poziom trudności:"))
        self.difficulty = StyledComboBox()
        self.difficulty.addItem("Wszystkie")
        for i in range(1, 6):
            self.difficulty.addItem(str(i))
        difficulty_layout.addWidget(self.difficulty)
        trail_params_layout.addLayout(difficulty_layout)
        
        # Region
        region_layout = QVBoxLayout()
        region_layout.addWidget(StyledLabel("Region:"))
        self.region = StyledComboBox()
        self.region.addItem("Wszystkie")
        region_layout.addWidget(self.region)
        trail_params_layout.addLayout(region_layout)
        
        # Karta preferencji pogodowych
        weather_prefs_card = CardFrame()
        weather_prefs_layout = QVBoxLayout(weather_prefs_card)
        weather_prefs_layout.setSpacing(15)
        
        # Tytuł preferencji pogodowych
        weather_prefs_title = StyledLabel("Preferencje pogodowe")
        font = weather_prefs_title.font()
        font.setBold(True)
        weather_prefs_title.setFont(font)
        weather_prefs_layout.addWidget(weather_prefs_title)
        
        # Temperatura
        temp_layout = QVBoxLayout()
        temp_layout.addWidget(StyledLabel("Preferowana temperatura (°C):"))
        
        temp_inputs = QHBoxLayout()
        
        temp_inputs.addWidget(StyledLabel("Min:"))
        self.min_temp = StyledDoubleSpinBox()
        self.min_temp.setRange(-20, 40)
        self.min_temp.setValue(15)
        temp_inputs.addWidget(self.min_temp)
        
        temp_inputs.addWidget(StyledLabel("Max:"))
        self.max_temp = StyledDoubleSpinBox()
        self.max_temp.setRange(-20, 40)
        self.max_temp.setValue(25)
        temp_inputs.addWidget(self.max_temp)
        
        temp_layout.addLayout(temp_inputs)
        weather_prefs_layout.addLayout(temp_layout)
        
        # Opady
        precip_layout = QVBoxLayout()
        precip_layout.addWidget(StyledLabel("Maksymalne opady (mm):"))
        self.max_precip = StyledDoubleSpinBox()
        self.max_precip.setRange(0, 100)
        self.max_precip.setValue(5)
        precip_layout.addWidget(self.max_precip)
        weather_prefs_layout.addLayout(precip_layout)
        
        # Nasłonecznienie
        sunshine_layout = QVBoxLayout()
        sunshine_layout.addWidget(StyledLabel("Minimalne nasłonecznienie (h):"))
        self.min_sunshine = StyledDoubleSpinBox()
        self.min_sunshine.setRange(0, 24)
        self.min_sunshine.setValue(4)
        sunshine_layout.addWidget(self.min_sunshine)
        weather_prefs_layout.addLayout(sunshine_layout)
        
        # Zakres dat
        date_layout = QVBoxLayout()
        date_layout.addWidget(StyledLabel("Planowany termin:"))
        
        date_inputs = QHBoxLayout()
        
        date_inputs.addWidget(StyledLabel("Od:"))
        self.start_date = StyledDateEdit()
        date_inputs.addWidget(self.start_date)
        
        date_inputs.addWidget(StyledLabel("Do:"))
        self.end_date = StyledDateEdit()
        self.end_date.setDate(self.end_date.date().addDays(7))
        date_inputs.addWidget(self.end_date)
        
        date_layout.addLayout(date_inputs)
        weather_prefs_layout.addLayout(date_layout)
        
        # Przycisk generowania rekomendacji
        self.recommend_btn = PrimaryButton("Generuj rekomendacje")
        
        # Dodanie kart i przycisku do lewej kolumny
        left_column.addWidget(data_card)
        left_column.addWidget(trail_params_card)
        left_column.addWidget(weather_prefs_card)
        left_column.addWidget(self.recommend_btn)
        left_column.addStretch()
        
        # Prawa kolumna - rekomendacje
        right_column = QVBoxLayout()
        
        # Kontener z przewijaniem
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(scroll_area.Shape.NoFrame)
        
        # Widget wewnątrz kontenera
        scroll_content = QWidget()
        self.results_layout = QVBoxLayout(scroll_content)
        self.results_layout.setContentsMargins(0, 0, 0, 0)
        self.results_layout.setSpacing(15)
        
        # Tytuł rekomendacji
        results_title = StyledLabel("Rekomendowane trasy")
        font = results_title.font()
        font.setBold(True)
        font.setPointSize(14)
        results_title.setFont(font)
        results_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.results_layout.addWidget(results_title)
        
        # Komunikat początkowy
        self.no_results_label = StyledLabel(
            "Wczytaj dane o trasach i dane pogodowe, a następnie kliknij 'Generuj rekomendacje'."
        )
        self.no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_results_label.setWordWrap(True)
        self.results_layout.addWidget(self.no_results_label)
        
        # Miejsce na wyniki rekomendacji - puste na początku
        self.results_layout.addStretch()
        
        # Dodanie zawartości do kontenera z przewijaniem
        scroll_area.setWidget(scroll_content)
        right_column.addWidget(scroll_area)
        
        # Dodanie kolumn do głównego układu
        content_layout.addLayout(left_column, 1)
        content_layout.addLayout(right_column, 2)
        
        layout.addLayout(content_layout)
        
        # Przycisk powrotu
        back_layout = QHBoxLayout()
        back_layout.addStretch()
        self.back_btn = BaseButton("Powrót do menu głównego")
        back_layout.addWidget(self.back_btn)
        
        layout.addLayout(back_layout)
    
    def _connect_signals(self):
        """Połączenie sygnałów z slotami."""
        self.load_trails_btn.clicked.connect(self.load_trail_data)
        self.load_weather_btn.clicked.connect(self.load_weather_data)
        self.recommend_btn.clicked.connect(self.generate_recommendations)
        
        if self.main_window:
            self.back_btn.clicked.connect(self.main_window.show_home_page)
    
    def load_trail_data(self):
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
            
            # Aktualizacja regionów w filtrach
            self.region.clear()
            self.region.addItem("Wszystkie")
            for region in self.trail_data.get_regions():
                self.region.addItem(region)
            
            # Aktualizacja statusa
            self.trails_status.setText(f"Wczytano {len(self.trail_data.trails)} tras")
            
            # Aktualizacja rekomendatora jeśli są dane pogodowe
            if hasattr(self, 'weather_data') and self.weather_data.records:
                self.recommender = RouteRecommender(self.trail_data, self.weather_data)
            
            QMessageBox.information(self, "Sukces", "Dane o trasach zostały wczytane pomyślnie!")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wczytać danych: {str(e)}")
    
    def load_weather_data(self):
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
            
            # Aktualizacja statusa
            self.weather_status.setText(f"Wczytano {len(self.weather_data.records)} rekordów")
            
            # Aktualizacja rekomendatora jeśli są dane o trasach
            if hasattr(self, 'trail_data') and self.trail_data.trails:
                self.recommender = RouteRecommender(self.trail_data, self.weather_data)
            
            QMessageBox.information(self, "Sukces", "Dane pogodowe zostały wczytane pomyślnie!")
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wczytać danych: {str(e)}")
    
    def generate_recommendations(self):
        """Generuje rekomendacje tras na podstawie preferencji użytkownika."""
        if not self.recommender:
            if not self.trail_data.trails:
                QMessageBox.warning(self, "Ostrzeżenie", "Brak danych o trasach!")
                return
            
            if not self.weather_data.records:
                QMessageBox.warning(self, "Ostrzeżenie", "Brak danych pogodowych!")
                return
            
            self.recommender = RouteRecommender(self.trail_data, self.weather_data)
        
        # Parametry tras
        trail_params = {}
        
        # Długość
        min_len = self.min_length.value()
        if min_len > 0:
            trail_params['min_length'] = min_len
        
        max_len = self.max_length.value()
        if max_len < self.max_length.maximum():
            trail_params['max_length'] = max_len
        
        # Trudność
        if self.difficulty.currentText() != "Wszystkie":
            trail_params['difficulty'] = int(self.difficulty.currentText())
        
        # Region
        if self.region.currentText() != "Wszystkie":
            trail_params['region'] = self.region.currentText()
        
        # Preferencje pogodowe
        weather_preferences = {
            'min_temp': self.min_temp.value(),
            'max_temp': self.max_temp.value(),
            'max_precipitation': self.max_precip.value(),
            'min_sunshine_hours': self.min_sunshine.value()
        }
        
        # Zakres dat
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        # Generowanie rekomendacji
        try:
            recommendations = self.recommender.recommend_routes(
                weather_preferences,
                trail_params,
                start_date,
                end_date
            )
            
            # Czyszczenie poprzednich rekomendacji
            self._clear_recommendations()
            
            if not recommendations:
                # Brak rekomendacji
                self.no_results_label.setText("Nie znaleziono tras spełniających podane kryteria.")
                self.no_results_label.setVisible(True)
            else:
                # Ukrycie etykiety "brak wyników"
                self.no_results_label.setVisible(False)
                
                # Wyświetlenie rekomendacji
                for i, rec in enumerate(recommendations):
                    self._add_recommendation_card(i + 1, rec)
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie udało się wygenerować rekomendacji: {str(e)}")
    
    def _clear_recommendations(self):
        """Usuwa wszystkie karty rekomendacji."""
        # Usunięcie wszystkich widgetów poza etykietą tytułową i "brak wyników"
        while self.results_layout.count() > 2:
            # Pobierz widget
            widget = self.results_layout.itemAt(2).widget()
            if widget:
                # Usuń widget z układu
                self.results_layout.removeWidget(widget)
                # Usuń widget z pamięci
                widget.deleteLater()
    
    def _add_recommendation_card(self, rank, recommendation):
        """
        Dodaje kartę z rekomendacją trasy.
        
        Args:
            rank: Ranking rekomendacji (1, 2, 3...).
            recommendation: Słownik z danymi rekomendacji.
        """
        # Karta rekomendacji
        card = CardFrame()
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(10)
        
        # Nagłówek z rangą i nazwą
        header_layout = QHBoxLayout()
        
        # Ranga
        rank_label = StyledLabel(f"#{rank}")
        font = rank_label.font()
        font.setPointSize(18)
        font.setBold(True)
        rank_label.setFont(font)
        header_layout.addWidget(rank_label)
        
        # Nazwa trasy
        name_label = StyledLabel(recommendation['name'])
        font = name_label.font()
        font.setPointSize(14)
        font.setBold(True)
        name_label.setFont(font)
        header_layout.addWidget(name_label, 1)
        
        # Ocena
        score_label = StyledLabel(f"Ocena: {recommendation['total_score']:.1f}/100")
        font = score_label.font()
        font.setBold(True)
        score_label.setFont(font)
        header_layout.addWidget(score_label)
        
        card_layout.addLayout(header_layout)
        
        # Szczegóły trasy
        details_grid = QGridLayout()
        details_grid.setColumnStretch(1, 1)
        details_grid.setColumnStretch(3, 1)
        
        # Kolumna 1
        details_grid.addWidget(StyledLabel("Region:"), 0, 0)
        details_grid.addWidget(StyledLabel(recommendation['region']), 0, 1)
        
        details_grid.addWidget(StyledLabel("Długość:"), 1, 0)
        details_grid.addWidget(StyledLabel(f"{recommendation['length_km']:.1f} km"), 1, 1)
        
        # Kolumna 2
        details_grid.addWidget(StyledLabel("Trudność:"), 0, 2)
        details_grid.addWidget(StyledLabel(str(recommendation['difficulty'])), 0, 3)
        
        details_grid.addWidget(StyledLabel("Teren:"), 1, 2)
        details_grid.addWidget(StyledLabel(recommendation['terrain_type']), 1, 3)
        
        # Dodatkowe informacje
        details_grid.addWidget(StyledLabel("Przewyższenie:"), 2, 0)
        details_grid.addWidget(StyledLabel(f"{recommendation['elevation_gain']:.0f} m"), 2, 1)
        
        details_grid.addWidget(StyledLabel("Ocena pogody:"), 2, 2)
        details_grid.addWidget(StyledLabel(f"{recommendation['weather_score']:.1f}/100"), 2, 3)
        
        card_layout.addLayout(details_grid)
        
        # Dodanie karty do wyników
        self.results_layout.insertWidget(self.results_layout.count() - 1, card) 