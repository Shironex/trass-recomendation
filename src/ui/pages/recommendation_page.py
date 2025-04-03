"""
Strona rekomendacji tras turystycznych.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QMessageBox, QGridLayout,
    QScrollArea, QFileDialog, QFrame, QGroupBox, QFormLayout, QDateEdit,
    QPushButton, QComboBox, QSlider, QLabel, QTableWidget, QHeaderView,
    QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QTimer, QEventLoop, QDate
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
        self.parent = parent
        self.trail_data = TrailData()
        self.weather_data = WeatherData()
        self.recommender = None
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Główny układ
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Tytuł strony
        title_label = QLabel("Rekomendacje Tras Turystycznych")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Grupa danych
        data_group = QGroupBox("Dane")
        main_layout.addWidget(data_group)
        data_layout = QFormLayout(data_group)
        
        # Przyciski ładowania danych
        data_btn_layout = QHBoxLayout()
        self.load_trails_btn = QPushButton("Wczytaj dane o trasach")
        self.load_weather_btn = QPushButton("Wczytaj dane pogodowe") 
        data_btn_layout.addWidget(self.load_trails_btn)
        data_btn_layout.addWidget(self.load_weather_btn)
        data_layout.addRow("", data_btn_layout)
        
        # Status danych
        status_layout = QGridLayout()
        status_layout.addWidget(QLabel("Trasy:"), 0, 0)
        self.trails_status = QLabel("Nie wczytano")
        status_layout.addWidget(self.trails_status, 0, 1)
        
        status_layout.addWidget(QLabel("Dane pogodowe:"), 1, 0)
        self.weather_status = QLabel("Nie wczytano")
        status_layout.addWidget(self.weather_status, 1, 1)
        data_layout.addRow("Status:", status_layout)
        
        # Sekcja parametrów wyszukiwania
        main_content = QHBoxLayout()
        main_layout.addLayout(main_content)
        
        # Lewa kolumna - parametry
        left_column = QVBoxLayout()
        
        # Grupa parametrów tras
        trail_params_group = QGroupBox("Parametry tras")
        trail_params_layout = QFormLayout(trail_params_group)
        
        # Długość trasy
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Min:"))
        self.min_length = QDoubleSpinBox()
        self.min_length.setRange(0, 1000)
        length_layout.addWidget(self.min_length)
        
        length_layout.addWidget(QLabel("Max:"))
        self.max_length = QDoubleSpinBox()
        self.max_length.setRange(0, 1000)
        self.max_length.setValue(50)
        length_layout.addWidget(self.max_length)
        trail_params_layout.addRow("Długość trasy (km):", length_layout)
        
        # Poziom trudności
        self.difficulty = QComboBox()
        self.difficulty.addItem("Wszystkie")
        for i in range(1, 6):
            self.difficulty.addItem(str(i))
        trail_params_layout.addRow("Poziom trudności:", self.difficulty)
        
        # Region
        self.region = QComboBox()
        self.region.addItem("Wszystkie")
        trail_params_layout.addRow("Region:", self.region)
        
        left_column.addWidget(trail_params_group)
        
        # Grupa preferencji pogodowych
        weather_prefs_group = QGroupBox("Preferencje pogodowe")
        weather_prefs_layout = QFormLayout(weather_prefs_group)
        
        # Temperatura
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Min:"))
        self.min_temp = QDoubleSpinBox()
        self.min_temp.setRange(-20, 40)
        self.min_temp.setValue(15)
        temp_layout.addWidget(self.min_temp)
        
        temp_layout.addWidget(QLabel("Max:"))
        self.max_temp = QDoubleSpinBox()
        self.max_temp.setRange(-20, 40)
        self.max_temp.setValue(25)
        temp_layout.addWidget(self.max_temp)
        weather_prefs_layout.addRow("Temperatura (°C):", temp_layout)
        
        # Maksymalne opady
        self.max_precip = QDoubleSpinBox()
        self.max_precip.setRange(0, 100)
        self.max_precip.setValue(5)
        weather_prefs_layout.addRow("Maksymalne opady (mm):", self.max_precip)
        
        # Minimalne nasłonecznienie
        self.min_sunshine = QDoubleSpinBox()
        self.min_sunshine.setRange(0, 24)
        self.min_sunshine.setValue(4)
        weather_prefs_layout.addRow("Min. nasłonecznienie (h):", self.min_sunshine)
        
        # Zakres dat
        date_layout = QHBoxLayout()
        
        date_layout.addWidget(QLabel("Od:"))
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("Do:"))
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(self.end_date.date().addDays(7))
        date_layout.addWidget(self.end_date)
        
        weather_prefs_layout.addRow("Planowany termin:", date_layout)
        
        left_column.addWidget(weather_prefs_group)
        
        # Przycisk generowania rekomendacji
        self.recommend_btn = QPushButton("Generuj rekomendacje")
        self.recommend_btn.setMinimumHeight(35)
        left_column.addWidget(self.recommend_btn)
        
        # Prawa kolumna - wyniki
        right_column = QVBoxLayout()
        
        # Tabela wyników - zastąpimy ją layoutem z przewijaniem
        results_label = QLabel("Rekomendowane trasy:")
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
        self.recommend_btn.clicked.connect(self.generate_recommendations)
    
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
            for i, rec in enumerate(recommendations):
                # Tworzenie karty dla rekomendacji
                card = QGroupBox()
                card_layout = QVBoxLayout(card)
                card_layout.setContentsMargins(15, 15, 15, 15)
                card_layout.setSpacing(8)
                
                # Nagłówek z numerem i nazwą
                header_layout = QHBoxLayout()
                rank_label = QLabel(f"#{i+1}.")
                rank_font = rank_label.font()
                rank_font.setBold(True)
                rank_font.setPointSize(14)
                rank_label.setFont(rank_font)
                
                name_label = QLabel(rec['name'])
                name_font = name_label.font()
                name_font.setBold(True)
                name_font.setPointSize(14)
                name_label.setFont(name_font)
                
                header_layout.addWidget(rank_label)
                header_layout.addWidget(name_label)
                header_layout.addStretch()
                
                # Ocena
                score_label = QLabel(f"{rec['total_score']:.1f}/100")
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
                info_layout.addWidget(QLabel("Region:"), 0, 0)
                region_label = QLabel(rec['region'])
                region_font = region_label.font()
                region_font.setBold(True)
                region_label.setFont(region_font)
                info_layout.addWidget(region_label, 0, 1)
                
                # Długość
                info_layout.addWidget(QLabel("Długość:"), 1, 0)
                length_label = QLabel(f"{rec['length_km']:.1f} km")
                length_font = length_label.font()
                length_font.setBold(True)
                length_label.setFont(length_font)
                info_layout.addWidget(length_label, 1, 1)
                
                # Trudność
                info_layout.addWidget(QLabel("Trudność:"), 0, 2)
                difficulty_label = QLabel(str(rec['difficulty']))
                difficulty_font = difficulty_label.font()
                difficulty_font.setBold(True)
                difficulty_label.setFont(difficulty_font)
                info_layout.addWidget(difficulty_label, 0, 3)
                
                # Typ terenu
                if 'terrain_type' in rec and rec['terrain_type']:
                    info_layout.addWidget(QLabel("Typ terenu:"), 1, 2)
                    info_layout.addWidget(QLabel(rec['terrain_type']), 1, 3)
                
                # Przewyższenie
                if 'elevation_gain' in rec and rec['elevation_gain']:
                    info_layout.addWidget(QLabel("Przewyższenie:"), 2, 0)
                    info_layout.addWidget(QLabel(f"{rec['elevation_gain']} m"), 2, 1)
                
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