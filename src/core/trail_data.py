"""
Moduł do obsługi danych o trasach turystycznych.
"""

import csv
import json
from dataclasses import dataclass
from typing import List
from src.utils import ( logger, safe_file_operation )


@dataclass
class TrailRecord:
    """Klasa reprezentująca pojedynczy rekord trasy turystycznej."""
    id: str
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
    """
    Klasa do obsługi danych o trasach turystycznych.
    
    Umożliwia wczytywanie danych z plików CSV/JSON, 
    filtrowanie tras według różnych kryteriów i zapisywanie wyników.
    """
    
    def __init__(self):
        """Inicjalizacja obiektu TrailData."""
        logger.debug("Inicjalizacja obiektu TrailData")
        self.trails: List[TrailRecord] = []
        self.filtered_trails: List[TrailRecord] = []
    
    def load_from_csv(self, filepath: str) -> None:
        """
        Wczytuje dane o trasach z pliku CSV.
        
        Args:
            filepath: Ścieżka do pliku CSV.
            
        Raises:
            ValueError: Gdy nie udało się wczytać danych.
        """
        logger.info(f"Wczytywanie danych z pliku CSV: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.trails = [
                    TrailRecord(
                        id=row['id'],
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
                        tags=row['tags'].split(',') if row['tags'] else []
                    )
                    for row in reader
                ]
                self.filtered_trails = self.trails.copy()
                logger.info(f"Wczytano {len(self.trails)} tras z pliku CSV")
        except Exception as e:
            logger.error(f"Błąd podczas wczytywania danych z CSV: {str(e)}")
            raise ValueError(f"Błąd podczas wczytywania danych z CSV: {str(e)}")
    
    def load_from_json(self, filepath: str) -> None:
        """
        Wczytuje dane o trasach z pliku JSON.
        
        Args:
            filepath: Ścieżka do pliku JSON.
            
        Raises:
            ValueError: Gdy nie udało się wczytać danych.
        """
        logger.info(f"Wczytywanie danych z pliku JSON: {filepath}")
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
                trail_records = data.get('trail_records', [])
                
                self.trails = [
                    TrailRecord(
                        id=record['id'],
                        name=record['name'],
                        region=record['region'],
                        start_lat=float(record['start_lat']),
                        start_lon=float(record['start_lon']),
                        end_lat=float(record['end_lat']),
                        end_lon=float(record['end_lon']),
                        length_km=float(record['length_km']),
                        elevation_gain=float(record['elevation_gain']),
                        difficulty=int(record['difficulty']),
                        terrain_type=record['terrain_type'],
                        tags=record['tags']
                    )
                    for record in trail_records
                ]
                self.filtered_trails = self.trails.copy()
                logger.info(f"Wczytano {len(self.trails)} tras z pliku JSON")
        except Exception as e:
            logger.error(f"Błąd podczas wczytywania danych z JSON: {str(e)}")
            raise ValueError(f"Błąd podczas wczytywania danych z JSON: {str(e)}")
    
    def filter_by_length(self, min_length: float = 0, max_length: float = float('inf')) -> List[TrailRecord]:
        """
        Filtruje trasy według długości.
        
        Args:
            min_length: Minimalna długość trasy w km.
            max_length: Maksymalna długość trasy w km.
            
        Returns:
            Lista przefiltrowanych tras.
        """
        logger.debug(f"Filtrowanie tras według długości: min={min_length} km, max={max_length} km")
        filtered = list(filter(
            lambda trail: min_length <= trail.length_km <= max_length,
            self.trails
        ))
        self.filtered_trails = filtered
        logger.info(f"Znaleziono {len(filtered)} tras spełniających kryteria długości")
        return filtered
    
    def filter_by_difficulty(self, difficulty: int) -> List[TrailRecord]:
        """
        Filtruje trasy według poziomu trudności.
        
        Args:
            difficulty: Poziom trudności trasy (1-5).
            
        Returns:
            Lista przefiltrowanych tras.
        """
        logger.debug(f"Filtrowanie tras według poziomu trudności: {difficulty}")
        filtered = list(filter(
            lambda trail: trail.difficulty == difficulty,
            self.filtered_trails
        ))
        self.filtered_trails = filtered
        logger.info(f"Znaleziono {len(filtered)} tras o poziomie trudności {difficulty}")
        return filtered
    
    def filter_by_region(self, region: str) -> List[TrailRecord]:
        """
        Filtruje trasy według regionu.
        
        Args:
            region: Region, w którym znajduje się trasa.
            
        Returns:
            Lista przefiltrowanych tras.
        """
        logger.debug(f"Filtrowanie tras według regionu: {region}")
        filtered = list(filter(
            lambda trail: trail.region == region,
            self.filtered_trails
        ))
        self.filtered_trails = filtered
        logger.info(f"Znaleziono {len(filtered)} tras w regionie {region}")
        return filtered
    
    def get_regions(self) -> List[str]:
        """
        Zwraca listę unikalnych regionów występujących w danych.
        
        Returns:
            Lista unikalnych regionów.
        """
        logger.debug("Pobieranie listy unikalnych regionów")
        regions = {trail.region for trail in self.trails}
        logger.debug(f"Znaleziono {len(regions)} unikalnych regionów")
        return sorted(regions)
    
    def get_difficulty_levels(self) -> List[int]:
        """
        Zwraca listę unikalnych poziomów trudności występujących w danych.
        
        Returns:
            Lista unikalnych poziomów trudności.
        """
        logger.debug("Pobieranie listy unikalnych poziomów trudności")
        difficulty_levels = {trail.difficulty for trail in self.trails}
        logger.debug(f"Znaleziono {len(difficulty_levels)} unikalnych poziomów trudności")
        return sorted(difficulty_levels)
    
    def get_terrain_types(self) -> List[str]:
        """
        Zwraca listę unikalnych typów terenu występujących w danych.
        
        Returns:
            Lista unikalnych typów terenu.
        """
        logger.debug("Pobieranie listy unikalnych typów terenu")
        terrain_types = {trail.terrain_type for trail in self.trails}
        logger.debug(f"Znaleziono {len(terrain_types)} unikalnych typów terenu")
        return sorted(terrain_types)
    
    def get_length_range(self) -> tuple:
        """
        Zwraca zakres długości tras (min, max).
        
        Returns:
            Krotka (min_length, max_length).
        """
        logger.debug("Obliczanie zakresu długości tras")
        if not self.trails:
            logger.warn("Brak danych o trasach do obliczenia zakresu długości")
            return (0, 0)
        
        min_length = min(trail.length_km for trail in self.trails)
        max_length = max(trail.length_km for trail in self.trails)
        
        logger.debug(f"Zakres długości tras: {min_length} - {max_length} km")
        return (min_length, max_length)
    
    def save_to_csv(self, filepath: str) -> None:
        """
        Zapisuje przefiltrowane dane do pliku CSV.
        
        Args:
            filepath: Ścieżka do pliku CSV.
            
        Raises:
            ValueError: Gdy nie udało się zapisać danych.
        """
        logger.info(f"Zapisywanie {len(self.filtered_trails)} tras do pliku CSV: {filepath}")
        
        def write_csv(filepath):
            fieldnames = [
                'id', 'name', 'region', 'start_lat', 'start_lon', 'end_lat', 'end_lon',
                'length_km', 'elevation_gain', 'difficulty', 'terrain_type', 'tags'
            ]
            
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for trail in self.filtered_trails:
                    writer.writerow({
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
        logger.info(f"Zapisywanie {len(self.filtered_trails)} tras do pliku JSON: {filepath}")
        
        def write_json(filepath):
            data = {
                'trail_records': [
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
                    for trail in self.filtered_trails
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=2, ensure_ascii=False)
        
        safe_file_operation(write_json, filepath, "JSON")
