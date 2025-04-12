"""
Strona rekomendacji tras turystycznych.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QGridLayout,
    QScrollArea, QFileDialog, QPushButton, QLabel
)
from PyQt6.QtCore import Qt, QTimer, QEventLoop
import traceback
import sys
sys.path.append('.')
from src.core import ( TrailData, WeatherData, RouteRecommender )
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
        self.difficulty = self.trail_params_form.add_combo_field(
            "difficulty",
            "Poziom trudności",
            ["Wszystkie", "1", "2", "3", "4", "5"]
        )
        
        # Region
        self.region = self.trail_params_form.add_combo_field(
            "region",
            "Region",
            ["Wszystkie"]
        )
        
        left_column.addWidget(self.trail_params_form)
        
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
        
        left_column.addWidget(self.weather_params_form)
        
        # Przycisk generowania rekomendacji
        self.recommend_btn = QPushButton("Generuj rekomendacje")
        self.recommend_btn.setMinimumHeight(35)
        self.recommend_btn.clicked.connect(self.generate_recommendations)
        left_column.addWidget(self.recommend_btn)
        
        # Prawa kolumna - wyniki
        right_column = QVBoxLayout()
        
        # Tabela wyników - zastąpimy ją layoutem z przewijaniem
        results_label = StyledLabel("Rekomendowane trasy:", is_title=False)
        right_column.addWidget(results_label)
        
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
    
    def _connect_signals(self):
        """Połączenie sygnałów z slotami."""
        self.load_trails_btn.clicked.connect(self.load_trail_data)
        self.load_weather_btn.clicked.connect(self.load_weather_data)
    
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
            summary_label = QLabel(f"Znaleziono {len(recommendations)} tras, które odpowiadają Twoim preferencjom.")
            summary_label.setWordWrap(True)
            summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            font = summary_label.font()
            font.setBold(True)
            summary_label.setFont(font)
            self.results_layout.insertWidget(1, summary_label)
            
            # Dodawanie kart dla każdej rekomendacji
            self.result_cards = []
            for i, rec in enumerate(recommendations):
                # Tworzenie karty dla rekomendacji
                card = ResultCard(self)
                card.set_data(rec, i+1)
                
                # Dodanie karty do układu wyników
                self.results_layout.insertWidget(i + 2, card)
                self.result_cards.append(card)
            
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
        
        # Czyścimy listę kart
        self.result_cards = [] 