"""
Komponent karty wyników dla aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QFrame
)
from PyQt6.QtCore import Qt


class ResultCard(QGroupBox):
    """
    Karta wyświetlająca pojedynczy wynik rekomendacji.
    """
    
    def __init__(self, parent=None):
        """
        Inicjalizacja karty wyników.
        
        Args:
            parent: Rodzic widgetu.
        """
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Ustawienie stylów - ciemny motyw
        self.setStyleSheet("""
            QGroupBox {
                background-color: #333333;
                border: 1px solid #555555;
                border-radius: 8px;
                margin-top: 10px;
                color: #e0e0e0;
            }
            QLabel {
                color: #e0e0e0;
            }
        """)
        
        # Główny układ
        self.card_layout = QVBoxLayout(self)
        self.card_layout.setContentsMargins(15, 15, 15, 15)
        self.card_layout.setSpacing(8)
        
        # Nagłówek z numerem i nazwą
        self.header_layout = QHBoxLayout()
        
        self.rank_label = QLabel()
        rank_font = self.rank_label.font()
        rank_font.setBold(True)
        rank_font.setPointSize(14)
        self.rank_label.setFont(rank_font)
        self.rank_label.setStyleSheet("color: #3a7ca5;")  # Niebieski akcent
        
        self.name_label = QLabel()
        name_font = self.name_label.font()
        name_font.setBold(True)
        name_font.setPointSize(14)
        self.name_label.setFont(name_font)
        
        self.header_layout.addWidget(self.rank_label)
        self.header_layout.addWidget(self.name_label)
        self.header_layout.addStretch()
        
        # Ocena
        self.score_label = QLabel()
        score_font = self.score_label.font()
        score_font.setBold(True)
        score_font.setPointSize(14)
        self.score_label.setFont(score_font)
        self.score_label.setStyleSheet("color: #4CAF50;")  # Zielony dla wyniku
        self.header_layout.addWidget(self.score_label)
        
        self.card_layout.addLayout(self.header_layout)
        
        # Separator
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setStyleSheet("background-color: #555555;")
        self.card_layout.addWidget(self.line)
        
        # Informacje o trasie
        self.info_layout = QGridLayout()
        self.info_layout.setVerticalSpacing(8)
        self.info_layout.setHorizontalSpacing(15)
        
        # Etykiety dla regionu, długości, trudności, itd.
        self.field_labels = []
        
        region_label = QLabel("Region:")
        region_label.setStyleSheet("color: #aaaaaa;")  # Jasnoszary dla etykiet
        self.field_labels.append(region_label)
        self.info_layout.addWidget(region_label, 0, 0)
        
        self.region_label = QLabel()
        region_font = self.region_label.font()
        region_font.setBold(True)
        self.region_label.setFont(region_font)
        self.info_layout.addWidget(self.region_label, 0, 1)
        
        length_label = QLabel("Długość:")
        length_label.setStyleSheet("color: #aaaaaa;")
        self.field_labels.append(length_label)
        self.info_layout.addWidget(length_label, 1, 0)
        
        self.length_label = QLabel()
        length_font = self.length_label.font()
        length_font.setBold(True)
        self.length_label.setFont(length_font)
        self.info_layout.addWidget(self.length_label, 1, 1)
        
        difficulty_label = QLabel("Trudność:")
        difficulty_label.setStyleSheet("color: #aaaaaa;")
        self.field_labels.append(difficulty_label)
        self.info_layout.addWidget(difficulty_label, 0, 2)
        
        self.difficulty_label = QLabel()
        difficulty_font = self.difficulty_label.font()
        difficulty_font.setBold(True)
        self.difficulty_label.setFont(difficulty_font)
        self.info_layout.addWidget(self.difficulty_label, 0, 3)
        
        terrain_label = QLabel("Typ terenu:")
        terrain_label.setStyleSheet("color: #aaaaaa;")
        self.field_labels.append(terrain_label)
        self.info_layout.addWidget(terrain_label, 1, 2)
        
        self.terrain_label = QLabel()
        self.info_layout.addWidget(self.terrain_label, 1, 3)
        
        elev_label = QLabel("Przewyższenie:")
        elev_label.setStyleSheet("color: #aaaaaa;")
        self.field_labels.append(elev_label)
        self.info_layout.addWidget(elev_label, 2, 0)
        
        self.elevation_label = QLabel()
        self.info_layout.addWidget(self.elevation_label, 2, 1)
        
        self.card_layout.addLayout(self.info_layout)
        
        # Efekt najechania myszą
        self.setObjectName("resultCard")
        self.setStyleSheet(self.styleSheet() + """
            #resultCard:hover {
                background-color: #3a4047;
                border: 1px solid #3a7ca5;
            }
        """)
    
    def set_data(self, data, rank=1):
        """
        Ustawia dane do wyświetlenia.
        
        Args:
            data: Słownik z danymi o trasie.
            rank: Pozycja w rankingu.
        """
        # Ustawienie nagłówka
        self.rank_label.setText(f"#{rank}.")
        self.name_label.setText(data.get('name', 'Brak nazwy'))
        
        # Ustawienie oceny
        score = data.get('total_score', 0)
        self.score_label.setText(f"{score:.1f}/100")
        
        # Kolorowanie oceny w zależności od wartości
        if score >= 75:
            self.score_label.setStyleSheet("color: #4CAF50;")  # Zielony
        elif score >= 50:
            self.score_label.setStyleSheet("color: #FFC107;")  # Żółty/pomarańczowy
        else:
            self.score_label.setStyleSheet("color: #F44336;")  # Czerwony
        
        # Ustawienie danych trasy
        self.region_label.setText(data.get('region', 'Nieznany'))
        self.length_label.setText(f"{data.get('length_km', 0):.1f} km")
        self.difficulty_label.setText(str(data.get('difficulty', 'Nieznana')))
        
        # Opcjonalne dane
        if 'terrain_type' in data and data['terrain_type']:
            self.terrain_label.setText(data['terrain_type'])
        else:
            self.terrain_label.setText("Nieznany")
            
        if 'elevation_gain' in data and data['elevation_gain']:
            self.elevation_label.setText(f"{data['elevation_gain']} m")
        else:
            self.elevation_label.setText("Brak danych")
    
    def clear(self):
        """Czyści wszystkie dane."""
        self.rank_label.setText("")
        self.name_label.setText("")
        self.score_label.setText("")
        self.region_label.setText("")
        self.length_label.setText("")
        self.difficulty_label.setText("")
        self.terrain_label.setText("")
        self.elevation_label.setText("") 