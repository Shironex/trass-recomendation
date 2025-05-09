"""
Komponent karty wyników dla aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QLabel, QFrame, QPushButton
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
        
        self.title_label = QLabel()
        title_font = self.title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(14)
        self.title_label.setFont(title_font)
        
        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()
        
        # Ocena (będzie dodana w funkcji add_detail z parametrem is_highlighted=True)
        
        self.card_layout.addLayout(self.header_layout)
        
        # Separator
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setStyleSheet("background-color: #555555;")
        self.card_layout.addWidget(self.line)
        
        # Informacje o trasie - teraz używamy QGridLayout z dynamiczną liczbą wierszy
        self.info_layout = QGridLayout()
        self.info_layout.setVerticalSpacing(8)
        self.info_layout.setHorizontalSpacing(15)
        self.info_layout.setColumnStretch(1, 1)
        self.info_layout.setColumnStretch(3, 1)
        
        self.detail_labels = {}  # Słownik na etykiety z wartościami
        self.current_row = 0
        self.current_col = 0
        
        self.card_layout.addLayout(self.info_layout)
        
        # Miejsce na przyciski
        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(10)
        self.buttons_layout.addStretch()
        
        self.card_layout.addLayout(self.buttons_layout)
        
        # Efekt najechania myszą
        self.setObjectName("resultCard")
        self.setStyleSheet(self.styleSheet() + """
            #resultCard:hover {
                background-color: #3a4047;
                border: 1px solid #3a7ca5;
            }
        """)
    
    def set_title(self, title):
        """Ustawia tytuł karty."""
        self.title_label.setText(title)
    
    def add_detail(self, label_text, value_text, is_highlighted=False):
        """
        Dodaje parę etykieta-wartość do karty.
        
        Args:
            label_text: Tekst etykiety.
            value_text: Tekst wartości.
            is_highlighted: Czy wartość ma być wyróżniona.
        """
        # Etykieta
        label = QLabel(f"{label_text}:")
        label.setStyleSheet("color: #aaaaaa;")  # Jasnoszary dla etykiet
        
        # Wartość
        value = QLabel(value_text)
        value_font = value.font()
        value_font.setBold(True)
        value.setFont(value_font)
        
        if is_highlighted:
            # Jeśli to ocena całkowita, dodajemy ją do nagłówka
            value.setStyleSheet("color: #4CAF50;")  # Zielony dla wyniku
            
            # Kolorowanie oceny w zależności od wartości
            try:
                score = float(value_text.split('/')[0])
                if score >= 75:
                    value.setStyleSheet("color: #4CAF50;")  # Zielony
                elif score >= 50:
                    value.setStyleSheet("color: #FFC107;")  # Żółty/pomarańczowy
                else:
                    value.setStyleSheet("color: #F44336;")  # Czerwony
            except:
                # Jeśli nie można przekonwertować do float, używamy domyślnego koloru
                pass
            
            # Dodajemy do nagłówka
            self.header_layout.addWidget(value)
        else:
            # Dodajemy do siatki informacji
            # Określamy, czy dodać do lewej czy prawej kolumny
            col = self.current_col * 2  # 0 lub 2
            
            # Dodanie etykiety i wartości do siatki
            self.info_layout.addWidget(label, self.current_row, col)
            self.info_layout.addWidget(value, self.current_row, col + 1)
            
            # Zapisanie referencji do etykiety wartości
            self.detail_labels[label_text] = value
            
            # Aktualizacja pozycji dla następnej etykiety
            self.current_col = (self.current_col + 1) % 2
            if self.current_col == 0:
                self.current_row += 1
    
    def add_button(self, button):
        """
        Dodaje przycisk do karty.
        
        Args:
            button: Obiekt QPushButton do dodania.
        """
        self.buttons_layout.insertWidget(self.buttons_layout.count() - 1, button)
    
    def set_data(self, data, rank=1):
        """
        Ustawia dane do wyświetlenia (stara metoda dla kompatybilności wstecznej).
        
        Args:
            data: Słownik z danymi o trasie.
            rank: Pozycja w rankingu.
        """
        # Ustawienie nagłówka
        self.set_title(f"#{rank}. {data.get('name', 'Brak nazwy')}")
        
        # Podstawowe informacje
        self.add_detail("Region", data.get('region', 'Nieznany'))
        self.add_detail("Długość", f"{data.get('length_km', 0):.1f} km")
        self.add_detail("Trudność", f"{data.get('difficulty', 'Nieznana')}/5")
        
        # Opcjonalne dane
        if 'terrain_type' in data and data['terrain_type']:
            self.add_detail("Typ terenu", data['terrain_type'])
            
        if 'elevation_gain' in data and data['elevation_gain']:
            self.add_detail("Przewyższenie", f"{data['elevation_gain']} m")
        
        # Ocena
        score = data.get('total_score', 0)
        self.add_detail("Ocena ogólna", f"{score:.1f}/100", is_highlighted=True)
    
    def clear(self):
        """Czyści wszystkie dane."""
        self.title_label.setText("")
        
        # Usunięcie wszystkich etykiet informacyjnych
        for i in reversed(range(self.info_layout.count())): 
            widget = self.info_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Usunięcie wszystkich przycisków
        for i in reversed(range(self.buttons_layout.count()-1)):  # -1 aby zachować stretch
            item = self.buttons_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        
        # Wyczyszczenie słownika etykiet
        self.detail_labels = {}
        self.current_row = 0
        self.current_col = 0 