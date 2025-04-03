"""
Komponenty podstawowe UI dla aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import (
    QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
    QDoubleSpinBox, QDateEdit, QHeaderView, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate

class BaseButton(QPushButton):
    """Podstawowy przycisk z podstawową stylizacją."""
    
    def __init__(self, text, parent=None):
        """Inicjalizacja przycisku."""
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px 16px;
                color: #333;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e9ecef;
                border-color: #ced4da;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """)


class PrimaryButton(QPushButton):
    """Przycisk główny z wyróżniającą się stylizacją."""
    
    def __init__(self, text, parent=None):
        """Inicjalizacja przycisku głównego."""
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                border: 1px solid #0069d9;
                border-radius: 4px;
                padding: 8px 16px;
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0069d9;
                border-color: #0062cc;
            }
            QPushButton:pressed {
                background-color: #0062cc;
            }
        """)


class StyledLabel(QLabel):
    """Etykieta z dodatkową stylizacją."""
    
    def __init__(self, text, is_title=False, parent=None):
        """Inicjalizacja etykiety."""
        super().__init__(text, parent)
        
        if is_title:
            font = self.font()
            font.setPointSize(18)
            font.setBold(True)
            self.setFont(font)
            self.setStyleSheet("color: #333; margin: 10px 0;")
        else:
            self.setStyleSheet("color: #333; font-size: 14px;")


class StyledLineEdit(QLineEdit):
    """Pole tekstowe z dodatkową stylizacją."""
    
    def __init__(self, parent=None):
        """Inicjalizacja pola tekstowego."""
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                color: #333;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #80bdff;
                outline: 0;
                box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
            }
        """)


class StyledComboBox(QComboBox):
    """Rozwijana lista z dodatkową stylizacją."""
    
    def __init__(self, parent=None):
        """Inicjalizacja rozwijanej listy."""
        super().__init__(parent)
        self.setStyleSheet("""
            QComboBox {
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                color: #333;
                font-size: 14px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right;
                width: 20px;
                border-left: 1px solid #ddd;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox:on {
                border-bottom-left-radius: 0;
                border-bottom-right-radius: 0;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ddd;
                background-color: white;
                selection-background-color: #e7f3ff;
                selection-color: #333;
            }
        """)


class StyledDoubleSpinBox(QDoubleSpinBox):
    """Pole numeryczne z dodatkową stylizacją."""
    
    def __init__(self, parent=None):
        """Inicjalizacja pola numerycznego."""
        super().__init__(parent)
        self.setStyleSheet("""
            QDoubleSpinBox {
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                color: #333;
                font-size: 14px;
                min-width: 100px;
            }
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                width: 20px;
                border-left: 1px solid #ddd;
            }
            QDoubleSpinBox:focus {
                border-color: #80bdff;
            }
        """)
        self.setDecimals(1)
        self.setSingleStep(0.5)


class StyledDateEdit(QDateEdit):
    """Pole daty z dodatkową stylizacją."""
    
    def __init__(self, parent=None):
        """Inicjalizacja pola daty."""
        super().__init__(parent)
        current_date = QDate.currentDate()
        self.setDate(current_date)
        self.setDisplayFormat("yyyy-MM-dd")
        self.setCalendarPopup(True)
        self.setStyleSheet("""
            QDateEdit {
                background-color: #fff;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                color: #333;
                font-size: 14px;
                min-width: 120px;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right;
                width: 20px;
                border-left: 1px solid #ddd;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QDateEdit:focus {
                border-color: #80bdff;
            }
        """)


class CardFrame(QFrame):
    """Ramka karty z cieniowaniem."""
    
    def __init__(self, parent=None):
        """Inicjalizacja ramki karty."""
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("""
            #card {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)


class DataTable(QTableWidget):
    """Tabela danych ze stylizacją."""
    
    def __init__(self, parent=None):
        """Inicjalizacja tabeli danych."""
        super().__init__(parent)
        
        # Ustawienia podstawowe
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setAlternatingRowColors(True)
        self.setShowGrid(True)
        self.setGridStyle(Qt.PenStyle.SolidLine)
        self.setSortingEnabled(True)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Ustawienia rozmiaru
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.horizontalHeader().setMinimumSectionSize(80)
        self.horizontalHeader().setDefaultSectionSize(100)
        self.horizontalHeader().setStretchLastSection(True)
        
        # Stylizacja
        self.setStyleSheet("""
            QTableWidget {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                gridline-color: #ddd;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #e7f3ff;
                color: #000;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 6px;
                border: none;
                border-right: 1px solid #ddd;
                border-bottom: 1px solid #ddd;
                font-weight: bold;
            }
            QTableWidget::item:alternate {
                background-color: #f5f5f5;
            }
        """) 