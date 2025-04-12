"""
Komponent wyświetlania statystyk dla aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt


class StatsDisplay(QGroupBox):
    """
    Komponent do wyświetlania statystyk i podsumowań danych.
    """
    
    def __init__(self, title="Statystyki", parent=None):
        """
        Inicjalizacja komponentu statystyk.
        
        Args:
            title: Tytuł grupy statystyk.
            parent: Rodzic widgetu.
        """
        super().__init__(title, parent)
        self._setup_ui()
        self._stats = {}
    
    def _setup_ui(self):
        """Konfiguracja interfejsu użytkownika."""
        self.layout = QVBoxLayout(self)
        
        # Główna etykieta statystyk
        self.stats_label = QLabel("Brak danych")
        self.stats_label.setWordWrap(True)
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.stats_label)
    
    def update_stats(self, stats_text):
        """
        Aktualizuje wyświetlane statystyki.
        
        Args:
            stats_text: Tekst z podsumowaniem statystyk.
        """
        self.stats_label.setText(stats_text)
    
    def set_stats(self, stats_dict):
        """
        Ustawia statystyki na podstawie słownika wartości.
        
        Args:
            stats_dict: Słownik z danymi statystycznymi.
        """
        self._stats = stats_dict
        
        # Generowanie tekstu statystyk
        stats_text = ""
        for label, value in stats_dict.items():
            stats_text += f"{label}: {value}\n"
        
        # Aktualizacja etykiety
        self.stats_label.setText(stats_text)
    
    def add_section(self, title):
        """
        Dodaje nową sekcję statystyk.
        
        Args:
            title: Tytuł sekcji.
            
        Returns:
            Label sekcji.
        """
        # Dodaj separator jeśli już są jakieś statystyki
        if self.layout.count() > 1:
            separator = QFrame()
            separator.setFrameShape(QFrame.Shape.HLine)
            separator.setFrameShadow(QFrame.Shadow.Sunken)
            self.layout.addWidget(separator)
        
        # Dodaj tytuł sekcji
        section_title = QLabel(title)
        font = section_title.font()
        font.setBold(True)
        section_title.setFont(font)
        self.layout.addWidget(section_title)
        
        # Dodaj label na treść sekcji
        section_content = QLabel()
        section_content.setWordWrap(True)
        section_content.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(section_content)
        
        return section_content
    
    def update_section(self, section_label, stats_dict):
        """
        Aktualizuje sekcję statystyk.
        
        Args:
            section_label: Label sekcji do aktualizacji.
            stats_dict: Słownik z danymi statystycznymi.
        """
        # Generowanie tekstu statystyk
        stats_text = ""
        for label, value in stats_dict.items():
            stats_text += f"{label}: {value}\n"
        
        # Aktualizacja etykiety
        section_label.setText(stats_text)
    
    def clear(self):
        """Czyści wszystkie statystyki."""
        self.stats_label.setText("Brak danych")
        self._stats = {} 