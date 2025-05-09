"""
Strona rekomendacji tras turystycznych.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QGridLayout,
    QScrollArea, QFileDialog, QPushButton, QLabel, QSlider,
    QApplication, QCheckBox, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QEventLoop
import traceback
import sys
sys.path.append('.')
from src.core import ( TrailData, WeatherData, RouteRecommender, UserPreference )
from src.utils import logger
from src.ui.components import (
    StyledLabel, DataForm, ResultCard
)


class RecommendationPage(QWidget):
    """Strona rekomendacji tras turystycznych."""
    
    def __init__(self, parent=None):
        """Inicjalizacja strony rekomendacji."""
        super().__init__(parent)
        self.parent = parent
        self.trail_data = TrailData()
        self.weather_data = WeatherData()
        self.recommender = None
        self.user_preference = UserPreference()  # Dodajemy obiekt preferencji użytkownika
        self.result_cards = []
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Główny układ
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Tytuł strony
        title_label = StyledLabel("Rekomendacje Tras Turystycznych", is_title=True)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Grupa danych
        self.data_form = DataForm("Dane", self)
        main_layout.addWidget(self.data_form)
        
        # Przyciski ładowania danych
        load_buttons = self.data_form.add_buttons_row({
            "load_trails": "Wczytaj dane o trasach",
            "load_weather": "Wczytaj dane pogodowe"
        })
        self.load_trails_btn = load_buttons["load_trails"]
        self.load_weather_btn = load_buttons["load_weather"]
        
        # Status danych
        status_layout = QGridLayout()
        status_layout.addWidget(QLabel("Trasy:"), 0, 0)
        self.trails_status = QLabel("Nie wczytano")
        status_layout.addWidget(self.trails_status, 0, 1)
        
        status_layout.addWidget(QLabel("Dane pogodowe:"), 1, 0)
        self.weather_status = QLabel("Nie wczytano")
        status_layout.addWidget(self.weather_status, 1, 1)
        self.data_form.form_layout.addRow("Status:", status_layout)
        
        # Sekcja parametrów wyszukiwania
        main_content = QHBoxLayout()
        main_layout.addLayout(main_content)
        
        # Lewa kolumna - parametry
        left_column = QVBoxLayout()
        
        # Dodanie obszaru przewijania dla lewej kolumny
        left_scroll_area = QScrollArea()
        left_scroll_area.setWidgetResizable(True)
        left_scroll_area.setFrameShape(QFrame.Shape.NoFrame)  # Usunięcie ramki
        
        # Widget wewnątrz obszaru przewijania
        left_scroll_content = QWidget()
        left_scroll_layout = QVBoxLayout(left_scroll_content)
        left_scroll_layout.setContentsMargins(0, 0, 5, 0)  # Małe marginesy, aby był widoczny pasek przewijania
        
        # Grupa parametrów tras
        self.trail_params_form = DataForm("Parametry tras", self)
        
        # Długość trasy
        self.min_length, self.max_length = self.trail_params_form.add_number_range(
            "length",
            "Długość trasy (km)",
            min_value=0,
            max_value=1000,
            default_min=0,
            default_max=50
        )
        
        # Poziom trudności
        self.min_difficulty, self.max_difficulty = self.trail_params_form.add_number_range(
            "difficulty",
            "Poziom trudności",
            min_value=1,
            max_value=5,
            default_min=1,
            default_max=5,
            step=1
        )
        
        # Region
        self.region = self.trail_params_form.add_combo_field(
            "region",
            "Region",
            ["Wszystkie"]
        )
        
        # Kategorie tras (nowe)
        categories_layout = QGridLayout()
        categories_layout.setColumnStretch(0, 1)
        categories_layout.setColumnStretch(1, 1)
        
        self.category_checkboxes = {}
        categories = ["Rodzinna", "Widokowa", "Sportowa", "Ekstremalna"]
        row, col = 0, 0
        for category in categories:
            cb = QCheckBox(category)
            self.category_checkboxes[category] = cb
            categories_layout.addWidget(cb, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1
        
        self.trail_params_form.form_layout.addRow("Kategorie tras:", categories_layout)
        
        left_scroll_layout.addWidget(self.trail_params_form)
        
        # Grupa preferencji pogodowych
        self.weather_params_form = DataForm("Preferencje pogodowe", self)
        
        # Temperatura
        self.min_temp, self.max_temp = self.weather_params_form.add_number_range(
            "temp",
            "Temperatura (°C)",
            min_value=-20,
            max_value=40,
            default_min=15,
            default_max=25
        )
        
        # Opady
        self.min_precip, self.max_precip = self.weather_params_form.add_number_range(
            "precip",
            "Opady (mm)",
            min_value=0,
            max_value=100,
            default_min=0,
            default_max=5
        )
        
        # Nasłonecznienie
        self.min_sunshine, self.max_sunshine = self.weather_params_form.add_number_range(
            "sunshine",
            "Nasłonecznienie (h)",
            min_value=0,
            max_value=24,
            default_min=4,
            default_max=12
        )
        
        # Zakres dat
        self.start_date, self.end_date = self.weather_params_form.add_date_range(
            "date_range",
            "Planowany termin",
            default_start_days=0,
            default_end_days=7
        )
        
        left_scroll_layout.addWidget(self.weather_params_form)
        
        # NOWA SEKCJA: Grupa wag preferencji
        self.weights_form = DataForm("Wagi preferencji", self)
        
        # Waga pogody
        self.weather_weight_slider = QSlider(Qt.Orientation.Horizontal)
        self.weather_weight_slider.setMinimum(0)
        self.weather_weight_slider.setMaximum(100)
        self.weather_weight_slider.setValue(int(self.user_preference.weights['weather']))
        self.weather_weight_label = QLabel(f"{int(self.user_preference.weights['weather'])}%")
        self.weather_weight_slider.valueChanged.connect(
            lambda v: self._update_weight_label('weather', v, self.weather_weight_label)
        )
        
        weather_weight_layout = QHBoxLayout()
        weather_weight_layout.addWidget(self.weather_weight_slider)
        weather_weight_layout.addWidget(self.weather_weight_label)
        self.weights_form.form_layout.addRow("Pogoda:", weather_weight_layout)
        
        # Waga trudności
        self.difficulty_weight_slider = QSlider(Qt.Orientation.Horizontal)
        self.difficulty_weight_slider.setMinimum(0)
        self.difficulty_weight_slider.setMaximum(100)
        self.difficulty_weight_slider.setValue(int(self.user_preference.weights['difficulty']))
        self.difficulty_weight_label = QLabel(f"{int(self.user_preference.weights['difficulty'])}%")
        self.difficulty_weight_slider.valueChanged.connect(
            lambda v: self._update_weight_label('difficulty', v, self.difficulty_weight_label)
        )
        
        difficulty_weight_layout = QHBoxLayout()
        difficulty_weight_layout.addWidget(self.difficulty_weight_slider)
        difficulty_weight_layout.addWidget(self.difficulty_weight_label)
        self.weights_form.form_layout.addRow("Trudność:", difficulty_weight_layout)
        
        # Waga długości
        self.length_weight_slider = QSlider(Qt.Orientation.Horizontal)
        self.length_weight_slider.setMinimum(0)
        self.length_weight_slider.setMaximum(100)
        self.length_weight_slider.setValue(int(self.user_preference.weights['length']))
        self.length_weight_label = QLabel(f"{int(self.user_preference.weights['length'])}%")
        self.length_weight_slider.valueChanged.connect(
            lambda v: self._update_weight_label('length', v, self.length_weight_label)
        )
        
        length_weight_layout = QHBoxLayout()
        length_weight_layout.addWidget(self.length_weight_slider)
        length_weight_layout.addWidget(self.length_weight_label)
        self.weights_form.form_layout.addRow("Długość:", length_weight_layout)
        
        # Waga przewyższenia
        self.elevation_weight_slider = QSlider(Qt.Orientation.Horizontal)
        self.elevation_weight_slider.setMinimum(0)
        self.elevation_weight_slider.setMaximum(100)
        self.elevation_weight_slider.setValue(int(self.user_preference.weights['elevation']))
        self.elevation_weight_label = QLabel(f"{int(self.user_preference.weights['elevation'])}%")
        self.elevation_weight_slider.valueChanged.connect(
            lambda v: self._update_weight_label('elevation', v, self.elevation_weight_label)
        )
        
        elevation_weight_layout = QHBoxLayout()
        elevation_weight_layout.addWidget(self.elevation_weight_slider)
        elevation_weight_layout.addWidget(self.elevation_weight_label)
        self.weights_form.form_layout.addRow("Przewyższenie:", elevation_weight_layout)
        
        # Przycisk resetowania wag
        self.reset_weights_btn = QPushButton("Resetuj wagi")
        self.reset_weights_btn.clicked.connect(self._reset_weights)
        
        self.weights_form.form_layout.addRow("", self.reset_weights_btn)
        
        left_scroll_layout.addWidget(self.weights_form)
        
        # Przycisk generowania rekomendacji
        self.recommend_btn = QPushButton("Generuj rekomendacje")
        self.recommend_btn.setMinimumHeight(35)
        self.recommend_btn.clicked.connect(self.generate_recommendations)
        left_scroll_layout.addWidget(self.recommend_btn)
        
        # Przypisanie zawartości do obszaru przewijania
        left_scroll_area.setWidget(left_scroll_content)
        
        # Dodanie obszaru przewijania do lewej kolumny
        left_column.addWidget(left_scroll_area)
        
        # Prawa kolumna - wyniki
        right_column = QVBoxLayout()
        
        # Tabela wyników - zastąpimy ją layoutem z przewijaniem
        results_header_layout = QHBoxLayout()
        results_label = StyledLabel("Rekomendowane trasy:", is_title=False)
        results_header_layout.addWidget(results_label)
        
        right_column.addLayout(results_header_layout)
        
        # Obszar przewijania dla wyników
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        right_column.addWidget(scroll_area)
        
        # Widget wewnątrz obszaru przewijania
        scroll_content = QWidget()
        self.results_layout = QVBoxLayout(scroll_content)
        
        # Komunikat początkowy
        self.no_results_label = QLabel(
            "Wczytaj dane o trasach i dane pogodowe, a następnie kliknij 'Generuj rekomendacje'."
        )
        self.no_results_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_results_label.setWordWrap(True)
        self.results_layout.addWidget(self.no_results_label)
        
        # Miejsce na wyniki rekomendacji
        self.results_layout.addStretch()
        
        # Przypisanie zawartości do obszaru przewijania
        scroll_area.setWidget(scroll_content)
        
        # Dodanie kolumn do głównego układu
        main_content.addLayout(left_column, 1)
        main_content.addLayout(right_column, 2)
        
        # Przyciski na dole
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_button = QPushButton("Powrót")
        close_button.clicked.connect(lambda: self.parent.show_home_page())
        buttons_layout.addWidget(close_button)
        
        main_layout.addLayout(buttons_layout)
    
    def _update_weight_label(self, weight_name, value, label):
        """Aktualizuje etykietę wagi i preferencje użytkownika."""
        label.setText(f"{value}%")
        
        # Aktualizacja wagi w preferencjach
        self.user_preference.weights[weight_name] = value
        
        # Normalizacja wag
        self.user_preference._validate_weights()
        
        # Aktualizacja suwaków po normalizacji
        self._update_weight_sliders()
    
    def _update_weight_sliders(self):
        """Aktualizuje suwaki po normalizacji wag."""
        # Blokujemy sygnały, aby uniknąć pętli
        self.weather_weight_slider.blockSignals(True)
        self.difficulty_weight_slider.blockSignals(True)
        self.length_weight_slider.blockSignals(True)
        self.elevation_weight_slider.blockSignals(True)
        
        # Aktualizacja wartości suwaków
        self.weather_weight_slider.setValue(int(self.user_preference.weights['weather']))
        self.difficulty_weight_slider.setValue(int(self.user_preference.weights['difficulty']))
        self.length_weight_slider.setValue(int(self.user_preference.weights['length']))
        self.elevation_weight_slider.setValue(int(self.user_preference.weights['elevation']))
        
        # Aktualizacja etykiet
        self.weather_weight_label.setText(f"{int(self.user_preference.weights['weather'])}%")
        self.difficulty_weight_label.setText(f"{int(self.user_preference.weights['difficulty'])}%")
        self.length_weight_label.setText(f"{int(self.user_preference.weights['length'])}%")
        self.elevation_weight_label.setText(f"{int(self.user_preference.weights['elevation'])}%")
        
        # Odblokowujemy sygnały
        self.weather_weight_slider.blockSignals(False)
        self.difficulty_weight_slider.blockSignals(False)
        self.length_weight_slider.blockSignals(False)
        self.elevation_weight_slider.blockSignals(False)
    
    def _reset_weights(self):
        """Resetuje wagi do wartości domyślnych."""
        # Ustawiamy domyślne wagi
        self.user_preference.weights = {
            'weather': 40.0,
            'difficulty': 20.0,
            'length': 20.0,
            'elevation': 10.0,
            'tags': 10.0
        }
        
        # Aktualizacja suwaków
        self._update_weight_sliders()
    
    def _connect_signals(self):
        """Połączenie sygnałów z slotami."""
        self.load_trails_btn.clicked.connect(self.load_trail_data)
        self.load_weather_btn.clicked.connect(self.load_weather_data)
    
    def load_trail_data(self):
        """Wczytuje dane o trasach."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wczytaj dane o trasach", "", "CSV (*.csv);;JSON (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # Wczytanie danych
            if file_path.lower().endswith('.csv'):
                self.trail_data.load_from_csv(file_path)
            elif file_path.lower().endswith('.json'):
                self.trail_data.load_from_json(file_path)
            else:
                QMessageBox.warning(self, "Nieobsługiwany format", "Wybierz plik CSV lub JSON.")
                return
            
            # Aktualizacja statusu
            self.trails_status.setText(f"Wczytano {len(self.trail_data.trails)} tras")
            
            # Aktualizacja listy regionów
            regions = ["Wszystkie"] + list(self.trail_data.get_regions())
            self.region.clear()
            self.region.addItems(regions)
            
            # Inicjalizacja obiektu rekomendacji
            if self.weather_data.records:
                self.recommender = RouteRecommender(self.trail_data, self.weather_data)
                self.recommender.set_user_preference(self.user_preference)
            
            QMessageBox.information(
                self, "Sukces", f"Pomyślnie wczytano {len(self.trail_data.trails)} tras."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas wczytywania danych: {str(e)}")
            logger.error(f"Błąd wczytywania danych tras: {str(e)}")
            logger.debug(traceback.format_exc())
    
    def load_weather_data(self):
        """Wczytuje dane pogodowe."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wczytaj dane pogodowe", "", "CSV (*.csv);;JSON (*.json)"
        )
        
        if not file_path:
            return
        
        try:
            # Wczytanie danych
            if file_path.lower().endswith('.csv'):
                self.weather_data.load_from_csv(file_path)
            elif file_path.lower().endswith('.json'):
                self.weather_data.load_from_json(file_path)
            else:
                QMessageBox.warning(self, "Nieobsługiwany format", "Wybierz plik CSV lub JSON.")
                return
            
            # Aktualizacja statusu
            self.weather_status.setText(f"Wczytano {len(self.weather_data.records)} rekordów")
            
            # Inicjalizacja obiektu rekomendacji
            if self.trail_data.trails:
                self.recommender = RouteRecommender(self.trail_data, self.weather_data)
                self.recommender.set_user_preference(self.user_preference)
            
            QMessageBox.information(
                self, "Sukces", f"Pomyślnie wczytano {len(self.weather_data.records)} rekordów pogodowych."
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas wczytywania danych: {str(e)}")
            logger.error(f"Błąd wczytywania danych pogodowych: {str(e)}")
            logger.debug(traceback.format_exc())
    
    def generate_recommendations(self):
        """Generuje rekomendacje tras na podstawie wybranych parametrów."""
        # Sprawdzenie, czy dane zostały wczytane
        if not self.trail_data.trails:
            QMessageBox.warning(self, "Brak danych", "Nie wczytano danych o trasach.")
            return
        
        if not self.weather_data.records:
            QMessageBox.warning(self, "Brak danych", "Nie wczytano danych pogodowych.")
            return
        
        # Inicjalizacja obiektu rekomendacji, jeśli jeszcze nie istnieje
        if not self.recommender:
            self.recommender = RouteRecommender(self.trail_data, self.weather_data)
            self.recommender.set_user_preference(self.user_preference)
        
        try:
            # Aktualizacja preferencji użytkownika
            self.user_preference.update_preferences(
                min_temperature=self.min_temp.value(),
                max_temperature=self.max_temp.value(),
                max_precipitation=self.max_precip.value(),
                min_sunshine_hours=self.min_sunshine.value(),
                min_difficulty=self.min_difficulty.value(),
                max_difficulty=self.max_difficulty.value(),
                min_length=self.min_length.value(),
                max_length=self.max_length.value()
            )
            
            # Parametry filtrowania tras
            trail_params = {
                'min_length': self.min_length.value(),
                'max_length': self.max_length.value(),
                'min_difficulty': self.min_difficulty.value(),
                'max_difficulty': self.max_difficulty.value()
            }
            
            # Dodanie regionu, jeśli wybrano
            if self.region.currentText() != "Wszystkie":
                trail_params['region'] = self.region.currentText()
            
            # Dodanie kategorii, jeśli wybrano
            selected_categories = [
                cat for cat, cb in self.category_checkboxes.items() if cb.isChecked()
            ]
            if selected_categories:
                trail_params['categories'] = selected_categories
            
            # Zakres dat
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            # Pokazanie "ładowania"
            self._clear_recommendations()
            self.no_results_label.setText("Generowanie rekomendacji...")
            QApplication.processEvents()  # Aktualizacja UI
            
            # Generowanie rekomendacji
            recommendations = self.recommender.recommend_routes(
                start_date=start_date,
                end_date=end_date,
                user_preference=self.user_preference,
                trail_params=trail_params
            )
            
            # Wyświetlenie wyników
            self._display_recommendations(recommendations)
            
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas generowania rekomendacji: {str(e)}")
            logger.error(f"Błąd generowania rekomendacji: {str(e)}")
            logger.debug(traceback.format_exc())
    
    def _display_recommendations(self, recommendations):
        """Wyświetla rekomendacje tras."""
        # Czyszczenie poprzednich wyników
        self._clear_recommendations()
        
        if not recommendations:
            self.no_results_label.setText("Nie znaleziono tras spełniających kryteria.")
            return
        
        # Zapisanie rekomendacji do późniejszego eksportu
        self.current_recommendations = recommendations
        
        # Ukrycie komunikatu "brak wyników"
        self.no_results_label.setVisible(False)
        
        # Wyświetlenie rekomendacji
        for i, rec in enumerate(recommendations):
            # Tworzenie karty wyników
            trail = rec['trail']
            result_card = ResultCard()
            
            # Podstawowe informacje
            result_card.set_title(f"{i+1}. {trail.name}")
            result_card.add_detail("Region", trail.region)
            result_card.add_detail("Długość", f"{trail.length_km} km")
            result_card.add_detail("Trudność", f"{trail.difficulty}/5")
            result_card.add_detail("Przewyższenie", f"{trail.elevation_gain} m")
            
            # Nowe informacje
            # Kategorie
            if 'categories' in rec:
                result_card.add_detail("Kategorie", ", ".join(rec['categories']))
            
            # Szacowany czas przejścia
            if 'estimated_time' in rec:
                result_card.add_detail("Szacowany czas", rec['estimated_time'])
            
            # Indeks komfortu pogodowego
            if 'weather_comfort_index' in rec:
                result_card.add_detail("Komfort pogodowy", f"{rec['weather_comfort_index']}/100")
            
            # Ocena dopasowania do preferencji
            if 'preference_match_score' in rec:
                result_card.add_detail("Dopasowanie do preferencji", f"{rec['preference_match_score']}/100")
            
            # Całkowita ocena
            result_card.add_detail("Ocena ogólna", f"{rec['total_score']}/100", is_highlighted=True)
            
            # Dodanie karty do listy
            self.results_layout.insertWidget(self.results_layout.count() - 1, result_card)
            self.result_cards.append(result_card)
            
            # Dodanie przycisku do wyświetlenia szczegółowych statystyk
            details_btn = QPushButton("Pokaż statystyki pogodowe")
            details_btn.clicked.connect(lambda checked, t=trail: self._show_trail_statistics(t))
            result_card.add_button(details_btn)
    
    def _show_trail_statistics(self, trail):
        """Wyświetla statystyki pogodowe dla trasy."""
        if not self.recommender:
            QMessageBox.warning(self, "Błąd", "Nie można wygenerować statystyk.")
            return
        
        try:
            # Pobieranie statystyk dla trasy
            stats = self.recommender.get_trail_statistics(trail)
            
            # Formatowanie statystyk do wyświetlenia
            message = f"<b>Statystyki dla trasy: {trail.name}</b><br><br>"
            message += f"<b>Region:</b> {stats['region']}<br>"
            message += f"<b>Długość:</b> {stats['length_km']} km<br>"
            message += f"<b>Trudność:</b> {stats['difficulty']}/5<br>"
            message += f"<b>Przewyższenie:</b> {stats['elevation_gain']} m<br>"
            message += f"<b>Kategorie:</b> {', '.join(stats['categories'])}<br>"
            message += f"<b>Szacowany czas przejścia:</b> {stats['estimated_time']}<br><br>"
            
            message += "<b>Statystyki pogodowe:</b><br>"
            message += f"<b>Średnia temperatura:</b> {stats['avg_temperature']:.1f}°C<br>"
            message += f"<b>Liczba słonecznych dni:</b> {stats['sunny_days_count']}<br>"
            message += f"<b>Liczba deszczowych dni:</b> {stats['rainy_days_count']}<br>"
            message += f"<b>Średni indeks komfortu:</b> {stats['avg_comfort_index']:.1f}/100<br><br>"
            
            message += "<b>Najlepsze miesiące:</b><br>"
            for month in stats['best_months']:
                message += f"- {month}<br>"
            
            # Wyświetlenie statystyk
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle(f"Statystyki trasy: {trail.name}")
            msg_box.setTextFormat(Qt.TextFormat.RichText)
            msg_box.setText(message)
            msg_box.setIcon(QMessageBox.Icon.Information)
            msg_box.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas generowania statystyk: {str(e)}")
            logger.error(f"Błąd generowania statystyk: {str(e)}")
            logger.debug(traceback.format_exc())
    
    def _clear_recommendations(self):
        """Czyści listę rekomendacji."""
        # Usunięcie wszystkich kart wyników
        for card in self.result_cards:
            self.results_layout.removeWidget(card)
            card.deleteLater()
        
        self.result_cards = []
        self.current_recommendations = []  # Czyszczenie zapisanych rekomendacji
        
        # Pokazanie komunikatu "brak wyników"
        self.no_results_label.setText("Nie znaleziono tras spełniających kryteria.")
        self.no_results_label.setVisible(True) 