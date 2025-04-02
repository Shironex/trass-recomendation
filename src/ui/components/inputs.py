"""
Komponenty pól wprowadzania danych UI.
"""

from PyQt6.QtWidgets import (
    QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit, QDateEdit
)
from PyQt6.QtCore import QDate


class StyledComboBox(QComboBox):
    """Niestandardowa lista rozwijana z formatowaniem."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QComboBox {
                background-color: #333333;
                color: #e0e0e0;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid #555555;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox QAbstractItemView {
                background-color: #333333;
                color: #e0e0e0;
                selection-background-color: #3a7ca5;
            }
        """)


class StyledSpinBox(QSpinBox):
    """Niestandardowe pole liczbowe z formatowaniem."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QSpinBox {
                background-color: #333333;
                color: #e0e0e0;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid #555555;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                background-color: #444444;
            }
        """)
        
        self.setRange(0, 1000)


class StyledDoubleSpinBox(QDoubleSpinBox):
    """Niestandardowe pole liczbowe zmiennoprzecinkowe z formatowaniem."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #333333;
                color: #e0e0e0;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid #555555;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                background-color: #444444;
            }
        """)
        
        self.setRange(0, 1000)
        self.setDecimals(1)
        self.setSingleStep(0.5)


class StyledLineEdit(QLineEdit):
    """Niestandardowe pole tekstowe z formatowaniem."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QLineEdit {
                background-color: #333333;
                color: #e0e0e0;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid #555555;
            }
        """)


class StyledDateEdit(QDateEdit):
    """Niestandardowe pole daty z formatowaniem."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QDateEdit {
                background-color: #333333;
                color: #e0e0e0;
                border-radius: 5px;
                padding: 5px;
                border: 1px solid #555555;
            }
            QDateEdit::drop-down {
                border: none;
                width: 20px;
            }
            QCalendarWidget {
                background-color: #333333;
                color: #e0e0e0;
            }
            QCalendarWidget QAbstractItemView {
                background-color: #333333;
                color: #e0e0e0;
                selection-background-color: #3a7ca5;
            }
        """)
        
        self.setDisplayFormat("yyyy-MM-dd")
        self.setDate(QDate.currentDate())
        self.setCalendarPopup(True) 