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
    
    def filter_trails_by_params(self, **params):
        """
        Filtruje trasy według podanych parametrów.
        
        Args:
            **params: Słownik z parametrami filtrowania (min_length, max_length, difficulty, region)
            
        Returns:
            list: Lista przefiltrowanych tras
        """
        print(f"DEBUG: [filter_trails_by_params] Filtruję trasy z parametrami: {params}")
        filtered_trails = self.trail_data.trails
        
        # Filtrowanie według długości minimalnej
        if 'min_length' in params:
            filtered_trails = [t for t in filtered_trails if t.length_km >= params['min_length']]
            print(f"DEBUG: [filter_trails_by_params] Po filtracji min_length: {len(filtered_trails)} tras")
        
        # Filtrowanie według długości maksymalnej
        if 'max_length' in params:
            filtered_trails = [t for t in filtered_trails if t.length_km <= params['max_length']]
            print(f"DEBUG: [filter_trails_by_params] Po filtracji max_length: {len(filtered_trails)} tras")
        
        # Filtrowanie według trudności
        if 'difficulty' in params:
            filtered_trails = [t for t in filtered_trails if t.difficulty == params['difficulty']]
            print(f"DEBUG: [filter_trails_by_params] Po filtracji difficulty: {len(filtered_trails)} tras")
        
        # Filtrowanie według regionu
        if 'region' in params:
            filtered_trails = [t for t in filtered_trails if t.region == params['region']]
            print(f"DEBUG: [filter_trails_by_params] Po filtracji region: {len(filtered_trails)} tras")
        
        print(f"DEBUG: [filter_trails_by_params] Wynik filtracji: {len(filtered_trails)} tras")
        return filtered_trails
    
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
        print(f"DEBUG: [_calculate_weather_score] Obliczanie oceny pogody dla lokalizacji: {location}")
        start_date, end_date = date_range
        
        try:
            # Pobieranie statystyk pogodowych
            stats = self.weather_data.calculate_statistics(location, start_date, end_date)
            print(f"DEBUG: [_calculate_weather_score] Statystyki pogodowe: {stats}")
            
            # Ocena temperatury (0-40 punktów)
            avg_temp = stats['avg_temperature']
            temp_score = 0
            if min_temp <= avg_temp <= max_temp:
                temp_score = 40
            else:
                # Im dalej od preferowanego zakresu, tym mniejsza ocena
                distance = min(abs(avg_temp - min_temp), abs(avg_temp - max_temp))
                temp_score = max(0, 40 - (distance * 4))
            print(f"DEBUG: [_calculate_weather_score] Ocena temperatury: {temp_score:.2f}")
            
            # Ocena opadów (0-30 punktów)
            precipitation = stats['total_precipitation']
            precip_score = 0
            if precipitation <= max_precipitation:
                precip_score = 30 * (1 - precipitation / max_precipitation)
            print(f"DEBUG: [_calculate_weather_score] Ocena opadów: {precip_score:.2f}")
            
            # Ocena nasłonecznienia (0-30 punktów)
            sunny_days = stats['sunny_days_count']
            total_days = (end_date - start_date).days + 1
            sunny_ratio = sunny_days / total_days if total_days > 0 else 0
            sunshine_score = 30 * sunny_ratio
            print(f"DEBUG: [_calculate_weather_score] Ocena nasłonecznienia: {sunshine_score:.2f}")
            
            # Łączna ocena
            total_score = temp_score + precip_score + sunshine_score
            print(f"DEBUG: [_calculate_weather_score] Łączna ocena pogody: {total_score:.2f}")
            return total_score
            
        except Exception as e:
            import traceback
            print(f"BŁĄD: [_calculate_weather_score] Obliczanie oceny pogody nie powiodło się: {str(e)}")
            print(f"BŁĄD: [_calculate_weather_score] Szczegóły błędu: {traceback.format_exc()}")
            # Zwracamy niską ocenę w przypadku błędu, aby nie eliminować trasy
            return 0.0
    
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
        print("DEBUG: [recommend_routes] Rozpoczęcie generowania rekomendacji")
        
        # Sprawdzenie poprawności danych wejściowych
        if not self.trail_data.trails or not self.weather_data.records:
            print("DEBUG: [recommend_routes] Brak danych wejściowych")
            return []
        
        try:
            # Filtrowanie tras według podanych parametrów
            print(f"DEBUG: [recommend_routes] Filtrowanie tras: {trail_params}")
            filtered_trails = self.filter_trails_by_params(**trail_params)
            print(f"DEBUG: [recommend_routes] Znaleziono {len(filtered_trails)} tras po filtrowaniu")
            
            if not filtered_trails:
                print("DEBUG: [recommend_routes] Brak tras po filtrowaniu")
                return []
            
            # Obliczanie ocen dla każdej trasy
            scored_trails = []
            print(f"DEBUG: [recommend_routes] Rozpoczęcie oceniania {len(filtered_trails)} tras")
            
            for i, trail in enumerate(filtered_trails):
                try:
                    print(f"DEBUG: [recommend_routes] Ocenianie trasy #{i+1}: {trail.name} (region: {trail.region})")
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
                    print(f"DEBUG: [recommend_routes] Trasa {trail.name} oceniona na {weather_score:.2f}")
                except Exception as e:
                    # Jeśli obliczenie oceny dla jednej trasy się nie powiedzie, 
                    # kontynuujemy dla pozostałych
                    print(f"BŁĄD: [recommend_routes] Problem z oceną trasy {trail.name}: {str(e)}")
                    continue
            
            if not scored_trails:
                print("DEBUG: [recommend_routes] Brak tras po ocenie")
                return []
            
            # Sortowanie tras według oceny (malejąco)
            print("DEBUG: [recommend_routes] Sortowanie tras według oceny")
            scored_trails.sort(key=lambda x: x['total_score'], reverse=True)
            
            # Ograniczenie do żądanej liczby rezultatów
            top_trails = scored_trails[:limit] if limit > 0 else scored_trails
            print(f"DEBUG: [recommend_routes] Wybrano {len(top_trails)} najlepszych tras")
            
            # Przygotowanie wyników
            results = []
            for i, trail in enumerate(top_trails):
                try:
                    print(f"DEBUG: [recommend_routes] Przygotowanie danych dla trasy #{i+1}: {trail['trail'].name}")
                    results.append({
                        'id': trail['trail'].id,
                        'name': trail['trail'].name,
                        'region': trail['trail'].region,
                        'length_km': trail['trail'].length_km,
                        'difficulty': trail['trail'].difficulty,
                        'terrain_type': trail['trail'].terrain_type,
                        'elevation_gain': trail['trail'].elevation_gain,
                        'weather_score': trail['weather_score'],
                        'total_score': trail['total_score']
                    })
                except Exception as e:
                    # Jeśli przygotowanie jednego wyniku się nie powiedzie,
                    # kontynuujemy dla pozostałych
                    print(f"BŁĄD: [recommend_routes] Problem z przygotowaniem danych trasy: {str(e)}")
                    continue
            
            print(f"DEBUG: [recommend_routes] Zakończenie generowania rekomendacji, znaleziono {len(results)} tras")
            return results
            
        except Exception as e:
            # Logowanie błędu dla debugowania
            import traceback
            print(f"BŁĄD: [recommend_routes] Generowanie rekomendacji nie powiodło się: {str(e)}")
            print(f"BŁĄD: [recommend_routes] Szczegóły błędu: {traceback.format_exc()}")
            return []
    
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
