"""
Strona główna aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from PyQt6.QtCore import Qt

import sys
sys.path.append('.')
from src.ui.components import (
    StyledLabel, PrimaryButton, CardFrame
)
from src.utils import logger


class HomePage(QWidget):
    """Strona główna aplikacji."""
    
    def __init__(self, parent=None):
        """Inicjalizacja strony głównej."""
        super().__init__(parent)
        self.main_window = parent
        logger.debug("Inicjalizacja strony głównej")
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
            "Uzyskaj rekomendacje tras dopasowanych do Twoich preferencji.",
            "show_recommendation_page"
        )
        cards_layout.addWidget(recommendation_card, 1, 0, 1, 2)
        
        layout.addLayout(cards_layout)
        layout.addStretch(1)
        
        logger.debug("Interfejs strony głównej skonfigurowany")
    
    def _create_card(self, title, description, action):
        """
        Tworzy kartę z akcją.
        
        Args:
            title (str): Tytuł karty
            description (str): Opis akcji
            action (str): Nazwa metody do wywołania po kliknięciu
            
        Returns:
            CardFrame: Karta z przyciskiem akcji
        """
        card = CardFrame()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(15, 15, 15, 15)
        card_layout.setSpacing(15)
        
        # Tytuł karty
        title_label = StyledLabel(title)
        font = title_label.font()
        font.setBold(True)
        font.setPointSize(12)
        title_label.setFont(font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title_label)
        
        # Opis
        desc_label = StyledLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(desc_label)
        
        # Przycisk
        btn_text = "Przejdź" 
        button = PrimaryButton(btn_text)
        button.setMinimumHeight(40)
        
        # Połączenie przycisku z akcją
        if hasattr(self.main_window, action):
            button.clicked.connect(getattr(self.main_window, action))
            logger.debug(f"Utworzono kartę '{title}' z akcją '{action}'")
        
        card_layout.addWidget(button)
        return card 