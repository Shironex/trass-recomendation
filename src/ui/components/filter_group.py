"""
Komponent grupy filtrów dla aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import (
    QGroupBox, QFormLayout, QHBoxLayout, QLabel, 
    QSlider, QComboBox, QDateEdit
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from .buttons import BaseButton


class FilterGroup(QGroupBox):
    """
    Komponent grupy filtrów do wielokrotnego użytku na różnych stronach.
    Umożliwia prostą implementację typowych filtrów z konfigurowalnymi opcjami.
    """
    
    filterApplied = pyqtSignal()
    filterReset = pyqtSignal()
    
    def __init__(self, title="Filtrowanie danych", parent=None):
        """
        Inicjalizacja grupy filtrów.
        
        Args:
            title: Tytuł grupy filtrów.
            parent: Rodzic widgetu.
        """
        super().__init__(title, parent)
        self._filter_widgets = {}
        self._setup_layout()
    
    def _setup_layout(self):
        """Konfiguracja podstawowego układu."""
        self.form_layout = QFormLayout(self)
        
        # Przyciski filtrowania
        self.filter_buttons_layout = QHBoxLayout()
        
        self.apply_button = BaseButton("Zastosuj filtry")
        self.apply_button.clicked.connect(self.filterApplied.emit)
        self.filter_buttons_layout.addWidget(self.apply_button)
        
        self.reset_button = BaseButton("Resetuj filtry")
        self.reset_button.clicked.connect(self._reset_filters)
        self.filter_buttons_layout.addWidget(self.reset_button)
    
    def _reset_filters(self):
        """Resetuje wszystkie filtry do wartości domyślnych."""
        # Funkcja zostanie rozbudowana przy dodawaniu konkretnych filtrów
        self.filterReset.emit()
    
    def add_buttons_row(self):
        """Dodaje przyciski do układu formularza."""
        self.form_layout.addRow("", self.filter_buttons_layout)
    
    def add_slider_filter(self, name, label, min_value, max_value, default_min, default_max, unit=""):
        """
        Dodaje filtr suwakowy z zakresem wartości.
        
        Args:
            name: Nazwa filtra (identyfikator).
            label: Etykieta wyświetlana w formularzu.
            min_value: Minimalna wartość suwaka.
            max_value: Maksymalna wartość suwaka.
            default_min: Domyślna wartość minimalna.
            default_max: Domyślna wartość maksymalna.
            unit: Jednostka wyświetlana obok wartości.
            
        Returns:
            Utworzone widgety suwaka.
        """
        slider_layout = QHBoxLayout()
        
        # Suwak minimalnej wartości
        min_slider = QSlider(Qt.Orientation.Horizontal)
        min_slider.setRange(min_value, max_value)
        min_slider.setValue(default_min)
        slider_layout.addWidget(min_slider)
        
        # Etykieta z wartością minimalną
        min_label = QLabel(f"{default_min}{unit}")
        slider_layout.addWidget(min_label)
        min_slider.valueChanged.connect(lambda v: min_label.setText(f"{v}{unit}"))
        
        slider_layout.addWidget(QLabel("do"))
        
        # Suwak maksymalnej wartości
        max_slider = QSlider(Qt.Orientation.Horizontal)
        max_slider.setRange(min_value, max_value)
        max_slider.setValue(default_max)
        slider_layout.addWidget(max_slider)
        
        # Etykieta z wartością maksymalną
        max_label = QLabel(f"{default_max}{unit}")
        slider_layout.addWidget(max_label)
        max_slider.valueChanged.connect(lambda v: max_label.setText(f"{v}{unit}"))
        
        # Dodanie do układu
        self.form_layout.addRow(f"{label}:", slider_layout)
        
        # Zapisanie referencji do widgetów
        self._filter_widgets[f"{name}_min"] = min_slider
        self._filter_widgets[f"{name}_max"] = max_slider
        self._filter_widgets[f"{name}_min_label"] = min_label
        self._filter_widgets[f"{name}_max_label"] = max_label
        
        return min_slider, max_slider
    
    def add_combo_filter(self, name, label, items=None, default_all=True):
        """
        Dodaje filtr typu combobox.
        
        Args:
            name: Nazwa filtra (identyfikator).
            label: Etykieta wyświetlana w formularzu.
            items: Lista elementów (opcjonalna).
            default_all: Czy dodać domyślny element "Wszystkie".
            
        Returns:
            Utworzony widget combobox.
        """
        combo = QComboBox()
        
        if default_all:
            combo.addItem(f"Wszystkie {label.lower()}")
        
        if items:
            combo.addItems(items)
        
        self.form_layout.addRow(f"{label}:", combo)
        
        # Zapisanie referencji do widgetu
        self._filter_widgets[name] = combo
        
        return combo
    
    def add_date_range_filter(self, name, label, default_start_days=-30, default_end_days=30):
        """
        Dodaje filtr zakresu dat.
        
        Args:
            name: Nazwa filtra (identyfikator).
            label: Etykieta wyświetlana w formularzu.
            default_start_days: Domyślna liczba dni od dziś dla daty początkowej.
            default_end_days: Domyślna liczba dni od dziś dla daty końcowej.
            
        Returns:
            Utworzone widgety dat.
        """
        dates_layout = QHBoxLayout()
        
        # Data początkowa
        start_date = QDateEdit()
        start_date.setDate(QDate.currentDate().addDays(default_start_days))
        start_date.setCalendarPopup(True)
        dates_layout.addWidget(start_date)
        
        dates_layout.addWidget(QLabel("do"))
        
        # Data końcowa
        end_date = QDateEdit()
        end_date.setDate(QDate.currentDate().addDays(default_end_days))
        end_date.setCalendarPopup(True)
        dates_layout.addWidget(end_date)
        
        # Dodanie do układu
        self.form_layout.addRow(f"{label}:", dates_layout)
        
        # Zapisanie referencji do widgetów
        self._filter_widgets[f"{name}_start"] = start_date
        self._filter_widgets[f"{name}_end"] = end_date
        
        return start_date, end_date
    
    def get_filter_value(self, name):
        """
        Zwraca wartość wybranego filtra.
        
        Args:
            name: Nazwa filtra.
            
        Returns:
            Wartość filtra lub None jeśli filtr nie istnieje.
        """
        return self._filter_widgets.get(name)
    
    def get_slider_range(self, name):
        """
        Zwraca zakres wartości dla filtra suwakowego.
        
        Args:
            name: Nazwa filtra bez przyrostków _min/_max.
            
        Returns:
            Tuple (min_value, max_value) lub (None, None) jeśli filtr nie istnieje.
        """
        min_slider = self._filter_widgets.get(f"{name}_min")
        max_slider = self._filter_widgets.get(f"{name}_max")
        
        if min_slider and max_slider:
            return min_slider.value(), max_slider.value()
        
        return None, None
    
    def get_date_range(self, name):
        """
        Zwraca zakres dat dla filtra dat.
        
        Args:
            name: Nazwa filtra bez przyrostków _start/_end.
            
        Returns:
            Tuple (start_date, end_date) lub (None, None) jeśli filtr nie istnieje.
        """
        start_date = self._filter_widgets.get(f"{name}_start")
        end_date = self._filter_widgets.get(f"{name}_end")
        
        if start_date and end_date:
            return start_date.date().toPyDate(), end_date.date().toPyDate()
        
        return None, None
    
    def reset_slider(self, name, min_value, max_value):
        """
        Resetuje filtr suwakowy do podanych wartości.
        
        Args:
            name: Nazwa filtra bez przyrostków _min/_max.
            min_value: Nowa wartość minimalna.
            max_value: Nowa wartość maksymalna.
        """
        min_slider = self._filter_widgets.get(f"{name}_min")
        max_slider = self._filter_widgets.get(f"{name}_max")
        
        if min_slider and max_slider:
            min_slider.setValue(min_value)
            max_slider.setValue(max_value)
            
    def reset_combo(self, name, index=0):
        """
        Resetuje filtr combobox do podanego indeksu.
        
        Args:
            name: Nazwa filtra.
            index: Indeks domyślnej opcji (zwykle 0 dla "Wszystkie").
        """
        combo = self._filter_widgets.get(name)
        if combo and index < combo.count():
            combo.setCurrentIndex(index)
            
    def reset_date_range(self, name, start_days=-30, end_days=30):
        """
        Resetuje filtr dat do domyślnych wartości.
        
        Args:
            name: Nazwa filtra bez przyrostków _start/_end.
            start_days: Liczba dni od dziś dla daty początkowej.
            end_days: Liczba dni od dziś dla daty końcowej.
        """
        start_date = self._filter_widgets.get(f"{name}_start")
        end_date = self._filter_widgets.get(f"{name}_end")
        
        if start_date and end_date:
            start_date.setDate(QDate.currentDate().addDays(start_days))
            end_date.setDate(QDate.currentDate().addDays(end_days)) 