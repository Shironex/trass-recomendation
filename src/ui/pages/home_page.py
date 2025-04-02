"""
Strona główna aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt

import sys
sys.path.append('.')
from src.ui.components import (
    StyledLabel, PrimaryButton, CardFrame
)


class HomePage(QWidget):
    """Strona główna aplikacji."""
    
    def __init__(self, parent=None):
        """Inicjalizacja strony głównej."""
        super().__init__(parent)
        self.main_window = parent
        self._setup_ui()
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        # Główny układ
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Tytuł
        title = StyledLabel("Rekomendator Tras Turystycznych", is_title=True)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Opis
        description = StyledLabel(
            "Witaj w aplikacji do rekomendowania tras turystycznych na podstawie "
            "preferencji pogodowych i parametrów trasy. Wybierz jedną z opcji poniżej."
        )
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Karty z akcjami
        cards_layout = QGridLayout()
        cards_layout.setSpacing(15)
        
        # Karta zarządzania trasami
        trail_card = self._create_card(
            "Zarządzanie Trasami",
            "Wczytaj, przeglądaj i filtruj dane o trasach turystycznych.",
            "show_trail_page"
        )
        cards_layout.addWidget(trail_card, 0, 0)
        
        # Karta danych pogodowych
        weather_card = self._create_card(
            "Dane Pogodowe",
            "Wczytaj i analizuj dane pogodowe dla różnych lokalizacji.",
            "show_weather_page"
        )
        cards_layout.addWidget(weather_card, 0, 1)
        
        # Karta rekomendacji
        recommendation_card = self._create_card(
            "Rekomendacje Tras",
            "Otrzymaj rekomendacje tras na podstawie preferencji pogodowych.",
            "show_recommendation_page"
        )
        cards_layout.addWidget(recommendation_card, 1, 0, 1, 2)
        
        layout.addLayout(cards_layout)
        layout.addStretch()
    
    def _create_card(self, title, description, action):
        """
        Tworzy kartę z tytułem, opisem i przyciskiem.
        
        Args:
            title: Tytuł karty.
            description: Opis karty.
            action: Nazwa metody do wywołania po kliknięciu przycisku.
            
        Returns:
            Obiekt CardFrame z zawartością.
        """
        card = CardFrame()
        card_layout = QVBoxLayout(card)
        
        # Tytuł karty
        card_title = StyledLabel(title)
        font = card_title.font()
        font.setPointSize(14)
        font.setBold(True)
        card_title.setFont(font)
        card_layout.addWidget(card_title)
        
        # Opis karty
        card_description = StyledLabel(description)
        card_description.setWordWrap(True)
        card_layout.addWidget(card_description)
        
        # Przycisk karty
        button_text = "Przejdź"
        button = PrimaryButton(button_text)
        button.setMinimumHeight(40)
        
        # Połączenie przycisku z odpowiednią metodą
        if action == "show_trail_page" and self.main_window:
            button.clicked.connect(self.main_window.show_trail_page)
        elif action == "show_weather_page" and self.main_window:
            button.clicked.connect(self.main_window.show_weather_page)
        elif action == "show_recommendation_page" and self.main_window:
            button.clicked.connect(self.main_window.show_recommendation_page)
        
        card_layout.addWidget(button)
        card_layout.addStretch()
        
        return card 