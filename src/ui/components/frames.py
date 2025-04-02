"""
Komponenty ramek UI.
"""

from PyQt6.QtWidgets import QFrame


class CardFrame(QFrame):
    """Ramka w stylu karty z zaokrąglonymi rogami."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
            QFrame {
                background-color: #2b2b2b;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        self.setFrameShape(QFrame.Shape.StyledPanel) 