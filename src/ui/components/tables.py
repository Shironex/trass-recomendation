"""
Komponenty tabel UI.
"""

from PyQt6.QtWidgets import QTableWidget, QHeaderView


class DataTable(QTableWidget):
    """Niestandardowa tabela danych z formatowaniem."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QTableWidget {
                background-color: #222222;
                color: #e0e0e0;
                gridline-color: #444444;
                border: none;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #333333;
            }
            QTableWidget::item:selected {
                background-color: #3a7ca5;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #ffffff;
                padding: 5px;
                border: none;
                font-weight: bold;
            }
        """)
        
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.verticalHeader().setVisible(False) 