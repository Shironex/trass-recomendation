"""
Moduł do obsługi danych o trasach turystycznych.
"""

import csv
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum, auto
from src.utils import ( logger, safe_file_operation )


class TrailCategory(Enum):
    """Kategorie tras turystycznych."""
    FAMILY = auto()      # Rodzinna
    SCENIC = auto()      # Widokowa
    SPORT = auto()       # Sportowa
    EXTREME = auto()     # Ekstremalna


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
    
    # Parametry dla szacowania czasu przejścia
    WALKING_SPEEDS = {
        'flat': 4.0,                  # km/h na płaskim terenie
        'mountain': 3.0,              # km/h w terenie górskim
        'lakeside': 4.5,              # km/h wokół jeziora
        'forest': 3.5,                # km/h w lesie
        'urban': 5.0,                 # km/h w terenie miejskim
        'hill': 3.2,                  # km/h na wzgórzach
        'coast': 4.0,                 # km/h wybrzeżem
        'meadow': 4.5,                # km/h po łące
        'rocky': 2.5,                 # km/h po skałach
        'desert': 3.0,                # km/h po pustyni
        'wetland': 2.5,               # km/h przez mokradła
        'canyon': 2.0                 # km/h w kanionie
    }
    
    # Domyślna prędkość dla nieznanego terenu (km/h)
    DEFAULT_SPEED = 3.5
    
    # Mnożniki trudności dla szacowania czasu
    DIFFICULTY_MULTIPLIER = {
        1: 1.0,    # Łatwa
        2: 1.2,    # Średnio łatwa
        3: 1.4,    # Średnia
        4: 1.6,    # Trudna
        5: 1.8     # Bardzo trudna
    }
    
    # Czas dodatkowy na każde 100m przewyższenia (w godzinach)
    ELEVATION_TIME_PER_100M = 0.1
    
    def calculate_center_point(self) -> Tuple[float, float]:
        """
        Oblicza środek trasy (średnia współrzędnych początku i końca).
        
        Returns:
            Krotka (latitude, longitude) ze współrzędnymi środka trasy.
        """
        center_lat = (self.start_lat + self.end_lat) / 2
        center_lon = (self.start_lon + self.end_lon) / 2
        return (center_lat, center_lon)
    
    def estimate_completion_time(self) -> float:
        """
        Szacuje czas przejścia trasy w godzinach.
        
        Uwzględnia:
        - Długość trasy
        - Przewyższenie (dodatkowy czas na każde 100m przewyższenia)
        - Trudność trasy (mnożnik czasu)
        - Typ terenu (różne prędkości dla różnych terenów)
        
        Returns:
            Szacowany czas przejścia w godzinach.
        """
        # Określenie prędkości poruszania się na podstawie terenu
        speed = self.WALKING_SPEEDS.get(self.terrain_type.lower(), self.DEFAULT_SPEED)
        
        # Podstawowy czas przejścia (długość / prędkość)
        base_time = self.length_km / speed
        
        # Dodatkowy czas na przewyższenie
        elevation_time = (self.elevation_gain / 100) * self.ELEVATION_TIME_PER_100M
        
        # Mnożnik trudności
        difficulty_multiplier = self.DIFFICULTY_MULTIPLIER.get(self.difficulty, 1.0)
        
        # Całkowity szacowany czas
        estimated_time = (base_time + elevation_time) * difficulty_multiplier
        
        return estimated_time
    
    def estimate_completion_time_formatted(self) -> str:
        """
        Zwraca szacowany czas przejścia trasy w formacie "Xh Ymin".
        
        Returns:
            String z czasem w formacie "Xh Ymin".
        """
        hours_total = self.estimate_completion_time()
        hours = int(hours_total)
        minutes = int((hours_total - hours) * 60)
        
        if hours == 0:
            return f"{minutes}min"
        else:
            return f"{hours}h {minutes}min"
    
    def check_preference_match(self, min_difficulty: int = 1, max_difficulty: int = 5,
                            min_length: float = 0, max_length: float = float('inf'),
                            max_elevation_gain: float = float('inf'),
                            preferred_regions: List[str] = None,
                            preferred_tags: List[str] = None) -> bool:
        """
        Sprawdza, czy trasa spełnia preferencje użytkownika.
        
        Args:
            min_difficulty: Minimalna akceptowalna trudność.
            max_difficulty: Maksymalna akceptowalna trudność.
            min_length: Minimalna akceptowalna długość trasy w km.
            max_length: Maksymalna akceptowalna długość trasy w km.
            max_elevation_gain: Maksymalne akceptowalne przewyższenie.
            preferred_regions: Lista preferowanych regionów.
            preferred_tags: Lista preferowanych tagów.
            
        Returns:
            True, jeśli trasa spełnia wszystkie preferencje, False w przeciwnym przypadku.
        """
        # Sprawdzenie trudności
        if self.difficulty < min_difficulty or self.difficulty > max_difficulty:
            return False
        
        # Sprawdzenie długości
        if self.length_km < min_length or self.length_km > max_length:
            return False
        
        # Sprawdzenie przewyższenia
        if self.elevation_gain > max_elevation_gain:
            return False
        
        # Sprawdzenie regionu
        if preferred_regions and self.region not in preferred_regions:
            return False
        
        # Sprawdzenie tagów (wystarczy jeden pasujący tag)
        if preferred_tags and not any(tag in self.tags for tag in preferred_tags):
            return False
        
        return True
    
    def categorize_trail(self) -> List[TrailCategory]:
        """
        Kategoryzuje trasę na podstawie jej parametrów.
        
        Kategorie:
        - FAMILY (Rodzinna): łatwa, niezbyt długa i z małym przewyższeniem
        - SCENIC (Widokowa): tagi wskazujące na walory krajobrazowe
        - SPORT (Sportowa): dłuższa, z większym przewyższeniem
        - EXTREME (Ekstremalna): bardzo trudna, duże przewyższenie
        
        Returns:
            Lista kategorii, do których należy trasa.
        """
        categories = []
        
        # Kategoria FAMILY (Rodzinna)
        if (self.difficulty <= 2 and 
            self.length_km <= 10 and 
            self.elevation_gain <= 300):
            categories.append(TrailCategory.FAMILY)
        
        # Kategoria SCENIC (Widokowa)
        scenic_tags = ['view', 'panorama', 'landscape', 'mountain', 'lake', 'forest', 'waterfall', 'viewpoint', 'widokowa']
        if any(tag in self.tags for tag in scenic_tags):
            categories.append(TrailCategory.SCENIC)
        
        # Kategoria SPORT (Sportowa)
        if (self.length_km >= 15 or 
            self.elevation_gain >= 500 or
            self.difficulty >= 3):
            categories.append(TrailCategory.SPORT)
        
        # Kategoria EXTREME (Ekstremalna)
        if (self.difficulty >= 4 and 
            (self.elevation_gain >= 1000 or self.length_km >= 25)):
            categories.append(TrailCategory.EXTREME)
        
        # Jeśli nie przypisano żadnej kategorii, przypisujemy domyślnie SCENIC
        if not categories:
            categories.append(TrailCategory.SCENIC)
        
        return categories
    
    def get_categories_names(self) -> List[str]:
        """
        Zwraca nazwy kategorii w języku polskim.
        
        Returns:
            Lista nazw kategorii.
        """
        categories = self.categorize_trail()
        
        names_map = {
            TrailCategory.FAMILY: "Rodzinna",
            TrailCategory.SCENIC: "Widokowa",
            TrailCategory.SPORT: "Sportowa",
            TrailCategory.EXTREME: "Ekstremalna"
        }
        
        return [names_map[category] for category in categories]


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
