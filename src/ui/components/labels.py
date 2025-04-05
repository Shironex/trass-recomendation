"""
Komponenty etykiet UI.
"""

from PyQt6.QtWidgets import QLabel

class StyledLabel(QLabel):
    """Niestandardowa etykieta z formatowaniem."""
    
    def __init__(self, text="", is_title=False, parent=None):
        super().__init__(text, parent)
        
        if is_title:
            font = self.font()
            font.setPointSize(16)
            font.setBold(True)
            self.setFont(font)
            self.setStyleSheet("color: #ffffff; margin: 10px;")
        else:
            self.setStyleSheet("color: #e0e0e0;") 