"""
Komponenty przycisków UI.
"""

from PyQt6.QtWidgets import QPushButton


class BaseButton(QPushButton):
    """Podstawowy przycisk z formatowaniem."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: #e0e0e0;
                border-radius: 5px;
                padding: 8px 15px;
                border: none;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton:pressed {
                background-color: #333333;
            }
        """)


class PrimaryButton(QPushButton):
    """Przycisk główny z formatowaniem."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        
        self.setStyleSheet("""
            QPushButton {
                background-color: #3a7ca5;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a8cb5;
            }
            QPushButton:pressed {
                background-color: #2a6c95;
            }
        """) 