"""
Komponent formularza danych dla aplikacji Rekomendator Tras Turystycznych.
"""

from PyQt6.QtWidgets import (
    QGroupBox, QFormLayout, QHBoxLayout, QLabel, 
    QComboBox, QDateEdit, QPushButton, QDoubleSpinBox
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from .buttons import BaseButton, PrimaryButton


class DataForm(QGroupBox):
    """
    Komponent formularza danych do wielokrotnego użytku.
    Umożliwia tworzenie formularzy do pobierania danych.
    """
    
    # Sygnał emitowany po kliknięciu przycisku
    submitClicked = pyqtSignal(dict)
    
    def __init__(self, title="Pobieranie danych", parent=None):
        """
        Inicjalizacja formularza danych.
        
        Args:
            title: Tytuł formularza.
            parent: Rodzic widgetu.
        """
        super().__init__(title, parent)
        self._form_widgets = {}
        self._setup_layout()
    
    def _setup_layout(self):
        """Konfiguracja podstawowego układu."""
        self.form_layout = QFormLayout(self)
    
    def add_combo_field(self, name, label, items=None, editable=False):
        """
        Dodaje pole combo do formularza.
        
        Args:
            name: Nazwa pola (identyfikator).
            label: Etykieta wyświetlana w formularzu.
            items: Lista elementów (opcjonalna).
            editable: Czy pole ma być edytowalne.
            
        Returns:
            Utworzony widget combobox.
        """
        combo = QComboBox()
        combo.setEditable(editable)
        
        if items:
            combo.addItems(items)
        
        self.form_layout.addRow(f"{label}:", combo)
        
        # Zapisanie referencji do widgetu
        self._form_widgets[name] = combo
        
        return combo
    
    def add_date_range(self, name, label, default_start_days=-7, default_end_days=0):
        """
        Dodaje zakres dat do formularza.
        
        Args:
            name: Nazwa pola (identyfikator).
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
        self._form_widgets[f"{name}_start"] = start_date
        self._form_widgets[f"{name}_end"] = end_date
        
        return start_date, end_date
    
    def add_number_range(self, name, label, min_value=0, max_value=100, decimals=1, 
                       default_min=0, default_max=100, step=0.5):
        """
        Dodaje zakres wartości liczbowych do formularza.
        
        Args:
            name: Nazwa pola (identyfikator).
            label: Etykieta wyświetlana w formularzu.
            min_value: Minimalna wartość zakresu
            max_value: Maksymalna wartość zakresu
            decimals: Liczba miejsc po przecinku
            default_min: Domyślna wartość minimalna
            default_max: Domyślna wartość maksymalna
            step: Krok zmiany wartości
            
        Returns:
            Tuple zawierające dwa obiekty QDoubleSpinBox (min, max)
        """
        number_layout = QHBoxLayout()
        
        # Minimalna wartość
        number_layout.addWidget(QLabel("Min:"))
        min_spin = QDoubleSpinBox()
        min_spin.setRange(min_value, max_value)
        min_spin.setValue(default_min)
        min_spin.setDecimals(decimals)
        min_spin.setSingleStep(step)
        number_layout.addWidget(min_spin)
        
        number_layout.addWidget(QLabel("Max:"))
        max_spin = QDoubleSpinBox()
        max_spin.setRange(min_value, max_value)
        max_spin.setValue(default_max)
        max_spin.setDecimals(decimals)
        max_spin.setSingleStep(step)
        number_layout.addWidget(max_spin)
        
        # Dodanie do układu
        self.form_layout.addRow(f"{label}:", number_layout)
        
        # Zapisanie referencji do widgetów
        self._form_widgets[f"{name}_min"] = min_spin
        self._form_widgets[f"{name}_max"] = max_spin
        
        return min_spin, max_spin
    
    def add_submit_button(self, text="Pobierz dane"):
        """
        Dodaje przycisk zatwierdzający do formularza.
        
        Args:
            text: Tekst przycisku.
            
        Returns:
            Utworzony przycisk.
        """
        button_layout = QHBoxLayout()
        
        submit_button = BaseButton(text)
        submit_button.clicked.connect(self._on_submit)
        button_layout.addWidget(submit_button)
        
        self.form_layout.addRow("", button_layout)
        
        # Zapisanie referencji do widgetu
        self._form_widgets["submit_button"] = submit_button
        
        return submit_button
    
    def add_buttons_row(self, buttons_dict):
        """
        Dodaje wiersz przycisków do formularza.
        
        Args:
            buttons_dict: Słownik z nazwami i tekstami przycisków.
            
        Returns:
            Słownik z utworzonymi przyciskami.
        """
        button_layout = QHBoxLayout()
        buttons = {}
        
        for name, text in buttons_dict.items():
            button = BaseButton(text)
            button_layout.addWidget(button)
            buttons[name] = button
            self._form_widgets[name] = button
        
        self.form_layout.addRow("", button_layout)
        
        return buttons
    
    def _on_submit(self):
        """
        Obsługuje zdarzenie kliknięcia przycisku zatwierdzającego.
        Zbiera dane z formularza i emituje sygnał submitClicked.
        """
        data = {}
        
        # Zbieranie danych z widgetów formularza (z wyjątkiem przycisków)
        for name, widget in self._form_widgets.items():
            if isinstance(widget, QComboBox):
                data[name] = widget.currentText()
            elif isinstance(widget, QDateEdit):
                data[name] = widget.date().toPyDate()
            elif isinstance(widget, QDoubleSpinBox):
                data[name] = widget.value()
        
        # Emitowanie sygnału z danymi
        self.submitClicked.emit(data)
    
    def get_field_value(self, name):
        """
        Zwraca wartość pola formularza.
        
        Args:
            name: Nazwa pola.
            
        Returns:
            Wartość pola lub None jeśli pole nie istnieje.
        """
        widget = self._form_widgets.get(name)
        
        if widget is None:
            return None
        
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QDateEdit):
            return widget.date().toPyDate()
        elif isinstance(widget, QDoubleSpinBox):
            return widget.value()
        
        return None
    
    def get_date_range(self, name):
        """
        Zwraca zakres dat z formularza.
        
        Args:
            name: Nazwa pola bez przyrostków _start/_end.
            
        Returns:
            Tuple (start_date, end_date) lub (None, None) jeśli pole nie istnieje.
        """
        start_date = self._form_widgets.get(f"{name}_start")
        end_date = self._form_widgets.get(f"{name}_end")
        
        if start_date and end_date:
            if isinstance(start_date, QDateEdit) and isinstance(end_date, QDateEdit):
                return start_date.date().toPyDate(), end_date.date().toPyDate()
            elif isinstance(start_date, QDoubleSpinBox) and isinstance(end_date, QDoubleSpinBox):
                return start_date.value(), end_date.value()
        
        return None, None
    
    def set_field_value(self, name, value):
        """
        Ustawia wartość pola formularza.
        
        Args:
            name: Nazwa pola.
            value: Nowa wartość.
        """
        widget = self._form_widgets.get(name)
        
        if widget is None:
            return
        
        if isinstance(widget, QComboBox):
            index = widget.findText(value)
            if index >= 0:
                widget.setCurrentIndex(index)
            elif widget.isEditable():
                widget.setEditText(value)
        elif isinstance(widget, QDateEdit):
            if isinstance(value, QDate):
                widget.setDate(value)
        elif isinstance(widget, QDoubleSpinBox):
            widget.setValue(value)
    
    def set_date_range(self, name, start_date, end_date):
        """
        Ustawia zakres dat w formularzu.
        
        Args:
            name: Nazwa pola bez przyrostków _start/_end.
            start_date: Nowa data początkowa.
            end_date: Nowa data końcowa.
        """
        start_widget = self._form_widgets.get(f"{name}_start")
        end_widget = self._form_widgets.get(f"{name}_end")
        
        if start_widget and isinstance(start_date, QDate) and isinstance(start_widget, QDateEdit):
            start_widget.setDate(start_date)
            
        if end_widget and isinstance(end_date, QDate) and isinstance(end_widget, QDateEdit):
            end_widget.setDate(end_date)
            
        if start_widget and isinstance(start_widget, QDoubleSpinBox):
            start_widget.setValue(start_date)
            
        if end_widget and isinstance(end_widget, QDoubleSpinBox):
            end_widget.setValue(end_date) 