"""
Moduł do obsługi danych pogodowych.
"""

import csv
import json
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Dict, Optional, Tuple
from functools import reduce
from src.utils import ( logger, safe_file_operation )


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
    
    def is_sunny_day(self, min_sunshine_hours: float = 5.0, max_cloud_cover: int = 30) -> bool:
        """
        Sprawdza, czy dzień jest słoneczny.
        
        Args:
            min_sunshine_hours: Minimalna liczba godzin słonecznych dla słonecznego dnia.
            max_cloud_cover: Maksymalne zachmurzenie (%) dla słonecznego dnia.
            
        Returns:
            True, jeśli dzień jest słoneczny, False w przeciwnym przypadku.
        """
        return self.sunshine_hours >= min_sunshine_hours and self.cloud_cover <= max_cloud_cover
    
    def is_rainy_day(self, min_precipitation: float = 1.0) -> bool:
        """
        Sprawdza, czy dzień jest deszczowy.
        
        Args:
            min_precipitation: Minimalna ilość opadów (mm) dla deszczowego dnia.
            
        Returns:
            True, jeśli dzień jest deszczowy, False w przeciwnym przypadku.
        """
        return self.precipitation >= min_precipitation
    
    def calculate_comfort_index(self, 
                              optimal_temp_range: Tuple[float, float] = (18, 25),
                              max_comfort_precipitation: float = 0.0,
                              optimal_sunshine: float = 8.0,
                              max_comfort_cloud_cover: int = 20) -> float:
        """
        Oblicza indeks komfortu pogodowego w skali 0-100.
        
        Indeks uwzględnia:
        - Temperaturę (optymalna 18-25°C)
        - Opady (idealne 0mm)
        - Godziny słoneczne (optymalne 8h)
        - Zachmurzenie (idealne 0-20%)
        
        Args:
            optimal_temp_range: Krotka (min, max) z optymalnym zakresem temperatur.
            max_comfort_precipitation: Maksymalna ilość opadów dla pełnego komfortu.
            optimal_sunshine: Optymalna liczba godzin słonecznych.
            max_comfort_cloud_cover: Maksymalne zachmurzenie dla pełnego komfortu.
            
        Returns:
            Indeks komfortu w skali 0-100.
        """
        # Wagi dla poszczególnych czynników (suma = 100)
        weights = {
            'temperature': 40,
            'precipitation': 30,
            'sunshine': 20,
            'cloud_cover': 10
        }
        
        # Ocena temperatury (0-100)
        temp_score = 0
        min_optimal, max_optimal = optimal_temp_range
        
        if min_optimal <= self.avg_temp <= max_optimal:
            # Idealna temperatura
            temp_score = 100
        else:
            # Im dalej od optymalnego zakresu, tym niższa ocena
            temp_diff = min(abs(self.avg_temp - min_optimal), abs(self.avg_temp - max_optimal))
            # Spadek o 5 punktów na każdy stopień różnicy
            temp_score = max(0, 100 - (temp_diff * 5))
        
        # Ocena opadów (0-100)
        precip_score = 0
        if self.precipitation <= max_comfort_precipitation:
            # Brak opadów = idealnie
            precip_score = 100
        else:
            # Spadek o 10 punktów na każdy mm opadu powyżej limitu
            precip_score = max(0, 100 - ((self.precipitation - max_comfort_precipitation) * 10))
        
        # Ocena godzin słonecznych (0-100)
        sunshine_score = 0
        if self.sunshine_hours >= optimal_sunshine:
            # Idealna liczba godzin słonecznych lub więcej
            sunshine_score = 100
        else:
            # Liniowy spadek dla mniejszej liczby godzin
            sunshine_score = (self.sunshine_hours / optimal_sunshine) * 100
        
        # Ocena zachmurzenia (0-100)
        cloud_score = 0
        if self.cloud_cover <= max_comfort_cloud_cover:
            # Idealne zachmurzenie
            cloud_score = 100
        else:
            # Liniowy spadek dla większego zachmurzenia
            cloud_score = max(0, 100 - (self.cloud_cover - max_comfort_cloud_cover) * (100 / (100 - max_comfort_cloud_cover)))
        
        # Obliczenie ważonego indeksu komfortu
        comfort_index = (
            (temp_score * weights['temperature'] / 100) +
            (precip_score * weights['precipitation'] / 100) +
            (sunshine_score * weights['sunshine'] / 100) +
            (cloud_score * weights['cloud_cover'] / 100)
        )
        
        return comfort_index


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
    
    def count_sunny_days(self, location_id: Optional[str] = None, 
                        start_date: Optional[date] = None, 
                        end_date: Optional[date] = None,
                        min_sunshine_hours: float = 5.0,
                        max_cloud_cover: int = 30) -> int:
        """
        Liczy słoneczne dni dla danej lokalizacji i zakresu dat.
        
        Args:
            location_id: Identyfikator lokalizacji (opcjonalny).
            start_date: Data początkowa zakresu (opcjonalna).
            end_date: Data końcowa zakresu (opcjonalna).
            min_sunshine_hours: Minimalna liczba godzin słonecznych dla słonecznego dnia.
            max_cloud_cover: Maksymalne zachmurzenie (%) dla słonecznego dnia.
            
        Returns:
            Liczba słonecznych dni.
        """
        # Filtrowanie rekordów według lokalizacji i zakresu dat
        filtered = self.records
        
        if location_id:
            filtered = [r for r in filtered if r.location_id == location_id]
        
        if start_date:
            filtered = [r for r in filtered if r.date >= start_date]
        
        if end_date:
            filtered = [r for r in filtered if r.date <= end_date]
        
        # Zliczanie słonecznych dni
        sunny_days = sum(1 for r in filtered if r.is_sunny_day(min_sunshine_hours, max_cloud_cover))
        
        return sunny_days
    
    def count_rainy_days(self, location_id: Optional[str] = None, 
                        start_date: Optional[date] = None, 
                        end_date: Optional[date] = None,
                        min_precipitation: float = 1.0) -> int:
        """
        Liczy deszczowe dni dla danej lokalizacji i zakresu dat.
        
        Args:
            location_id: Identyfikator lokalizacji (opcjonalny).
            start_date: Data początkowa zakresu (opcjonalna).
            end_date: Data końcowa zakresu (opcjonalna).
            min_precipitation: Minimalna ilość opadów (mm) dla deszczowego dnia.
            
        Returns:
            Liczba deszczowych dni.
        """
        # Filtrowanie rekordów według lokalizacji i zakresu dat
        filtered = self.records
        
        if location_id:
            filtered = [r for r in filtered if r.location_id == location_id]
        
        if start_date:
            filtered = [r for r in filtered if r.date >= start_date]
        
        if end_date:
            filtered = [r for r in filtered if r.date <= end_date]
        
        # Zliczanie deszczowych dni
        rainy_days = sum(1 for r in filtered if r.is_rainy_day(min_precipitation))
        
        return rainy_days
    
    def calculate_avg_comfort_index(self, location_id: Optional[str] = None, 
                                  start_date: Optional[date] = None, 
                                  end_date: Optional[date] = None) -> float:
        """
        Oblicza średni indeks komfortu dla danej lokalizacji i zakresu dat.
        
        Args:
            location_id: Identyfikator lokalizacji (opcjonalny).
            start_date: Data początkowa zakresu (opcjonalna).
            end_date: Data końcowa zakresu (opcjonalna).
            
        Returns:
            Średni indeks komfortu w skali 0-100.
        """
        # Filtrowanie rekordów według lokalizacji i zakresu dat
        filtered = self.records
        
        if location_id:
            filtered = [r for r in filtered if r.location_id == location_id]
        
        if start_date:
            filtered = [r for r in filtered if r.date >= start_date]
        
        if end_date:
            filtered = [r for r in filtered if r.date <= end_date]
        
        if not filtered:
            return 0.0
        
        # Obliczanie średniego indeksu komfortu
        total_comfort = sum(r.calculate_comfort_index() for r in filtered)
        avg_comfort = total_comfort / len(filtered)
        
        return avg_comfort
    
    def find_best_weather_periods(self, location_id: str, 
                                period_length: int = 7,
                                min_comfort_index: float = 70) -> List[Tuple[date, float]]:
        """
        Znajduje najlepsze okresy pogodowe dla danej lokalizacji.
        
        Args:
            location_id: Identyfikator lokalizacji.
            period_length: Długość okresu w dniach.
            min_comfort_index: Minimalny akceptowalny indeks komfortu.
            
        Returns:
            Lista krotek (data_początkowa, średni_indeks_komfortu) dla najlepszych okresów.
        """
        # Filtrowanie rekordów według lokalizacji
        location_records = [r for r in self.records if r.location_id == location_id]
        
        # Sortowanie według daty
        location_records.sort(key=lambda r: r.date)
        
        if len(location_records) < period_length:
            return []
        
        # Znajdowanie najlepszych okresów
        best_periods = []
        
        for i in range(len(location_records) - period_length + 1):
            period_records = location_records[i:i+period_length]
            
            # Sprawdzenie ciągłości dat
            dates = [r.date for r in period_records]
            is_continuous = all((dates[j+1] - dates[j]).days == 1 for j in range(len(dates)-1))
            
            if not is_continuous:
                continue
            
            # Obliczanie średniego indeksu komfortu dla okresu
            avg_comfort = sum(r.calculate_comfort_index() for r in period_records) / period_length
            
            if avg_comfort >= min_comfort_index:
                best_periods.append((period_records[0].date, avg_comfort))
        
        # Sortowanie okresów według indeksu komfortu (malejąco)
        best_periods.sort(key=lambda x: x[1], reverse=True)
        
        return best_periods
    
    def calculate_statistics(self, location_id: Optional[str] = None, 
                           start_date: Optional[date] = None, 
                           end_date: Optional[date] = None) -> Dict[str, float]:
        """
        Oblicza statystyki pogodowe dla danej lokalizacji i zakresu dat.
        
        Args:
            location_id: Identyfikator lokalizacji (opcjonalny).
            start_date: Data początkowa zakresu (opcjonalna).
            end_date: Data końcowa zakresu (opcjonalna).
            
        Returns:
            Słownik ze statystykami pogodowymi.
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
            'sunny_days_count': self.count_sunny_days(location_id, start_date, end_date),
            'rainy_days_count': self.count_rainy_days(location_id, start_date, end_date),
            'avg_comfort_index': self.calculate_avg_comfort_index(location_id, start_date, end_date)
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



