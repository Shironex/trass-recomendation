"""
Moduł zawierający klasę preferencji użytkownika.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Tuple
from src.core.trail_data import TrailRecord
from src.core.weather_data import WeatherRecord
from src.utils import logger


@dataclass
class UserPreference:
    """
    Klasa przechowująca preferencje użytkownika dotyczące tras i pogody.
    
    Umożliwia obliczanie zgodności tras z preferencjami oraz aktualizację preferencji.
    """
    
    # Preferencje dotyczące pogody
    min_temperature: float = 15.0
    max_temperature: float = 25.0
    max_precipitation: float = 5.0
    min_sunshine_hours: float = 4.0
    
    # Preferencje dotyczące trasy
    max_difficulty: int = 5
    min_difficulty: int = 1
    max_length: float = float('inf')
    min_length: float = 0.0
    max_elevation_gain: float = float('inf')
    preferred_regions: List[str] = field(default_factory=list)
    preferred_terrain_types: List[str] = field(default_factory=list)
    preferred_tags: List[str] = field(default_factory=list)
    
    # Wagi preferencji (suma musi wynosić 100)
    weights: Dict[str, float] = field(default_factory=lambda: {
        'weather': 40.0,
        'difficulty': 20.0,
        'length': 20.0,
        'elevation': 10.0,
        'tags': 10.0
    })
    
    def __post_init__(self):
        """Sprawdza, czy preferencje są poprawne po inicjalizacji."""
        self._validate_weights()
    
    def _validate_weights(self) -> None:
        """Sprawdza, czy suma wag wynosi 100."""
        weights_sum = sum(self.weights.values())
        if abs(weights_sum - 100) > 0.01:
            logger.warn(f"Suma wag preferencji nie wynosi 100 (wynosi {weights_sum}). Normalizacja wag.")
            factor = 100 / weights_sum
            self.weights = {k: v * factor for k, v in self.weights.items()}
    
    def update_preferences(self, **kwargs) -> None:
        """
        Aktualizuje preferencje użytkownika.
        
        Args:
            **kwargs: Słownik z nowymi wartościami preferencji.
        """
        logger.debug(f"Aktualizacja preferencji użytkownika: {kwargs}")
        
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
                logger.debug(f"Zaktualizowano preferencję '{key}' na wartość '{value}'")
            else:
                logger.warn(f"Nieznana preferencja: '{key}'")
        
        # Po aktualizacji wag należy je znormalizować
        if 'weights' in kwargs:
            self._validate_weights()
    
    def update_weights(self, **kwargs) -> None:
        """
        Aktualizuje wagi preferencji.
        
        Args:
            **kwargs: Słownik z nowymi wartościami wag.
        """
        logger.debug(f"Aktualizacja wag preferencji: {kwargs}")
        
        for key, value in kwargs.items():
            if key in self.weights:
                self.weights[key] = value
                logger.debug(f"Zaktualizowano wagę '{key}' na wartość '{value}'")
            else:
                logger.warn(f"Nieznana waga preferencji: '{key}'")
        
        self._validate_weights()
    
    def check_trail_match(self, trail: TrailRecord) -> Tuple[bool, float]:
        """
        Sprawdza dopasowanie trasy do preferencji użytkownika.
        
        Args:
            trail: Obiekt trasy do sprawdzenia.
            
        Returns:
            Krotka (czy_spełnia_minimalne_wymagania, ocena_dopasowania).
        """
        logger.debug(f"Sprawdzanie dopasowania trasy {trail.name} do preferencji")
        
        # Sprawdzenie minimalnych wymagań (warunki brzegowe)
        if trail.difficulty < self.min_difficulty or trail.difficulty > self.max_difficulty:
            logger.debug(f"Trasa nie spełnia wymagań trudności: {trail.difficulty}")
            return False, 0.0
        
        if trail.length_km < self.min_length or trail.length_km > self.max_length:
            logger.debug(f"Trasa nie spełnia wymagań długości: {trail.length_km}")
            return False, 0.0
        
        if trail.elevation_gain > self.max_elevation_gain:
            logger.debug(f"Trasa nie spełnia wymagań przewyższenia: {trail.elevation_gain}")
            return False, 0.0
        
        if self.preferred_regions and trail.region not in self.preferred_regions:
            logger.debug(f"Trasa nie jest w preferowanym regionie: {trail.region}")
            return False, 0.0
        
        # Obliczenie oceny dopasowania
        difficulty_score = self._calculate_difficulty_score(trail)
        length_score = self._calculate_length_score(trail)
        elevation_score = self._calculate_elevation_score(trail)
        tags_score = self._calculate_tags_score(trail)
        
        # Ważona ocena dopasowania bez pogody (pogoda jest obliczana osobno)
        matching_score = (
            difficulty_score * (self.weights['difficulty'] / 100) +
            length_score * (self.weights['length'] / 100) +
            elevation_score * (self.weights['elevation'] / 100) +
            tags_score * (self.weights['tags'] / 100)
        )
        
        # Normalizacja do zakresu 0-1
        normalized_score = matching_score / (1 - (self.weights['weather'] / 100))
        
        logger.debug(f"Ocena dopasowania trasy: {normalized_score:.2f}")
        return True, normalized_score
    
    def _calculate_difficulty_score(self, trail: TrailRecord) -> float:
        """
        Oblicza ocenę dopasowania trudności trasy.
        
        Args:
            trail: Obiekt trasy.
            
        Returns:
            Ocena dopasowania trudności (0-1).
        """
        # Preferujemy trasę bliżej środka zakresu trudności
        preferred_difficulty = (self.min_difficulty + self.max_difficulty) / 2
        difficulty_range = self.max_difficulty - self.min_difficulty
        
        if difficulty_range == 0:
            return 1.0 if trail.difficulty == preferred_difficulty else 0.0
        
        # Im bliżej preferowanej trudności, tym wyższa ocena
        distance = abs(trail.difficulty - preferred_difficulty)
        normalized_distance = distance / (difficulty_range / 2)
        score = max(0, 1 - normalized_distance)
        
        return score
    
    def _calculate_length_score(self, trail: TrailRecord) -> float:
        """
        Oblicza ocenę dopasowania długości trasy.
        
        Args:
            trail: Obiekt trasy.
            
        Returns:
            Ocena dopasowania długości (0-1).
        """
        if self.max_length == float('inf'):
            # Jeśli nie określono maksymalnej długości, preferujemy krótsze trasy
            return max(0, 1 - (trail.length_km / 50))  # Zakładamy, że 50km to długa trasa
        
        # Preferujemy trasę bliżej środka zakresu długości
        preferred_length = (self.min_length + self.max_length) / 2
        length_range = self.max_length - self.min_length
        
        if length_range == 0:
            return 1.0 if trail.length_km == preferred_length else 0.0
        
        # Im bliżej preferowanej długości, tym wyższa ocena
        distance = abs(trail.length_km - preferred_length)
        normalized_distance = distance / (length_range / 2)
        score = max(0, 1 - normalized_distance)
        
        return score
    
    def _calculate_elevation_score(self, trail: TrailRecord) -> float:
        """
        Oblicza ocenę dopasowania przewyższenia trasy.
        
        Args:
            trail: Obiekt trasy.
            
        Returns:
            Ocena dopasowania przewyższenia (0-1).
        """
        if self.max_elevation_gain == float('inf'):
            # Jeśli nie określono maksymalnego przewyższenia, preferujemy mniejsze przewyższenia
            return max(0, 1 - (trail.elevation_gain / 1500))  # 1500m to duże przewyższenie
        
        # Im mniejsze przewyższenie, tym lepsza ocena (z punktu widzenia wysiłku)
        return max(0, 1 - (trail.elevation_gain / self.max_elevation_gain))
    
    def _calculate_tags_score(self, trail: TrailRecord) -> float:
        """
        Oblicza ocenę dopasowania tagów trasy.
        
        Args:
            trail: Obiekt trasy.
            
        Returns:
            Ocena dopasowania tagów (0-1).
        """
        if not self.preferred_tags:
            return 1.0  # Brak preferencji oznacza pełne dopasowanie
        
        # Liczymy, ile preferowanych tagów ma trasa
        matching_tags = set(trail.tags).intersection(set(self.preferred_tags))
        
        # Ocena to stosunek liczby pasujących tagów do liczby preferowanych tagów
        return len(matching_tags) / len(self.preferred_tags)
    
    def calculate_weather_match(self, weather: WeatherRecord) -> Tuple[bool, float]:
        """
        Sprawdza dopasowanie pogody do preferencji użytkownika.
        
        Args:
            weather: Obiekt pogody do sprawdzenia.
            
        Returns:
            Krotka (czy_spełnia_minimalne_wymagania, ocena_dopasowania).
        """
        logger.debug(f"Sprawdzanie dopasowania pogody z {weather.date} do preferencji")
        
        # Ocena temperatury (0-1)
        temp_score = self._calculate_temperature_score(weather)
        
        # Ocena opadów (0-1)
        precip_score = self._calculate_precipitation_score(weather)
        
        # Ocena nasłonecznienia (0-1)
        sunshine_score = self._calculate_sunshine_score(weather)
        
        # Średnia ważona ocen
        weather_score = (temp_score + precip_score + sunshine_score) / 3
        
        # Minimalne wymagania - temperatura musi być w zakresie, opady nie mogą być za duże
        meets_requirements = (
            self.min_temperature <= weather.avg_temp <= self.max_temperature and
            weather.precipitation <= self.max_precipitation
        )
        
        logger.debug(f"Ocena dopasowania pogody: {weather_score:.2f}")
        return meets_requirements, weather_score
    
    def _calculate_temperature_score(self, weather: WeatherRecord) -> float:
        """
        Oblicza ocenę dopasowania temperatury.
        
        Args:
            weather: Obiekt pogody.
            
        Returns:
            Ocena dopasowania temperatury (0-1).
        """
        # Preferujemy temperaturę bliżej środka zakresu
        preferred_temp = (self.min_temperature + self.max_temperature) / 2
        temp_range = self.max_temperature - self.min_temperature
        
        if temp_range == 0:
            return 1.0 if weather.avg_temp == preferred_temp else 0.0
        
        # Im bliżej preferowanej temperatury, tym wyższa ocena
        distance = abs(weather.avg_temp - preferred_temp)
        normalized_distance = distance / (temp_range / 2)
        score = max(0, 1 - normalized_distance)
        
        return score
    
    def _calculate_precipitation_score(self, weather: WeatherRecord) -> float:
        """
        Oblicza ocenę dopasowania opadów.
        
        Args:
            weather: Obiekt pogody.
            
        Returns:
            Ocena dopasowania opadów (0-1).
        """
        # Im mniej opadów, tym lepsza ocena
        if self.max_precipitation == 0:
            return 1.0 if weather.precipitation == 0 else 0.0
        
        score = max(0, 1 - (weather.precipitation / self.max_precipitation))
        return score
    
    def _calculate_sunshine_score(self, weather: WeatherRecord) -> float:
        """
        Oblicza ocenę dopasowania godzin słonecznych.
        
        Args:
            weather: Obiekt pogody.
            
        Returns:
            Ocena dopasowania godzin słonecznych (0-1).
        """
        # Im więcej godzin słonecznych, tym lepsza ocena (do pewnego limitu)
        if weather.sunshine_hours >= self.min_sunshine_hours:
            return 1.0
        
        # Liniowy spadek oceny dla mniejszej liczby godzin słonecznych
        score = weather.sunshine_hours / self.min_sunshine_hours
        return max(0, score)
    
    def calculate_overall_match(self, trail: TrailRecord, weather: WeatherRecord) -> Tuple[bool, float]:
        """
        Oblicza ogólne dopasowanie trasy i pogody do preferencji użytkownika.
        
        Args:
            trail: Obiekt trasy.
            weather: Obiekt pogody.
            
        Returns:
            Krotka (czy_spełnia_minimalne_wymagania, ocena_dopasowania).
        """
        # Sprawdzenie dopasowania trasy
        trail_meets_req, trail_score = self.check_trail_match(trail)
        if not trail_meets_req:
            return False, 0.0
        
        # Sprawdzenie dopasowania pogody
        weather_meets_req, weather_score = self.calculate_weather_match(weather)
        if not weather_meets_req:
            return False, 0.0
        
        # Obliczenie ogólnej oceny z uwzględnieniem wag
        overall_score = (
            trail_score * (1 - (self.weights['weather'] / 100)) +
            weather_score * (self.weights['weather'] / 100)
        )
        
        return True, overall_score 