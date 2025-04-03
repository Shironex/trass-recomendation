"""
Strona rekomendacji tras turystycznych.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QGridLayout,
    QScrollArea, QFileDialog, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QEventLoop
import traceback
import sys
sys.path.append('.')
from src.ui.components import (
    StyledLabel, BaseButton, PrimaryButton, StyledComboBox,
    StyledDoubleSpinBox, StyledDateEdit, CardFrame
)
from src.core.trail_data import TrailData
from src.core.weather_data import WeatherData
from src.core.data_processor import RouteRecommender
from src.utils import logger


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
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Górny pasek z tytułem i przyciskiem powrotu
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        
        # Przycisk powrotu
        self.back_btn = BaseButton("Powrót do menu głównego")
        self.back_btn.setFixedWidth(180)
        top_bar.addWidget(self.back_btn)
        
        # Tytuł
        title = StyledLabel("Rekomendacje Tras", is_title=True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_bar.addWidget(title)
        top_bar.setStretchFactor(self.back_btn, 1)
        top_bar.setStretchFactor(title, 3)
        
        layout.addLayout(top_bar)
        
        # Układ dwukolumnowy
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        
        # Lewa kolumna - parametry rekomendacji
        left_scroll_area = QScrollArea()
        left_scroll_area.setWidgetResizable(True)
        left_scroll_area.setFrameShape(left_scroll_area.Shape.NoFrame)
        left_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Kontener dla lewej kolumny
        left_container = QWidget()
        left_column = QVBoxLayout(left_container)
        left_column.setContentsMargins(0, 0, 5, 0)  # Dodaj margines z prawej strony, aby zrobić miejsce na pasek przewijania
        left_column.setSpacing(8)
        
        # SEKCJA: Panel ładowania danych
        data_card = CardFrame()
        data_layout = QVBoxLayout(data_card)
        data_layout.setContentsMargins(10, 10, 10, 10)
        data_layout.setSpacing(8)
        
        # Tytuł panelu
        data_title = StyledLabel("Dane")
        font = data_title.font()
        font.setBold(True)
        data_title.setFont(font)
        data_layout.addWidget(data_title)
        
        # Przyciski ładowania danych
        data_btn_layout = QGridLayout()
        data_btn_layout.setSpacing(8)
        self.load_trails_btn = BaseButton("Wczytaj dane o trasach")
        self.load_trails_btn.setMinimumHeight(30)
        self.load_weather_btn = BaseButton("Wczytaj dane pogodowe") 
        self.load_weather_btn.setMinimumHeight(30)
        data_btn_layout.addWidget(self.load_trails_btn, 0, 0)
        data_btn_layout.addWidget(self.load_weather_btn, 0, 1)
        data_layout.addLayout(data_btn_layout)
        
        # Status danych
        status_layout = QGridLayout()
        status_layout.setVerticalSpacing(4)
        status_layout.setHorizontalSpacing(8)
        status_layout.setColumnStretch(1, 1)
        
        status_layout.addWidget(StyledLabel("Trasy:"), 0, 0)
        self.trails_status = StyledLabel("Nie wczytano")
        status_layout.addWidget(self.trails_status, 0, 1)
        
        status_layout.addWidget(StyledLabel("Dane pogodowe:"), 1, 0)
        self.weather_status = StyledLabel("Nie wczytano")
        status_layout.addWidget(self.weather_status, 1, 1)
        
        data_layout.addLayout(status_layout)
        
        # Karta parametrów tras
        trail_params_card = CardFrame()
        trail_params_layout = QVBoxLayout(trail_params_card)
        trail_params_layout.setContentsMargins(10, 10, 10, 10)
        trail_params_layout.setSpacing(8)
        
        # Tytuł parametrów tras
        trail_params_title = StyledLabel("Parametry tras")
        font = trail_params_title.font()
        font.setBold(True)
        trail_params_title.setFont(font)
        trail_params_layout.addWidget(trail_params_title)
        
        # Długość trasy
        length_layout = QVBoxLayout()
        length_layout.setSpacing(4)
        length_layout.addWidget(StyledLabel("Długość trasy (km):"))
        
        length_inputs = QGridLayout()
        length_inputs.setSpacing(8)
        length_inputs.setColumnStretch(1, 1)
        length_inputs.setColumnStretch(3, 1)
        
        length_inputs.addWidget(StyledLabel("Min:"), 0, 0)
        self.min_length = StyledDoubleSpinBox()
        self.min_length.setRange(0, 1000)
        self.min_length.setFixedWidth(70)
        length_inputs.addWidget(self.min_length, 0, 1)
        
        length_inputs.addWidget(StyledLabel("Max:"), 0, 2)
        self.max_length = StyledDoubleSpinBox()
        self.max_length.setRange(0, 1000)
        self.max_length.setValue(50)
        self.max_length.setFixedWidth(70)
        length_inputs.addWidget(self.max_length, 0, 3)
        
        length_layout.addLayout(length_inputs)
        trail_params_layout.addLayout(length_layout)
        
        # Poziom trudności
        difficulty_layout = QVBoxLayout()
        difficulty_layout.setSpacing(4)
        difficulty_layout.addWidget(StyledLabel("Poziom trudności:"))
        self.difficulty = StyledComboBox()
        self.difficulty.addItem("Wszystkie")
        for i in range(1, 6):
            self.difficulty.addItem(str(i))
        difficulty_layout.addWidget(self.difficulty)
        trail_params_layout.addLayout(difficulty_layout)
        
        # Region
        region_layout = QVBoxLayout()
        region_layout.setSpacing(4)
        region_layout.addWidget(StyledLabel("Region:"))
        self.region = StyledComboBox()
        self.region.addItem("Wszystkie")
        region_layout.addWidget(self.region)
        trail_params_layout.addLayout(region_layout)
        
        # Karta preferencji pogodowych
        weather_prefs_card = CardFrame()
        weather_prefs_layout = QVBoxLayout(weather_prefs_card)
        weather_prefs_layout.setContentsMargins(10, 10, 10, 10)
        weather_prefs_layout.setSpacing(8)
        
        # Tytuł preferencji pogodowych
        weather_prefs_title = StyledLabel("Preferencje pogodowe")
        font = weather_prefs_title.font()
        font.setBold(True)
        weather_prefs_title.setFont(font)
        weather_prefs_layout.addWidget(weather_prefs_title)
        
        # Temperatura
        temp_layout = QVBoxLayout()
        temp_layout.setSpacing(4)
        temp_layout.addWidget(StyledLabel("Preferowana temperatura (°C):"))
        
        temp_inputs = QHBoxLayout()
        temp_inputs.setSpacing(8)
        
        min_temp_layout = QHBoxLayout()
        min_temp_layout.addWidget(StyledLabel("Min:"), 0)
        self.min_temp = StyledDoubleSpinBox()
        self.min_temp.setRange(-20, 40)
        self.min_temp.setValue(15)
        self.min_temp.setFixedWidth(70)
        min_temp_layout.addWidget(self.min_temp, 1)
        temp_inputs.addLayout(min_temp_layout)
        
        max_temp_layout = QHBoxLayout()
        max_temp_layout.addWidget(StyledLabel("Max:"), 0)
        self.max_temp = StyledDoubleSpinBox()
        self.max_temp.setRange(-20, 40)
        self.max_temp.setValue(25)
        self.max_temp.setFixedWidth(70)
        max_temp_layout.addWidget(self.max_temp, 1)
        temp_inputs.addLayout(max_temp_layout)
        
        temp_layout.addLayout(temp_inputs)
        weather_prefs_layout.addLayout(temp_layout)
        
        # Opady
        precip_layout = QVBoxLayout()
        precip_layout.setSpacing(4)
        precip_layout.addWidget(StyledLabel("Maksymalne opady (mm):"))
        
        precip_input = QHBoxLayout()
        self.max_precip = StyledDoubleSpinBox()
        self.max_precip.setRange(0, 100)
        self.max_precip.setValue(5)
        precip_input.addWidget(self.max_precip)
        precip_input.addStretch(1)
        
        precip_layout.addLayout(precip_input)
        weather_prefs_layout.addLayout(precip_layout)
        
        # Nasłonecznienie
        sunshine_layout = QVBoxLayout()
        sunshine_layout.setSpacing(4)
        sunshine_layout.addWidget(StyledLabel("Minimalne nasłonecznienie (h):"))
        
        sunshine_input = QHBoxLayout()
        self.min_sunshine = StyledDoubleSpinBox()
        self.min_sunshine.setRange(0, 24)
        self.min_sunshine.setValue(4)
        sunshine_input.addWidget(self.min_sunshine)
        sunshine_input.addStretch(1)
        
        sunshine_layout.addLayout(sunshine_input)
        weather_prefs_layout.addLayout(sunshine_layout)
        
        # Zakres dat
        date_layout = QVBoxLayout()
        date_layout.setSpacing(4)
        date_layout.addWidget(StyledLabel("Planowany termin:"))
        
        date_inputs = QGridLayout()
        date_inputs.setSpacing(8)
        date_inputs.setColumnStretch(1, 1)
        date_inputs.setColumnStretch(3, 1)
        
        # Od
        date_inputs.addWidget(StyledLabel("Od:"), 0, 0)
        self.start_date = StyledDateEdit()
        date_inputs.addWidget(self.start_date, 0, 1)
        
        # Do
        date_inputs.addWidget(StyledLabel("Do:"), 0, 2)
        self.end_date = StyledDateEdit()
        self.end_date.setDate(self.end_date.date().addDays(7))
        date_inputs.addWidget(self.end_date, 0, 3)
        
        date_layout.addLayout(date_inputs)
        weather_prefs_layout.addLayout(date_layout)
        
        # Przycisk generowania rekomendacji
        self.recommend_btn = PrimaryButton("Generuj rekomendacje")
        self.recommend_btn.setMinimumHeight(35)
        
        # Dodanie kart i przycisku do lewej kolumny
        left_column.addWidget(data_card)
        left_column.addWidget(trail_params_card)
        left_column.addWidget(weather_prefs_card)
        left_column.addWidget(self.recommend_btn)
        left_column.addStretch()
        
        # Dodanie kontenera do obszaru przewijania
        left_scroll_area.setWidget(left_container)
        
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
        content_layout.addWidget(left_scroll_area, 1)
        content_layout.addLayout(right_column, 2)
        
        layout.addLayout(content_layout)
    
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
            logger.info(f"Wczytano {len(self.trail_data.trails)} tras z pliku {filepath}")
            
            # Aktualizacja rekomendatora jeśli są dane pogodowe
            if hasattr(self, 'weather_data') and self.weather_data.records:
                self.recommender = RouteRecommender(self.trail_data, self.weather_data)
            
            QMessageBox.information(self, "Sukces", "Dane o trasach zostały wczytane pomyślnie!")
        except Exception as e:
            logger.error(f"Nie udało się wczytać danych tras: {str(e)}")
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
            logger.info(f"Wczytano {len(self.weather_data.records)} rekordów pogodowych z pliku {filepath}")
            
            # Aktualizacja rekomendatora jeśli są dane o trasach
            if hasattr(self, 'trail_data') and self.trail_data.trails:
                self.recommender = RouteRecommender(self.trail_data, self.weather_data)
            
            QMessageBox.information(self, "Sukces", "Dane pogodowe zostały wczytane pomyślnie!")
        except Exception as e:
            logger.error(f"Nie udało się wczytać danych pogodowych: {str(e)}")
            QMessageBox.critical(self, "Błąd", f"Nie udało się wczytać danych: {str(e)}")
    
    def generate_recommendations(self):
        """Generuje rekomendacje tras na podstawie preferencji użytkownika."""
        logger.info("--- ROZPOCZĘCIE GENEROWANIA REKOMENDACJI ---")
        
        # Pokazujemy komunikat oczekiwania
        self.no_results_label.setText("Generowanie rekomendacji, proszę czekać...")
        self.no_results_label.setVisible(True)
        self.repaint()  # Wymuszenie odświeżenia interfejsu
        logger.debug("Interfejs zaktualizowany - wyświetlenie komunikatu oczekiwania")
        
        # Utworzenie pętli zdarzeń, która pozwoli na odświeżenie interfejsu
        loop = QEventLoop()
        QTimer.singleShot(100, loop.quit)
        loop.exec()
        
        # Sprawdzanie danych wejściowych
        if not self.trail_data.trails:
            logger.warn("Brak danych o trasach")
            QMessageBox.warning(self, "Ostrzeżenie", "Brak danych o trasach!")
            self.no_results_label.setText("Wczytaj dane o trasach i dane pogodowe, a następnie kliknij 'Generuj rekomendacje'.")
            return
        else:
            logger.debug(f"Liczba tras: {len(self.trail_data.trails)}")
        
        if not self.weather_data.records:
            logger.warn("Brak danych pogodowych")
            QMessageBox.warning(self, "Ostrzeżenie", "Brak danych pogodowych!")
            self.no_results_label.setText("Wczytaj dane o trasach i dane pogodowe, a następnie kliknij 'Generuj rekomendacje'.")
            return
        else:
            logger.debug(f"Liczba rekordów pogodowych: {len(self.weather_data.records)}")
        
        # Tworzenie rekomendatora, jeśli nie istnieje
        try:
            if not self.recommender:
                logger.debug("Tworzenie nowego rekomendatora")
                self.recommender = RouteRecommender(self.trail_data, self.weather_data)
            else:
                logger.debug("Użycie istniejącego rekomendatora")
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Błąd podczas tworzenia rekomendatora: {str(e)}")
            logger.debug(f"Szczegóły błędu: {error_details}")
            QMessageBox.critical(self, "Błąd", f"Nie udało się utworzyć rekomendatora: {str(e)}")
            self.no_results_label.setText("Wystąpił błąd podczas generowania rekomendacji. Spróbuj ponownie.")
            return
        
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
        
        logger.debug(f"Parametry tras: {trail_params}")
        
        # Preferencje pogodowe
        weather_preferences = {
            'min_temp': self.min_temp.value(),
            'max_temp': self.max_temp.value(),
            'max_precipitation': self.max_precip.value(),
            'min_sunshine_hours': self.min_sunshine.value()
        }
        
        logger.debug(f"Preferencje pogodowe: {weather_preferences}")
        
        # Zakres dat
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        logger.debug(f"Zakres dat: {start_date} - {end_date}")
        
        # Sprawdzenie poprawności dat
        if start_date > end_date:
            logger.warn("Niepoprawny zakres dat")
            QMessageBox.warning(self, "Ostrzeżenie", "Data początkowa nie może być późniejsza niż data końcowa!")
            self.no_results_label.setText("Wybierz poprawny zakres dat i spróbuj ponownie.")
            return
        
        # Wyłączanie przycisku rekomendacji podczas przetwarzania
        logger.debug("Wyłączanie przycisku rekomendacji")
        self.recommend_btn.setEnabled(False)
        self.repaint()  # Wymuszenie odświeżenia interfejsu
        
        # Utworzenie pętli zdarzeń, która pozwoli na odświeżenie interfejsu
        loop = QEventLoop()
        QTimer.singleShot(100, loop.quit)
        loop.exec()
        
        try:
            # Generowanie rekomendacji
            logger.info("Rozpoczęcie generowania rekomendacji")
            recommendations = []
            
            # Prosty trick - zamiast skomplikowanego wątku, po prostu generujemy rekomendacje bezpośrednio
            # ale w małych krokach, aktualizując interfejs
            
            # Krok 1: Filtrowanie tras
            logger.debug("Filtrowanie tras")
            self.no_results_label.setText("Filtrowanie tras...")
            self.repaint()
            
            filtered_trails = self.recommender.filter_trails_by_params(**trail_params)
            if not filtered_trails:
                self.recommend_btn.setEnabled(True)
                self.no_results_label.setText("Brak tras spełniających podane kryteria.")
                return
            
            # Krok 2: Ocenianie tras
            logger.debug("Ocenianie tras")
            self.no_results_label.setText("Analizowanie tras i pogody...")
            self.repaint()
            
            scored_trails = []
            for i, trail in enumerate(filtered_trails[:30]): # Ograniczamy do 30 tras dla wydajności
                try:
                    score = self.recommender._calculate_weather_score(
                        trail.region,
                        (start_date, end_date),
                        **weather_preferences
                    )
                    scored_trails.append({
                        'trail': trail,
                        'score': score
                    })
                    
                    # Co 5 tras odświeżamy interfejs, aby pozostał responsywny
                    if i % 5 == 0:
                        self.no_results_label.setText(f"Analizowanie tras i pogody... ({i+1}/{min(30, len(filtered_trails))})")
                        self.repaint()
                        loop = QEventLoop()
                        QTimer.singleShot(10, loop.quit)
                        loop.exec()
                    
                except Exception as e:
                    logger.error(f"Błąd podczas oceniania trasy {trail.name}: {str(e)}")
            
            # Posortuj trasy według oceny
            logger.debug("Sortowanie tras")
            self.no_results_label.setText("Sortowanie wyników...")
            self.repaint()
            
            scored_trails.sort(key=lambda x: x['score'], reverse=True)
            
            # Przygotuj wyniki
            logger.debug("Przygotowanie wyników")
            self.no_results_label.setText("Przygotowanie wyników...")
            self.repaint()
            
            recommendations = []
            for i, item in enumerate(scored_trails[:10]):  # Bierzemy 10 najlepszych
                trail = item['trail']
                recommendations.append({
                    'id': trail.id,
                    'name': trail.name,
                    'region': trail.region,
                    'length_km': trail.length_km,
                    'difficulty': trail.difficulty,
                    'terrain_type': trail.terrain_type,
                    'elevation_gain': trail.elevation_gain,
                    'weather_score': item['score'],
                    'total_score': item['score']
                })
            
            # Wyświetlenie wyników
            logger.debug("Wyświetlanie wyników")
            self._display_recommendations(recommendations)
            
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Błąd podczas generowania rekomendacji: {str(e)}")
            logger.debug(f"Szczegóły błędu: {error_details}")
            self.recommend_btn.setEnabled(True)
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd podczas generowania rekomendacji: {str(e)}")
            self.no_results_label.setText("Wystąpił błąd podczas generowania rekomendacji. Spróbuj ponownie.")
            
        finally:
            # Włączenie przycisku rekomendacji
            self.recommend_btn.setEnabled(True)
    
    def _display_recommendations(self, recommendations):
        """Wyświetla wygenerowane rekomendacje w atrakcyjnej formie."""
        try:
            # Czyszczenie poprzednich rekomendacji
            logger.debug("Czyszczenie poprzednich rekomendacji")
            self._clear_recommendations()
            
            # Sprawdzenie, czy znaleziono rekomendacje
            if not recommendations:
                logger.debug("Nie znaleziono rekomendacji")
                self.no_results_label.setText("Nie znaleziono tras spełniających podane kryteria.")
                self.no_results_label.setVisible(True)
                # Dodanie stretch na końcu, aby elementy były na górze
                self.results_layout.addStretch()
                return
            
            # Ukrycie etykiety "brak wyników"
            logger.info(f"Znaleziono {len(recommendations)} rekomendacji")
            self.no_results_label.setVisible(False)
            
            # Dodanie podsumowania
            summary_label = StyledLabel(f"Znaleziono {len(recommendations)} tras, które odpowiadają Twoim preferencjom.")
            summary_label.setWordWrap(True)
            summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = summary_label.font()
            font.setBold(True)
            summary_label.setFont(font)
            self.results_layout.insertWidget(1, summary_label)
            
            # Dodawanie kart dla każdej rekomendacji
            for i, rec in enumerate(recommendations):
                # Tworzenie karty dla rekomendacji
                card = CardFrame()
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(15, 15, 15, 15)
                card_layout.setSpacing(8)
                
                # Nagłówek z numerem i nazwą
                header_layout = QHBoxLayout()
                rank_label = StyledLabel(f"#{i+1}.")
                rank_font = rank_label.font()
                rank_font.setBold(True)
                rank_font.setPointSize(14)
                rank_label.setFont(rank_font)
                
                name_label = StyledLabel(rec['name'])
                name_font = name_label.font()
                name_font.setBold(True)
                name_font.setPointSize(14)
                name_label.setFont(name_font)
                
                header_layout.addWidget(rank_label)
                header_layout.addWidget(name_label)
                header_layout.addStretch()
                
                # Ocena
                score_label = StyledLabel(f"{rec['total_score']:.1f}/100")
                score_font = score_label.font()
                score_font.setBold(True)
                score_font.setPointSize(14)
                score_label.setFont(score_font)
                header_layout.addWidget(score_label)
                
                card_layout.addLayout(header_layout)
                
                # Separator
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setFrameShadow(QFrame.Shadow.Sunken)
                card_layout.addWidget(line)
                
                # Informacje o trasie
                info_layout = QGridLayout()
                info_layout.setVerticalSpacing(8)
                info_layout.setHorizontalSpacing(15)
                
                # Region
                info_layout.addWidget(StyledLabel("Region:"), 0, 0)
                region_label = StyledLabel(rec['region'])
                region_font = region_label.font()
                region_font.setBold(True)
                region_label.setFont(region_font)
                info_layout.addWidget(region_label, 0, 1)
                
                # Długość
                info_layout.addWidget(StyledLabel("Długość:"), 1, 0)
                length_label = StyledLabel(f"{rec['length_km']:.1f} km")
                length_font = length_label.font()
                length_font.setBold(True)
                length_label.setFont(length_font)
                info_layout.addWidget(length_label, 1, 1)
                
                # Trudność
                info_layout.addWidget(StyledLabel("Trudność:"), 0, 2)
                difficulty_label = StyledLabel(str(rec['difficulty']))
                difficulty_font = difficulty_label.font()
                difficulty_font.setBold(True)
                difficulty_label.setFont(difficulty_font)
                info_layout.addWidget(difficulty_label, 0, 3)
                
                # Typ terenu
                if 'terrain_type' in rec and rec['terrain_type']:
                    info_layout.addWidget(StyledLabel("Typ terenu:"), 1, 2)
                    info_layout.addWidget(StyledLabel(rec['terrain_type']), 1, 3)
                
                # Przewyższenie
                if 'elevation_gain' in rec and rec['elevation_gain']:
                    info_layout.addWidget(StyledLabel("Przewyższenie:"), 2, 0)
                    info_layout.addWidget(StyledLabel(f"{rec['elevation_gain']} m"), 2, 1)
                
                card_layout.addLayout(info_layout)
                
                # Dodanie karty do układu wyników
                self.results_layout.insertWidget(i + 2, card)
            
            # Dodanie stretch na końcu, aby zachować spójność układu
            self.results_layout.addStretch()
            
            logger.info("Wyświetlenie rekomendacji zakończone")
            
        except Exception as e:
            error_details = traceback.format_exc()
            logger.error(f"Błąd podczas wyświetlania wyników: {str(e)}")
            logger.debug(f"Szczegóły błędu: {error_details}")
            self.no_results_label.setText("Wystąpił błąd podczas wyświetlania wyników.")
            self.no_results_label.setVisible(True)
            
            # Informujemy użytkownika o wyniku, nawet jeśli nie możemy wyświetlić wszystkich szczegółów
            if recommendations:
                QMessageBox.information(self, "Wyniki wyszukiwania", 
                    f"Znaleziono {len(recommendations)} tras.")
                
    def _clear_recommendations(self):
        """Usuwa wszystkie karty rekomendacji."""
        # Usunięcie wszystkich widgetów poza etykietą tytułową i "brak wyników"
        for i in range(self.results_layout.count() - 1, 1, -1):
            item = self.results_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None and widget is not self.no_results_label:
                    self.results_layout.removeWidget(widget)
                    widget.deleteLater()
                else:
                    # Jeśli to nie widget (np. stretch), usuń również
                    self.results_layout.removeItem(item) 