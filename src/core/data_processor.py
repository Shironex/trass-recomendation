"""
Moduł do przetwarzania danych i generowania rekomendacji tras turystycznych.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, timedelta
from functools import reduce
from src.core.trail_data import TrailData, TrailRecord
from src.core.weather_data import WeatherData, WeatherRecord


class RouteRecommender:
    """
    Klasa do generowania rekomendacji tras turystycznych na podstawie
    danych o trasach i preferencji pogodowych użytkownika.
    """
    
    def __init__(self, trail_data: TrailData, weather_data: WeatherData):
        """
        Inicjalizacja obiektu RouteRecommender.
        
        Args:
            trail_data: Obiekt TrailData z danymi o trasach.
            weather_data: Obiekt WeatherData z danymi pogodowymi.
        """
        self.trail_data = trail_data
        self.weather_data = weather_data
    
    def filter_trails_by_params(self, 
                               min_length: Optional[float] = None,
                               max_length: Optional[float] = None,
                               difficulty: Optional[int] = None,
                               region: Optional[str] = None,
                               terrain_type: Optional[str] = None) -> List[TrailRecord]:
        """
        Filtruje trasy według podanych parametrów.
        
        Args:
            min_length: Minimalna długość trasy w km.
            max_length: Maksymalna długość trasy w km.
            difficulty: Poziom trudności trasy.
            region: Region, w którym znajduje się trasa.
            terrain_type: Typ terenu trasy.
            
        Returns:
            Lista przefiltrowanych tras.
        """
        # Resetowanie filtrów
        self.trail_data.filtered_trails = self.trail_data.trails.copy()
        
        # Filtrowanie po długości
        if min_length is not None or max_length is not None:
            min_len = min_length if min_length is not None else 0
            max_len = max_length if max_length is not None else float('inf')
            self.trail_data.filter_by_length(min_len, max_len)
        
        # Filtrowanie po trudności
        if difficulty is not None:
            self.trail_data.filter_by_difficulty(difficulty)
        
        # Filtrowanie po regionie
        if region is not None:
            self.trail_data.filter_by_region(region)
        
        return self.trail_data.filtered_trails
    
    def _calculate_weather_score(self, 
                               location: str, 
                               date_range: Tuple[date, date],
                               min_temp: float = 15.0,
                               max_temp: float = 25.0,
                               max_precipitation: float = 5.0,
                               min_sunshine_hours: float = 4.0) -> float:
        """
        Oblicza ocenę pogody dla danej lokalizacji i zakresu dat.
        
        Args:
            location: Identyfikator lokalizacji.
            date_range: Krotka (start_date, end_date).
            min_temp: Minimalna preferowana temperatura.
            max_temp: Maksymalna preferowana temperatura.
            max_precipitation: Maksymalna akceptowalna suma opadów.
            min_sunshine_hours: Minimalna preferowana liczba godzin słonecznych.
            
        Returns:
            Ocena pogody (0-100).
        """
        start_date, end_date = date_range
        
        # Pobieranie statystyk pogodowych
        stats = self.weather_data.calculate_statistics(location, start_date, end_date)
        
        # Ocena temperatury (0-40 punktów)
        avg_temp = stats['avg_temperature']
        temp_score = 0
        if min_temp <= avg_temp <= max_temp:
            temp_score = 40
        else:
            # Im dalej od preferowanego zakresu, tym mniejsza ocena
            distance = min(abs(avg_temp - min_temp), abs(avg_temp - max_temp))
            temp_score = max(0, 40 - (distance * 4))
        
        # Ocena opadów (0-30 punktów)
        precipitation = stats['total_precipitation']
        precip_score = 0
        if precipitation <= max_precipitation:
            precip_score = 30 * (1 - precipitation / max_precipitation)
        
        # Ocena nasłonecznienia (0-30 punktów)
        sunny_days = stats['sunny_days_count']
        total_days = (end_date - start_date).days + 1
        sunny_ratio = sunny_days / total_days if total_days > 0 else 0
        sunshine_score = 30 * sunny_ratio
        
        # Łączna ocena
        return temp_score + precip_score + sunshine_score
    
    def recommend_routes(self, 
                        weather_preferences: Dict[str, Any],
                        trail_params: Dict[str, Any],
                        start_date: date,
                        end_date: date,
                        limit: int = 5) -> List[Dict[str, Any]]:
        """
        Generuje rekomendacje tras na podstawie preferencji użytkownika.
        
        Args:
            weather_preferences: Słownik z preferencjami pogodowymi.
            trail_params: Słownik z parametrami tras.
            start_date: Data początkowa.
            end_date: Data końcowa.
            limit: Maksymalna liczba rekomendacji.
            
        Returns:
            Lista rekomendowanych tras z oceną.
        """
        # Filtrowanie tras według podanych parametrów
        filtered_trails = self.filter_trails_by_params(**trail_params)
        
        if not filtered_trails:
            return []
        
        # Obliczanie ocen dla każdej trasy
        scored_trails = []
        
        for trail in filtered_trails:
            # Obliczanie oceny pogody dla regionu trasy
            weather_score = self._calculate_weather_score(
                trail.region,
                (start_date, end_date),
                **weather_preferences
            )
            
            scored_trails.append({
                'trail': trail,
                'weather_score': weather_score,
                'total_score': weather_score  # Można rozbudować o inne czynniki
            })
        
        # Sortowanie tras według oceny (malejąco)
        scored_trails.sort(key=lambda x: x['total_score'], reverse=True)
        
        # Zwracanie najlepszych tras
        return [
            {
                'id': trail['trail'].id,
                'name': trail['trail'].name,
                'region': trail['trail'].region,
                'length_km': trail['trail'].length_km,
                'difficulty': trail['trail'].difficulty,
                'terrain_type': trail['trail'].terrain_type,
                'elevation_gain': trail['trail'].elevation_gain,
                'weather_score': trail['weather_score'],
                'total_score': trail['total_score']
            }
            for trail in scored_trails[:limit]
        ]
    
    def generate_weekly_recommendation(self, 
                                     weather_preferences: Dict[str, Any],
                                     trail_params: Dict[str, Any],
                                     start_date: Optional[date] = None) -> Dict[date, List[Dict[str, Any]]]:
        """
        Generuje rekomendacje tras na najbliższy tydzień.
        
        Args:
            weather_preferences: Słownik z preferencjami pogodowymi.
            trail_params: Słownik z parametrami tras.
            start_date: Data początkowa (domyślnie dzisiaj).
            
        Returns:
            Słownik, gdzie kluczem jest data, a wartością lista rekomendacji.
        """
        if start_date is None:
            start_date = date.today()
        
        recommendations = {}
        
        # Generowanie rekomendacji na każdy dzień tygodnia
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            
            # Rekomendacje na dany dzień
            daily_recommendations = self.recommend_routes(
                weather_preferences,
                trail_params,
                current_date,
                current_date,
                limit=3  # Mniej rekomendacji na dzień
            )
            
            recommendations[current_date] = daily_recommendations
        
        return recommendations
