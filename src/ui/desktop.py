"""
Desktop User Interface module for the Tourist Route Recommender application.
This module implements a graphical user interface using PyQt6.
"""

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QGroupBox,
    QDoubleSpinBox, QComboBox, QLineEdit, QMessageBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
import sys
from src.trail_data import TrailData
from src.weather_data import WeatherData

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tourist Route Recommender")
        self.setMinimumSize(800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create and add pages
        self.main_page = MainPage(self)
        self.trail_filter_page = TrailFilterPage(self)
        self.weather_data_page = WeatherDataPage(self)
        
        self.stacked_widget.addWidget(self.main_page)
        self.stacked_widget.addWidget(self.trail_filter_page)
        self.stacked_widget.addWidget(self.weather_data_page)
        
        # Set initial page
        self.stacked_widget.setCurrentWidget(self.main_page)

class MainPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Tourist Route Recommender")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # Buttons
        filter_btn = QPushButton("Filter Trails")
        filter_btn.clicked.connect(self.show_trail_filter)
        layout.addWidget(filter_btn)
        
        weather_btn = QPushButton("Weather Data & Preferences")
        weather_btn.clicked.connect(self.show_weather_data)
        layout.addWidget(weather_btn)
        
        recommend_btn = QPushButton("Get Recommendations")
        recommend_btn.clicked.connect(self.show_recommendations)
        layout.addWidget(recommend_btn)
        
        # Add stretch to push buttons to the top
        layout.addStretch()
    
    def show_trail_filter(self):
        if self.main_window:
            self.main_window.stacked_widget.setCurrentWidget(self.main_window.trail_filter_page)
    
    def show_weather_data(self):
        if self.main_window:
            self.main_window.stacked_widget.setCurrentWidget(self.main_window.weather_data_page)
    
    def show_recommendations(self):
        QMessageBox.information(self, "Recommendations", "Getting recommendations... (To be implemented)")

class TrailFilterPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.trail_data = TrailData()
        self.filtered_trails = []  # Store filtered trails
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Trail Filtering")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Load data button
        load_btn = QPushButton("Load Trail Data")
        load_btn.clicked.connect(self.load_trail_data)
        layout.addWidget(load_btn)
        
        # Length filter
        length_group = QWidget()
        length_layout = QVBoxLayout(length_group)
        length_layout.addWidget(QLabel("Trail Length (km):"))
        length_inputs = QWidget()
        length_inputs_layout = QHBoxLayout(length_inputs)
        self.min_length = QDoubleSpinBox()
        self.min_length.setRange(0, 100)
        self.max_length = QDoubleSpinBox()
        self.max_length.setRange(0, 100)
        length_inputs_layout.addWidget(QLabel("Min:"))
        length_inputs_layout.addWidget(self.min_length)
        length_inputs_layout.addWidget(QLabel("Max:"))
        length_inputs_layout.addWidget(self.max_length)
        length_layout.addWidget(length_inputs)
        layout.addWidget(length_group)
        
        # Difficulty filter
        difficulty_group = QWidget()
        difficulty_layout = QVBoxLayout(difficulty_group)
        difficulty_layout.addWidget(QLabel("Difficulty Level:"))
        self.difficulty = QComboBox()
        self.difficulty.addItems(["Any"] + [str(i) for i in range(1, 6)])
        difficulty_layout.addWidget(self.difficulty)
        layout.addWidget(difficulty_group)
        
        # Region filter
        region_group = QWidget()
        region_layout = QVBoxLayout(region_group)
        region_layout.addWidget(QLabel("Region:"))
        self.region = QComboBox()
        self.region.addItem("Any")
        region_layout.addWidget(self.region)
        layout.addWidget(region_group)
        
        # Filter button
        filter_btn = QPushButton("Apply Filters")
        filter_btn.clicked.connect(self.apply_filters)
        layout.addWidget(filter_btn)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Name", "Region", "Length (km)", "Difficulty", "Terrain"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.results_table)
        
        # Export buttons
        export_group = QWidget()
        export_layout = QHBoxLayout(export_group)
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.clicked.connect(self.export_to_csv)
        export_json_btn = QPushButton("Export to JSON")
        export_json_btn.clicked.connect(self.export_to_json)
        export_layout.addWidget(export_csv_btn)
        export_layout.addWidget(export_json_btn)
        layout.addWidget(export_group)
        
        # Back button
        back_btn = QPushButton("Back to Main Menu")
        back_btn.clicked.connect(self.back_to_main)
        layout.addWidget(back_btn)
    
    def load_trail_data(self):
        """Load trail data from a file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Load Trail Data",
            "",
            "CSV Files (*.csv);;JSON Files (*.json)"
        )
        if filepath:
            try:
                if filepath.endswith('.csv'):
                    self.trail_data.load_from_csv(filepath)
                else:
                    self.trail_data.load_from_json(filepath)
                
                # Update region combo box
                self.region.clear()
                self.region.addItem("Any")
                self.region.addItems(self.trail_data.get_regions())
                
                # Update difficulty combo box
                self.difficulty.clear()
                self.difficulty.addItem("Any")
                self.difficulty.addItems([str(i) for i in self.trail_data.get_difficulty_levels()])
                
                # Update length range
                min_len, max_len = self.trail_data.get_length_range()
                self.min_length.setRange(0, max_len)
                self.max_length.setRange(0, max_len)
                self.max_length.setValue(max_len)
                
                QMessageBox.information(self, "Success", "Trail data loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load trail data: {str(e)}")
    
    def apply_filters(self):
        """Apply filters and display results."""
        if not self.trail_data.trails:
            QMessageBox.warning(self, "Warning", "No trail data loaded!")
            return
        
        # Get filter values
        min_len = self.min_length.value()
        max_len = self.max_length.value()
        difficulty = int(self.difficulty.currentText()) if self.difficulty.currentText() != "Any" else None
        region = self.region.currentText() if self.region.currentText() != "Any" else None
        
        # Apply filters
        self.filtered_trails = self.trail_data.trails
        
        if min_len > 0 or max_len < 100:
            self.filtered_trails = self.trail_data.filter_by_length(min_len, max_len)
        
        if difficulty is not None:
            self.filtered_trails = self.trail_data.filter_by_difficulty(difficulty)
        
        if region is not None:
            self.filtered_trails = self.trail_data.filter_by_region(region)
        
        # Update results table
        self.results_table.setRowCount(len(self.filtered_trails))
        for i, trail in enumerate(self.filtered_trails):
            self.results_table.setItem(i, 0, QTableWidgetItem(trail.name))
            self.results_table.setItem(i, 1, QTableWidgetItem(trail.region))
            self.results_table.setItem(i, 2, QTableWidgetItem(f"{trail.length_km:.1f}"))
            self.results_table.setItem(i, 3, QTableWidgetItem(str(trail.difficulty)))
            self.results_table.setItem(i, 4, QTableWidgetItem(trail.terrain_type))
    
    def export_to_csv(self):
        """Export filtered trails to CSV file."""
        if not self.filtered_trails:
            QMessageBox.warning(self, "Warning", "No filtered trails to export!")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            "",
            "CSV Files (*.csv)"
        )
        if filepath:
            try:
                # Create temporary TrailData instance with filtered trails
                temp_data = TrailData()
                temp_data.trails = self.filtered_trails
                temp_data.save_to_csv(filepath)
                QMessageBox.information(self, "Success", "Trails exported to CSV successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export trails: {str(e)}")
    
    def export_to_json(self):
        """Export filtered trails to JSON file."""
        if not self.filtered_trails:
            QMessageBox.warning(self, "Warning", "No filtered trails to export!")
            return
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export to JSON",
            "",
            "JSON Files (*.json)"
        )
        if filepath:
            try:
                # Create temporary TrailData instance with filtered trails
                temp_data = TrailData()
                temp_data.trails = self.filtered_trails
                temp_data.save_to_json(filepath)
                QMessageBox.information(self, "Success", "Trails exported to JSON successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export trails: {str(e)}")
    
    def back_to_main(self):
        if self.main_window:
            self.main_window.stacked_widget.setCurrentWidget(self.main_window.main_page)

class WeatherDataPage(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.weather_data = WeatherData()
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Weather Data & Preferences")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Load data button
        load_btn = QPushButton("Load Weather Data")
        load_btn.clicked.connect(self.load_weather_data)
        layout.addWidget(load_btn)
        
        # Create two columns layout
        columns_layout = QHBoxLayout()
        
        # Left column - Weather Data
        left_column = QVBoxLayout()
        
        # Data filters group
        data_group = QGroupBox("Weather Data Filters")
        data_layout = QVBoxLayout()
        
        # Location filter
        location_layout = QVBoxLayout()
        location_layout.addWidget(QLabel("Location:"))
        self.location = QComboBox()
        location_layout.addWidget(self.location)
        data_layout.addLayout(location_layout)
        
        # Date range filter
        date_layout = QVBoxLayout()
        date_layout.addWidget(QLabel("Date Range:"))
        date_inputs = QWidget()
        date_inputs_layout = QHBoxLayout(date_inputs)
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        date_inputs_layout.addWidget(QLabel("Start:"))
        date_inputs_layout.addWidget(self.start_date)
        date_inputs_layout.addWidget(QLabel("End:"))
        date_inputs_layout.addWidget(self.end_date)
        date_layout.addWidget(date_inputs)
        data_layout.addLayout(date_layout)
        
        data_group.setLayout(data_layout)
        left_column.addWidget(data_group)
        
        # Statistics table
        self.stats_table = QTableWidget()
        self.stats_table.setColumnCount(4)
        self.stats_table.setHorizontalHeaderLabels([
            "Average Temperature (°C)", "Total Precipitation (mm)",
            "Sunny Days", "Total Days"
        ])
        left_column.addWidget(self.stats_table)
        
        # Right column - Weather Preferences
        right_column = QVBoxLayout()
        
        # Preferences group
        pref_group = QGroupBox("Weather Preferences")
        pref_layout = QVBoxLayout()
        
        # Temperature range
        temp_layout = QVBoxLayout()
        temp_layout.addWidget(QLabel("Temperature Range (°C):"))
        temp_inputs = QWidget()
        temp_inputs_layout = QHBoxLayout(temp_inputs)
        self.min_temp = QDoubleSpinBox()
        self.min_temp.setRange(-50, 50)
        self.max_temp = QDoubleSpinBox()
        self.max_temp.setRange(-50, 50)
        temp_inputs_layout.addWidget(QLabel("Min:"))
        temp_inputs_layout.addWidget(self.min_temp)
        temp_inputs_layout.addWidget(QLabel("Max:"))
        temp_inputs_layout.addWidget(self.max_temp)
        temp_layout.addWidget(temp_inputs)
        pref_layout.addLayout(temp_layout)
        
        # Precipitation preference
        precip_layout = QVBoxLayout()
        precip_layout.addWidget(QLabel("Precipitation:"))
        self.precip_combo = QComboBox()
        self.precip_combo.addItems(["No rain", "Light rain acceptable", "Any conditions"])
        precip_layout.addWidget(self.precip_combo)
        pref_layout.addLayout(precip_layout)
        
        # Sunshine preference
        sun_layout = QVBoxLayout()
        sun_layout.addWidget(QLabel("Sunshine:"))
        self.sun_combo = QComboBox()
        self.sun_combo.addItems(["Full sun", "Partial sun", "Any conditions"])
        sun_layout.addWidget(self.sun_combo)
        pref_layout.addLayout(sun_layout)
        
        pref_group.setLayout(pref_layout)
        right_column.addWidget(pref_group)
        
        # Add columns to main layout
        columns_layout.addLayout(left_column)
        columns_layout.addLayout(right_column)
        layout.addLayout(columns_layout)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        
        # Show statistics button
        stats_btn = QPushButton("Show Statistics")
        stats_btn.clicked.connect(self.show_statistics)
        buttons_layout.addWidget(stats_btn)
        
        # Export buttons
        export_csv_btn = QPushButton("Export to CSV")
        export_csv_btn.clicked.connect(self.export_to_csv)
        export_json_btn = QPushButton("Export to JSON")
        export_json_btn.clicked.connect(self.export_to_json)
        buttons_layout.addWidget(export_csv_btn)
        buttons_layout.addWidget(export_json_btn)
        
        layout.addLayout(buttons_layout)
        
        # Back button
        back_btn = QPushButton("Back to Main Menu")
        back_btn.clicked.connect(self.back_to_main)
        layout.addWidget(back_btn)
    
    def load_weather_data(self):
        """Load weather data from a file."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Load Weather Data",
            "",
            "CSV Files (*.csv);;JSON Files (*.json)"
        )
        if filepath:
            try:
                if filepath.endswith('.csv'):
                    self.weather_data.load_from_csv(filepath)
                else:
                    self.weather_data.load_from_json(filepath)
                
                # Update location combo box
                self.location.clear()
                self.location.addItems(self.weather_data.get_locations())
                
                # Set date range
                start_date, end_date = self.weather_data.get_date_range()
                self.start_date.setDate(start_date)
                self.end_date.setDate(end_date)
                
                QMessageBox.information(self, "Success", "Weather data loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load weather data: {str(e)}")
    
    def show_statistics(self):
        """Display weather statistics for selected location and date range."""
        if not self.weather_data.records:
            QMessageBox.warning(self, "Warning", "No weather data loaded!")
            return
        
        location = self.location.currentText()
        start_date = self.start_date.date().toPyDate()
        end_date = self.end_date.date().toPyDate()
        
        stats = self.weather_data.calculate_statistics(location, start_date, end_date)
        
        # Update statistics table
        self.stats_table.setRowCount(1)
        self.stats_table.setItem(0, 0, QTableWidgetItem(f"{stats['avg_temp']:.1f}"))
        self.stats_table.setItem(0, 1, QTableWidgetItem(f"{stats['total_precipitation']:.1f}"))
        self.stats_table.setItem(0, 2, QTableWidgetItem(str(stats['sunny_days'])))
        self.stats_table.setItem(0, 3, QTableWidgetItem(str(stats['total_days'])))
    
    def export_to_csv(self):
        """Export weather data to CSV file."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export to CSV",
            "",
            "CSV Files (*.csv)"
        )
        if filepath:
            try:
                self.weather_data.save_to_csv(filepath)
                QMessageBox.information(self, "Success", "Weather data exported to CSV successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export weather data: {str(e)}")
    
    def export_to_json(self):
        """Export weather data to JSON file."""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export to JSON",
            "",
            "JSON Files (*.json)"
        )
        if filepath:
            try:
                self.weather_data.save_to_json(filepath)
                QMessageBox.information(self, "Success", "Weather data exported to JSON successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export weather data: {str(e)}")
    
    def back_to_main(self):
        if self.main_window:
            self.main_window.stacked_widget.setCurrentWidget(self.main_window.main_page)

def run_desktop_app():
    """Run the desktop application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 