"""
Moduł do przetwarzania danych i generowania rekomendacji tras turystycznych.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, timedelta
from src.core.trail_data import TrailData
from src.core.weather_data import WeatherData
from src.utils import logger


class RouteRecommender:
    """
    Klasa do generowania rekomendacji tras turystycznych na podstawie
    danych o trasach i preferencji pogodowych użytkownika.
    """
    
    # Wagi używane do obliczania oceny pogody
    WEATHER_SCORE_WEIGHTS = {
        'temperature': 40,
        'precipitation': 30, 
        'sunshine': 30
    }
    
    def __init__(self, trail_data: TrailData, weather_data: WeatherData):
        """
        Inicjalizacja obiektu RouteRecommender.
        
        Args:
            trail_data: Obiekt TrailData z danymi o trasach.
            weather_data: Obiekt WeatherData z danymi pogodowymi.
        """
        logger.debug("Inicjalizacja systemu rekomendacji")
        self.trail_data = trail_data
        self.weather_data = weather_data
    
    def filter_trails_by_params(self, **params):
        """
        Filtruje trasy według podanych parametrów.
        
        Args:
            **params: Słownik z parametrami filtrowania:
                - min_length: Minimalna długość trasy w km
                - max_length: Maksymalna długość trasy w km
                - min_difficulty: Minimalny poziom trudności (1-5)
                - max_difficulty: Maksymalny poziom trudności (1-5)
                - region: Region trasy
            
        Returns:
            list: Lista przefiltrowanych tras
        """
        logger.debug(f"[filter_trails_by_params] Filtruję trasy z parametrami: {params}")
        filtered_trails = self.trail_data.trails
        
        # Filtrowanie według długości minimalnej
        if 'min_length' in params:
            filtered_trails = [t for t in filtered_trails if t.length_km >= params['min_length']]
            logger.debug(f"[filter_trails_by_params] Po filtracji min_length: {len(filtered_trails)} tras")
        
        # Filtrowanie według długości maksymalnej
        if 'max_length' in params:
            filtered_trails = [t for t in filtered_trails if t.length_km <= params['max_length']]
            logger.debug(f"[filter_trails_by_params] Po filtracji max_length: {len(filtered_trails)} tras")
        
        # Filtrowanie według trudności (zakres)
        if 'min_difficulty' in params or 'max_difficulty' in params:
            min_diff = params.get('min_difficulty', 1)
            max_diff = params.get('max_difficulty', 5)
            filtered_trails = [t for t in filtered_trails if min_diff <= t.difficulty <= max_diff]
            logger.debug(f"[filter_trails_by_params] Po filtracji difficulty: {len(filtered_trails)} tras")
        # Zachowujemy stare filtrowanie po trudności dla kompatybilności wstecznej
        elif 'difficulty' in params:
            filtered_trails = [t for t in filtered_trails if t.difficulty == params['difficulty']]
            logger.debug(f"[filter_trails_by_params] Po filtracji difficulty: {len(filtered_trails)} tras")
        
        # Filtrowanie według regionu
        if 'region' in params:
            filtered_trails = [t for t in filtered_trails if t.region == params['region']]
            logger.debug(f"[filter_trails_by_params] Po filtracji region: {len(filtered_trails)} tras")
        
        logger.debug(f"[filter_trails_by_params] Wynik filtracji: {len(filtered_trails)} tras")
        return filtered_trails
    
    def _calculate_weather_score(self, 
                               location: str, 
                               date_range: Tuple[date, date],
                               min_temp: float = 15.0,
                               max_temp: float = 25.0,
                               max_precipitation: float = 5.0,
                               min_sunshine_hours: float = 4.0,
                               max_sunshine_hours: float = 12.0,
                               temperature_weight: float = None,
                               precipitation_weight: float = None,
                               sunshine_weight: float = None) -> float:
        """
        Oblicza ocenę pogody dla danej lokalizacji i zakresu dat.
        
        Args:
            location: Identyfikator lokalizacji.
            date_range: Krotka (start_date, end_date).
            min_temp: Minimalna preferowana temperatura.
            max_temp: Maksymalna preferowana temperatura.
            max_precipitation: Maksymalna akceptowalna suma opadów.
            min_sunshine_hours: Minimalna preferowana liczba godzin słonecznych.
            max_sunshine_hours: Maksymalna preferowana liczba godzin słonecznych.
            temperature_weight: Waga temperatury w ocenie (domyślnie WEATHER_SCORE_WEIGHTS['temperature']).
            precipitation_weight: Waga opadów w ocenie (domyślnie WEATHER_SCORE_WEIGHTS['precipitation']).
            sunshine_weight: Waga nasłonecznienia w ocenie (domyślnie WEATHER_SCORE_WEIGHTS['sunshine']).
            
        Returns:
            Ocena pogody (0-100).
        """
        logger.debug(f"[_calculate_weather_score] Obliczanie oceny pogody dla lokalizacji: {location}")
        start_date, end_date = date_range
        
        # Używanie domyślnych wag jeśli nie podano innych
        if temperature_weight is None:
            temperature_weight = self.WEATHER_SCORE_WEIGHTS['temperature']
        if precipitation_weight is None:
            precipitation_weight = self.WEATHER_SCORE_WEIGHTS['precipitation']
        if sunshine_weight is None:
            sunshine_weight = self.WEATHER_SCORE_WEIGHTS['sunshine']
        
        try:
            # Pobieranie statystyk pogodowych
            stats = self.weather_data.calculate_statistics(location, start_date, end_date)
            logger.debug(f"[_calculate_weather_score] Statystyki pogodowe: {stats}")
            
            # Ocena temperatury
            avg_temp = stats['avg_temperature']
            temp_score = 0
            if min_temp <= avg_temp <= max_temp:
                temp_score = temperature_weight
            else:
                # Im dalej od preferowanego zakresu, tym mniejsza ocena
                distance = min(abs(avg_temp - min_temp), abs(avg_temp - max_temp))
                temp_score = max(0, temperature_weight - (distance * 4))
            logger.debug(f"[_calculate_weather_score] Ocena temperatury: {temp_score:.2f}")
            
            # Ocena opadów
            precipitation = stats['total_precipitation']
            precip_score = 0
            if precipitation <= max_precipitation:
                precip_score = precipitation_weight * (1 - precipitation / max_precipitation)
            logger.debug(f"[_calculate_weather_score] Ocena opadów: {precip_score:.2f}")
            
            # Ocena nasłonecznienia
            avg_sunshine = stats.get('avg_sunshine_hours', 0)
            sunshine_score = 0
            if min_sunshine_hours <= avg_sunshine <= max_sunshine_hours:
                sunshine_score = sunshine_weight
            else:
                # Im dalej od preferowanego zakresu, tym mniejsza ocena
                distance = min(abs(avg_sunshine - min_sunshine_hours), 
                             abs(avg_sunshine - max_sunshine_hours))
                sunshine_score = max(0, sunshine_weight - (distance * 4))
            logger.debug(f"[_calculate_weather_score] Ocena nasłonecznienia: {sunshine_score:.2f}")
            
            # Łączna ocena
            total_score = temp_score + precip_score + sunshine_score
            logger.debug(f"[_calculate_weather_score] Łączna ocena pogody: {total_score:.2f}")
            return total_score
            
        except Exception as e:
            import traceback
            logger.error(f"[_calculate_weather_score] Obliczanie oceny pogody nie powiodło się: {str(e)}")
            logger.debug(f"[_calculate_weather_score] Szczegóły błędu: {traceback.format_exc()}")
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
        logger.info("--- ROZPOCZĘCIE GENEROWANIA REKOMENDACJI ---")
        logger.debug("[recommend_routes] Rozpoczęcie generowania rekomendacji")
        
        # Sprawdzenie poprawności danych wejściowych
        if not self.trail_data.trails or not self.weather_data.records:
            logger.debug("[recommend_routes] Brak danych wejściowych")
            return []
        
        try:
            # Filtrowanie tras według podanych parametrów
            logger.debug(f"[recommend_routes] Filtrowanie tras: {trail_params}")
            filtered_trails = self.filter_trails_by_params(**trail_params)
            logger.debug(f"[recommend_routes] Znaleziono {len(filtered_trails)} tras po filtrowaniu")
            
            if not filtered_trails:
                logger.debug("[recommend_routes] Brak tras po filtrowaniu")
                return []
            
            # Używamy map() do obliczenia ocen dla każdej trasy
            date_range = (start_date, end_date)
            scored_trails = list(self.calculate_trail_scores(filtered_trails, date_range, weather_preferences))
            logger.debug(f"[recommend_routes] Oceniono {len(scored_trails)} tras")
            
            if not scored_trails:
                logger.debug("[recommend_routes] Brak tras po ocenie")
                return []
            
            # Sortowanie tras według oceny (malejąco)
            logger.debug("[recommend_routes] Sortowanie tras według oceny")
            scored_trails.sort(key=lambda x: x['total_score'], reverse=True)
            
            # Ograniczenie do żądanej liczby rezultatów
            top_trails = scored_trails[:limit] if limit > 0 else scored_trails
            logger.debug(f"[recommend_routes] Wybrano {len(top_trails)} najlepszych tras")
            
            # Przygotowanie wyników
            results = []
            for i, trail in enumerate(top_trails):
                try:
                    logger.debug(f"[recommend_routes] Przygotowanie danych dla trasy #{i+1}: {trail['trail'].name}")
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
                    logger.error(f"[recommend_routes] Problem z przygotowaniem danych trasy: {str(e)}")
                    continue
            
            logger.debug(f"[recommend_routes] Zakończenie generowania rekomendacji, znaleziono {len(results)} tras")
            return results
            
        except Exception as e:
            # Logowanie błędu dla debugowania
            import traceback
            logger.error(f"[recommend_routes] Generowanie rekomendacji nie powiodło się: {str(e)}")
            logger.debug(f"[recommend_routes] Szczegóły błędu: {traceback.format_exc()}")
            return []
    
    def calculate_trail_scores(self, 
                              trails: List[Any], 
                              date_range: Tuple[date, date], 
                              weather_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Oblicza oceny dla listy tras używając funkcji map().
        
        Args:
            trails: Lista tras do oceny.
            date_range: Krotka (start_date, end_date).
            weather_preferences: Słownik z preferencjami pogodowymi.
            
        Returns:
            Lista tras z ocenami.
        """
        logger.debug(f"[calculate_trail_scores] Rozpoczęcie oceniania {len(trails)} tras")
        
        def score_trail(trail):
            try:
                # Obliczanie oceny pogody dla regionu trasy
                weather_score = self._calculate_weather_score(
                    trail.region,
                    date_range,
                    **weather_preferences
                )
                
                return {
                    'trail': trail,
                    'weather_score': weather_score,
                    'total_score': weather_score  # Można rozbudować o inne czynniki
                }
            except Exception as e:
                logger.error(f"[score_trail] Problem z oceną trasy {trail.name}: {str(e)}")
                return None
        
        # Używamy map do przetwarzania każdej trasy, a następnie filtrujemy None
        scored_trails = list(map(score_trail, trails))
        return [trail for trail in scored_trails if trail is not None]
    
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
        # Ustawienie daty początkowej
        if start_date is None:
            start_date = date.today()
            
        logger.debug(f"[generate_weekly_recommendation] Generowanie rekomendacji na tydzień od {start_date}")
        
        # Słownik na wyniki
        recommendations = {}
        
        # Generowanie rekomendacji na każdy dzień tygodnia
        for day_offset in range(7):
            current_date = start_date + timedelta(days=day_offset)
            logger.debug(f"[generate_weekly_recommendation] Generowanie rekomendacji na {current_date}")
            
            # Ustawienie daty końcowej jako bieżący dzień (rekomendacje na 1 dzień)
            end_date = current_date
            
            # Generowanie rekomendacji na dany dzień
            daily_recommendations = self.recommend_routes(
                weather_preferences=weather_preferences,
                trail_params=trail_params,
                start_date=current_date,
                end_date=end_date,
                limit=3  # Ograniczamy do 3 rekomendacji na dzień
            )
            
            # Zapisanie rekomendacji dla danego dnia
            recommendations[current_date] = daily_recommendations
            logger.debug(f"[generate_weekly_recommendation] Znaleziono {len(daily_recommendations)} tras na {current_date}")
            
        logger.debug("[generate_weekly_recommendation] Zakończenie generowania rekomendacji tygodniowych")
        return recommendations
