"""
Moduł do obsługi danych pogodowych.
"""

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Dict, Optional, Any, Tuple
from functools import reduce
from pathlib import Path
from src.utils.logger import logger
from src.utils.file import safe_file_operation


@dataclass
class WeatherRecord:
    """Klasa reprezentująca pojedynczy rekord danych pogodowych."""
    date: date
    location_id: str
    avg_temp: float
    min_temp: float
    max_temp: float
    precipitation: float
    sunshine_hours: float
    cloud_cover: int


class WeatherData:
    """
    Klasa do obsługi danych pogodowych.
    
    Umożliwia wczytywanie danych z plików CSV/JSON, 
    filtrowanie danych pogodowych według różnych kryteriów,
    obliczanie statystyk i zapisywanie wyników.
    """
    
    def __init__(self):
        """Inicjalizacja obiektu WeatherData."""
        logger.debug("Inicjalizacja obiektu WeatherData")
        self.records: List[WeatherRecord] = []
        self.filtered_records: List[WeatherRecord] = []
    
    def load_from_csv(self, filepath: str) -> None:
        """
        Wczytuje dane pogodowe z pliku CSV.
        
        Args:
            filepath: Ścieżka do pliku CSV.
            
        Raises:
            ValueError: Gdy nie udało się wczytać danych.
        """
        logger.info(f"Wczytywanie danych pogodowych z pliku CSV: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.records = [
                    WeatherRecord(
                        date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                        location_id=row['location_id'],
                        avg_temp=float(row['avg_temp']),
                        min_temp=float(row['min_temp']),
                        max_temp=float(row['max_temp']),
                        precipitation=float(row['precipitation']),
                        sunshine_hours=float(row['sunshine_hours']),
                        cloud_cover=int(row['cloud_cover'])
                    )
                    for row in reader
                ]
                self.filtered_records = self.records.copy()
                logger.info(f"Wczytano {len(self.records)} rekordów pogodowych z pliku CSV")
        except Exception as e:
            logger.error(f"Błąd podczas wczytywania danych z CSV: {str(e)}")
            raise ValueError(f"Błąd podczas wczytywania danych z CSV: {str(e)}")
    
    def load_from_json(self, filepath: str) -> None:
        """
        Wczytuje dane pogodowe z pliku JSON.
        
        Args:
            filepath: Ścieżka do pliku JSON.
            
        Raises:
            ValueError: Gdy nie udało się wczytać danych.
        """
        logger.info(f"Wczytywanie danych pogodowych z pliku JSON: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                weather_records = data.get('weather_records', [])
                
                self.records = [
                    WeatherRecord(
                        date=datetime.strptime(record['date'], '%Y-%m-%d').date(),
                        location_id=record['location_id'],
                        avg_temp=float(record['avg_temp']),
                        min_temp=float(record['min_temp']),
                        max_temp=float(record['max_temp']),
                        precipitation=float(record['precipitation']),
                        sunshine_hours=float(record['sunshine_hours']),
                        cloud_cover=int(record['cloud_cover'])
                    )
                    for record in weather_records
                ]
                self.filtered_records = self.records.copy()
                logger.info(f"Wczytano {len(self.records)} rekordów pogodowych z pliku JSON")
        except Exception as e:
            logger.error(f"Błąd podczas wczytywania danych z JSON: {str(e)}")
            raise ValueError(f"Błąd podczas wczytywania danych z JSON: {str(e)}")
    
    def filter_records(self, location=None, date_range=None, **kwargs) -> List[WeatherRecord]:
        """
        Filtruje rekordy pogodowe według podanych parametrów.
        
        Args:
            location: Identyfikator lokalizacji (opcjonalny).
            date_range: Krotka (start_date, end_date) z zakresem dat (opcjonalna).
            **kwargs: Dodatkowe parametry filtrowania.
            
        Returns:
            Lista przefiltrowanych rekordów pogodowych.
        """
        logger.debug(f"Zastosowano filtry pogodowe: {{'location': {location}, 'date_range': {date_range}}}")
        
        # Resetujemy filtrowane rekordy do wszystkich rekordów
        self.filtered_records = self.records.copy()
        
        # Filtrowanie według lokalizacji
        if location:
            self.filter_by_location(location)
        
        # Filtrowanie według zakresu dat
        if date_range and len(date_range) == 2:
            start_date, end_date = date_range
            self.filter_by_date_range(start_date, end_date)
        
        logger.info(f"Po filtrowaniu pozostało {len(self.filtered_records)} rekordów pogodowych")
        return self.filtered_records
    
    def filter_by_location(self, location_id: str) -> List[WeatherRecord]:
        """
        Filtruje dane pogodowe według lokalizacji.
        
        Args:
            location_id: Identyfikator lokalizacji.
            
        Returns:
            Lista przefiltrowanych rekordów pogodowych.
        """
        logger.debug(f"Filtrowanie rekordów pogodowych według lokalizacji: {location_id}")
        filtered = list(filter(
            lambda record: record.location_id == location_id,
            self.records
        ))
        self.filtered_records = filtered
        logger.info(f"Znaleziono {len(filtered)} rekordów dla lokalizacji {location_id}")
        return filtered
    
    def filter_by_date_range(self, start_date: date, end_date: date) -> List[WeatherRecord]:
        """
        Filtruje dane pogodowe według zakresu dat.
        
        Args:
            start_date: Data początkowa.
            end_date: Data końcowa.
            
        Returns:
            Lista przefiltrowanych rekordów pogodowych.
        """
        logger.debug(f"Filtrowanie rekordów pogodowych według zakresu dat: {start_date} do {end_date}")
        filtered = list(filter(
            lambda record: start_date <= record.date <= end_date,
            self.filtered_records
        ))
        self.filtered_records = filtered
        logger.info(f"Znaleziono {len(filtered)} rekordów w zakresie dat od {start_date} do {end_date}")
        return filtered
    
    def get_locations(self) -> List[str]:
        """
        Zwraca listę unikalnych lokalizacji występujących w danych.
        
        Returns:
            Lista unikalnych lokalizacji.
        """
        logger.debug("Pobieranie listy unikalnych lokalizacji")
        locations = {record.location_id for record in self.records}
        logger.debug(f"Znaleziono {len(locations)} unikalnych lokalizacji")
        return sorted(locations)
    
    def get_date_range(self) -> Tuple[date, date]:
        """
        Zwraca zakres dat (min, max) dostępnych w danych.
        
        Returns:
            Krotka (min_date, max_date).
        """
        logger.debug("Obliczanie zakresu dat")
        if not self.records:
            logger.warn("Brak danych pogodowych do obliczenia zakresu dat")
            return (date.today(), date.today())
        
        min_date = reduce(
            lambda d1, d2: d1 if d1 < d2 else d2,
            (record.date for record in self.records)
        )
        
        max_date = reduce(
            lambda d1, d2: d1 if d1 > d2 else d2,
            (record.date for record in self.records)
        )
        
        logger.debug(f"Zakres dat: od {min_date} do {max_date}")
        return (min_date, max_date)
    
    def calculate_avg_temperature(self) -> float:
        """
        Oblicza średnią temperaturę dla przefiltrowanych danych.
        
        Returns:
            Średnia temperatura.
        """
        logger.debug("Obliczanie średniej temperatury")
        if not self.filtered_records:
            logger.warn("Brak danych pogodowych do obliczenia średniej temperatury")
            return 0.0
        
        total = sum(record.avg_temp for record in self.filtered_records)
        avg_temp = total / len(self.filtered_records)
        logger.debug(f"Średnia temperatura: {avg_temp:.2f}°C")
        return avg_temp
    
    def calculate_total_precipitation(self) -> float:
        """
        Oblicza sumę opadów dla przefiltrowanych danych.
        
        Returns:
            Suma opadów.
        """
        logger.debug("Obliczanie sumy opadów")
        if not self.filtered_records:
            logger.warn("Brak danych pogodowych do obliczenia sumy opadów")
            return 0.0
        
        total_precip = sum(record.precipitation for record in self.filtered_records)
        logger.debug(f"Suma opadów: {total_precip:.2f} mm")
        return total_precip
    
    def count_sunny_days(self, min_sunshine_hours: float = 5.0) -> int:
        """
        Oblicza liczbę dni słonecznych dla przefiltrowanych danych.
        
        Args:
            min_sunshine_hours: Minimalna liczba godzin słonecznych uznawana za dzień słoneczny.
            
        Returns:
            Liczba dni słonecznych.
        """
        logger.debug(f"Obliczanie liczby dni słonecznych (min. {min_sunshine_hours} godzin)")
        if not self.filtered_records:
            logger.warn("Brak danych pogodowych do obliczenia liczby dni słonecznych")
            return 0
        
        sunny_days = len(list(filter(
            lambda record: record.sunshine_hours >= min_sunshine_hours,
            self.filtered_records
        )))
        logger.debug(f"Liczba dni słonecznych: {sunny_days}")
        return sunny_days
    
    def calculate_statistics(self, location_id: Optional[str] = None, 
                           start_date: Optional[date] = None, 
                           end_date: Optional[date] = None) -> Dict[str, float]:
        """
        Oblicza statystyki dla danych pogodowych, opcjonalnie ograniczonych do lokalizacji i zakresu dat.
        
        Args:
            location_id: Opcjonalny identyfikator lokalizacji.
            start_date: Opcjonalna data początkowa.
            end_date: Opcjonalna data końcowa.
            
        Returns:
            Słownik ze statystykami: średnia temperatura, suma opadów, liczba dni słonecznych.
        """
        logger.info(f"Obliczanie statystyk pogodowych dla lokalizacji: {location_id}, zakres dat: {start_date} - {end_date}")
        # Resetowanie filtrów
        self.filtered_records = self.records.copy()
        
        # Filtrowanie według lokalizacji
        if location_id:
            self.filter_by_location(location_id)
        
        # Filtrowanie według zakresu dat
        if start_date and end_date:
            self.filter_by_date_range(start_date, end_date)
        
        # Obliczanie statystyk
        stats = {
            'avg_temperature': self.calculate_avg_temperature(),
            'total_precipitation': self.calculate_total_precipitation(),
            'sunny_days_count': self.count_sunny_days()
        }
        
        logger.info(f"Obliczone statystyki: {stats}")
        return stats
    
    def save_to_csv(self, filepath: str) -> None:
        """
        Zapisuje przefiltrowane dane do pliku CSV.
        
        Args:
            filepath: Ścieżka do pliku CSV.
            
        Raises:
            ValueError: Gdy nie udało się zapisać danych.
        """
        logger.info(f"Zapisywanie {len(self.filtered_records)} rekordów pogodowych do pliku CSV: {filepath}")
        
        def write_csv(filepath):
            fieldnames = [
                'date', 'location_id', 'avg_temp', 'min_temp', 'max_temp',
                'precipitation', 'sunshine_hours', 'cloud_cover'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                
                for record in self.filtered_records:
                    writer.writerow({
                        'date': record.date.strftime('%Y-%m-%d'),
                        'location_id': record.location_id,
                        'avg_temp': record.avg_temp,
                        'min_temp': record.min_temp,
                        'max_temp': record.max_temp,
                        'precipitation': record.precipitation,
                        'sunshine_hours': record.sunshine_hours,
                        'cloud_cover': record.cloud_cover
                    })
        
        safe_file_operation(write_csv, filepath, "CSV")
    
    def save_to_json(self, filepath: str) -> None:
        """
        Zapisuje przefiltrowane dane do pliku JSON.
        
        Args:
            filepath: Ścieżka do pliku JSON.
            
        Raises:
            ValueError: Gdy nie udało się zapisać danych.
        """
        logger.info(f"Zapisywanie {len(self.filtered_records)} rekordów pogodowych do pliku JSON: {filepath}")
        
        def write_json(filepath):
            data = {
                'weather_records': [
                    {
                        'date': record.date.strftime('%Y-%m-%d'),
                        'location_id': record.location_id,
                        'avg_temp': record.avg_temp,
                        'min_temp': record.min_temp,
                        'max_temp': record.max_temp,
                        'precipitation': record.precipitation,
                        'sunshine_hours': record.sunshine_hours,
                        'cloud_cover': record.cloud_cover
                    }
                    for record in self.filtered_records
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        
        safe_file_operation(write_json, filepath, "JSON")



