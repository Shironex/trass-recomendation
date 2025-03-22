"""
Module for handling weather data in the Tourist Route Recommender application.
This module provides functionality for loading, processing, and saving weather data.
"""

import csv
import json
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, date
from functools import reduce

@dataclass
class WeatherRecord:
    """Data class representing a single weather record."""
    date: datetime
    location_id: str
    avg_temp: float
    min_temp: float
    max_temp: float
    precipitation: float
    sunshine_hours: float
    cloud_cover: int

class WeatherData:
    """Class for managing weather data including loading, processing, and saving."""
    
    def __init__(self):
        self.records: List[WeatherRecord] = []
        self.filtered_records: List[WeatherRecord] = []
    
    def load_from_csv(self, filepath: str) -> None:
        """Load weather data from a CSV file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Using list comprehension for data transformation
            self.records = [
                WeatherRecord(
                    date=datetime.strptime(row['date'], '%Y-%m-%d'),
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
    
    def load_from_json(self, filepath: str) -> None:
        """Load weather data from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Using map for data transformation
            self.records = list(map(
                lambda x: WeatherRecord(
                    date=datetime.strptime(x['date'], '%Y-%m-%d'),
                    location_id=x['location_id'],
                    avg_temp=float(x['avg_temp']),
                    min_temp=float(x['min_temp']),
                    max_temp=float(x['max_temp']),
                    precipitation=float(x['precipitation']),
                    sunshine_hours=float(x['sunshine_hours']),
                    cloud_cover=int(x['cloud_cover'])
                ),
                data
            ))
            self.filtered_records = self.records.copy()
    
    def get_locations(self) -> List[str]:
        """Get list of unique locations."""
        # Using set comprehension for unique values
        return sorted({record.location_id for record in self.records})
    
    def get_date_range(self) -> tuple[date, date]:
        """Get the range of dates (min, max)."""
        if not self.records:
            return (date.today(), date.today())
        # Using reduce for finding min and max
        return (
            reduce(lambda x, y: min(x, y.date.date()), self.records, datetime.max.date()),
            reduce(lambda x, y: max(x, y.date.date()), self.records, datetime.min.date())
        )
    
    def calculate_statistics(self, location_id: str, start_date: Optional[date] = None, 
                           end_date: Optional[date] = None) -> Dict:
        """Calculate weather statistics for a specific location and date range."""
        # Filter records by location and date range
        self.filtered_records = [
            record for record in self.records
            if record.location_id == location_id
            and (start_date is None or record.date.date() >= start_date)
            and (end_date is None or record.date.date() <= end_date)
        ]
        
        if not self.filtered_records:
            return {
                'avg_temp': 0.0,
                'total_precipitation': 0.0,
                'sunny_days': 0,
                'total_days': 0
            }
        
        # Calculate statistics using reduce and list comprehension
        total_temp = reduce(lambda x, y: x + y.avg_temp, self.filtered_records, 0.0)
        total_precip = reduce(lambda x, y: x + y.precipitation, self.filtered_records, 0.0)
        sunny_days = len([r for r in self.filtered_records if r.cloud_cover < 30])
        
        return {
            'avg_temp': total_temp / len(self.filtered_records),
            'total_precipitation': total_precip,
            'sunny_days': sunny_days,
            'total_days': len(self.filtered_records)
        }
    
    def save_to_csv(self, filepath: str) -> None:
        """Save filtered weather data to a CSV file."""
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'date', 'location_id', 'avg_temp', 'min_temp', 'max_temp',
                'precipitation', 'sunshine_hours', 'cloud_cover'
            ])
            writer.writeheader()
            # Using map for data transformation
            writer.writerows(map(
                lambda record: {
                    'date': record.date.strftime('%Y-%m-%d'),
                    'location_id': record.location_id,
                    'avg_temp': record.avg_temp,
                    'min_temp': record.min_temp,
                    'max_temp': record.max_temp,
                    'precipitation': record.precipitation,
                    'sunshine_hours': record.sunshine_hours,
                    'cloud_cover': record.cloud_cover
                },
                self.filtered_records
            ))
    
    def save_to_json(self, filepath: str) -> None:
        """Save filtered weather data to a JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            # Using list comprehension for data transformation
            json.dump(
                [
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
                ],
                f,
                indent=2
            ) 