"""
Module for handling trail data in the Tourist Route Recommender application.
This module provides functionality for loading, filtering, and saving trail data.
"""

import csv
import json
from dataclasses import dataclass
from typing import List, Dict, Optional, Union
from functools import reduce

@dataclass
class Trail:
    """Data class representing a single trail."""
    id: int
    name: str
    region: str
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    length_km: float
    elevation_gain: float
    difficulty: int
    terrain_type: str
    tags: List[str]

class TrailData:
    """Class for managing trail data including loading, filtering, and saving."""
    
    def __init__(self):
        self.trails: List[Trail] = []
    
    def load_from_csv(self, filepath: str) -> None:
        """Load trail data from a CSV file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # Using list comprehension for data transformation
            self.trails = [
                Trail(
                    id=int(row['id']),
                    name=row['name'],
                    region=row['region'],
                    start_lat=float(row['start_lat']),
                    start_lon=float(row['start_lon']),
                    end_lat=float(row['end_lat']),
                    end_lon=float(row['end_lon']),
                    length_km=float(row['length_km']),
                    elevation_gain=float(row['elevation_gain']),
                    difficulty=int(row['difficulty']),
                    terrain_type=row['terrain_type'],
                    tags=row['tags'].split(',')
                )
                for row in reader
            ]
    
    def load_from_json(self, filepath: str) -> None:
        """Load trail data from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Using map for data transformation
            self.trails = list(map(
                lambda x: Trail(
                    id=x['id'],
                    name=x['name'],
                    region=x['region'],
                    start_lat=float(x['start_lat']),
                    start_lon=float(x['start_lon']),
                    end_lat=float(x['end_lat']),
                    end_lon=float(x['end_lon']),
                    length_km=float(x['length_km']),
                    elevation_gain=float(x['elevation_gain']),
                    difficulty=int(x['difficulty']),
                    terrain_type=x['terrain_type'],
                    tags=x['tags']
                ),
                data
            ))
    
    def filter_by_length(self, min_length: Optional[float] = None, max_length: Optional[float] = None) -> List[Trail]:
        """Filter trails by length range."""
        # Using filter with lambda for filtering
        return list(filter(
            lambda trail: (min_length is None or trail.length_km >= min_length) and
                         (max_length is None or trail.length_km <= max_length),
            self.trails
        ))
    
    def filter_by_difficulty(self, difficulty: int) -> List[Trail]:
        """Filter trails by difficulty level."""
        # Using list comprehension for filtering
        return [trail for trail in self.trails if trail.difficulty == difficulty]
    
    def filter_by_region(self, region: str) -> List[Trail]:
        """Filter trails by region."""
        # Using filter with lambda for filtering
        return list(filter(lambda trail: trail.region.lower() == region.lower(), self.trails))
    
    def get_regions(self) -> List[str]:
        """Get list of unique regions."""
        # Using set comprehension for unique values
        return sorted({trail.region for trail in self.trails})
    
    def get_difficulty_levels(self) -> List[int]:
        """Get list of unique difficulty levels."""
        # Using set comprehension for unique values
        return sorted({trail.difficulty for trail in self.trails})
    
    def get_length_range(self) -> tuple[float, float]:
        """Get the range of trail lengths (min, max)."""
        # Using reduce for finding min and max
        if not self.trails:
            return (0.0, 0.0)
        return (
            reduce(lambda x, y: min(x, y.length_km), self.trails, float('inf')),
            reduce(lambda x, y: max(x, y.length_km), self.trails, float('-inf'))
        )
    
    def save_to_csv(self, filepath: str) -> None:
        """Save trail data to a CSV file."""
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'name', 'region', 'start_lat', 'start_lon',
                'end_lat', 'end_lon', 'length_km', 'elevation_gain',
                'difficulty', 'terrain_type', 'tags'
            ])
            writer.writeheader()
            # Using map for data transformation
            writer.writerows(map(
                lambda trail: {
                    'id': trail.id,
                    'name': trail.name,
                    'region': trail.region,
                    'start_lat': trail.start_lat,
                    'start_lon': trail.start_lon,
                    'end_lat': trail.end_lat,
                    'end_lon': trail.end_lon,
                    'length_km': trail.length_km,
                    'elevation_gain': trail.elevation_gain,
                    'difficulty': trail.difficulty,
                    'terrain_type': trail.terrain_type,
                    'tags': ','.join(trail.tags)
                },
                self.trails
            ))
    
    def save_to_json(self, filepath: str) -> None:
        """Save trail data to a JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            # Using list comprehension for data transformation
            json.dump(
                [
                    {
                        'id': trail.id,
                        'name': trail.name,
                        'region': trail.region,
                        'start_lat': trail.start_lat,
                        'start_lon': trail.start_lon,
                        'end_lat': trail.end_lat,
                        'end_lon': trail.end_lon,
                        'length_km': trail.length_km,
                        'elevation_gain': trail.elevation_gain,
                        'difficulty': trail.difficulty,
                        'terrain_type': trail.terrain_type,
                        'tags': trail.tags
                    }
                    for trail in self.trails
                ],
                f,
                indent=2
            ) 