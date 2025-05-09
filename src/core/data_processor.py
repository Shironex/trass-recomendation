"""
Moduł do przetwarzania danych i generowania rekomendacji tras turystycznych.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import date, timedelta
from src.core.trail_data import TrailData, TrailRecord, TrailCategory
from src.core.weather_data import WeatherData, WeatherRecord
from src.core.user_preference import UserPreference
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
        self.user_preference = None  # Będzie ustawione później przez set_user_preference()
    
    def set_user_preference(self, preference: UserPreference) -> None:
        """
        Ustawia preferencje użytkownika dla systemu rekomendacji.
        
        Args:
            preference: Obiekt UserPreference z preferencjami użytkownika.
        """
        logger.debug("Ustawianie preferencji użytkownika")
        self.user_preference = preference
    
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
                - categories: Lista kategorii tras (np. ["Rodzinna", "Widokowa"])
            
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
        
        # Filtrowanie według kategorii tras
        if 'categories' in params and params['categories']:
            filtered_trails = [
                t for t in filtered_trails 
                if any(category in t.get_categories_names() for category in params['categories'])
            ]
            logger.debug(f"[filter_trails_by_params] Po filtracji categories: {len(filtered_trails)} tras")
        
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
    
    def calculate_trail_scores(self, 
                              trails: List[TrailRecord], 
                              date_range: Tuple[date, date], 
                              weather_preferences: Dict[str, Any] = None,
                              user_preference: UserPreference = None) -> List[Dict[str, Any]]:
        """
        Oblicza oceny dla tras na podstawie pogody i preferencji użytkownika.
        
        Args:
            trails: Lista tras do oceny.
            date_range: Krotka (start_date, end_date).
            weather_preferences: Słownik z preferencjami pogodowymi (opcjonalny, kompatybilność wsteczna).
            user_preference: Obiekt UserPreference z preferencjami użytkownika (opcjonalny).
            
        Returns:
            Lista tras z ocenami.
        """
        logger.debug(f"[calculate_trail_scores] Obliczanie ocen dla {len(trails)} tras")
        
        # Używamy przekazanych preferencji lub tych zapisanych w obiekcie
        user_pref = user_preference or self.user_preference
        
        # Funkcja oceniająca trasę
        def score_trail(trail):
            trail_result = {
                'trail': trail,
                'id': trail.id,  # Dodajemy id bezpośrednio do wyników
                'name': trail.name,  # Dodajemy nazwę bezpośrednio do wyników
                'categories': trail.get_categories_names(),
                'estimated_time': trail.estimate_completion_time_formatted()
            }
            
            # Ocena na podstawie preferencji użytkownika
            if user_pref:
                # Sprawdzenie indeksu komfortu dla pogody
                location = trail.region
                comfort_index = self.weather_data.calculate_avg_comfort_index(
                    location, date_range[0], date_range[1]
                )
                
                # Sprawdzenie dopasowania trasy do preferencji
                meets_requirements, score = user_pref.check_trail_match(trail)
                
                trail_result['weather_comfort_index'] = round(comfort_index, 1)
                trail_result['preference_match_score'] = round(score * 100, 1)
                
                # Całkowita ocena (ważona)
                if meets_requirements:
                    # Połączenie oceny trasy i pogody według wag
                    trail_result['total_score'] = round(
                        (score * (100 - user_pref.weights['weather']) + 
                         (comfort_index * user_pref.weights['weather'] / 100)) / 100 * 100, 
                        1
                    )
                else:
                    trail_result['total_score'] = 0
            
            # Stary sposób obliczania oceny (kompatybilność wsteczna)
            elif weather_preferences:
                try:
                    weather_score = self._calculate_weather_score(
                        trail.region, date_range, **weather_preferences
                    )
                    trail_result['weather_score'] = round(weather_score, 1)
                    trail_result['total_score'] = trail_result['weather_score']
                except Exception as e:
                    logger.error(f"[score_trail] Błąd podczas obliczania oceny pogody: {e}")
                    trail_result['weather_score'] = 0
                    trail_result['total_score'] = 0
            
            else:
                # Brak preferencji - prosta ocena
                trail_result['total_score'] = 50  # Domyślna ocena
            
            return trail_result
        
        # Oceniamy każdą trasę
        trail_scores = [score_trail(trail) for trail in trails]
        
        # Sortujemy według oceny (malejąco)
        trail_scores.sort(key=lambda x: x['total_score'], reverse=True)
        
        logger.debug(f"[calculate_trail_scores] Zakończono obliczanie ocen")
        return trail_scores
    
    def recommend_routes(self, 
                        start_date: date,
                        end_date: date,
                        user_preference: UserPreference = None,
                        weather_preferences: Dict[str, Any] = None,  # Dla kompatybilności wstecznej
                        trail_params: Dict[str, Any] = None,
                        limit: int = 5) -> List[Dict[str, Any]]:
        """
        Generuje rekomendacje tras na podstawie preferencji użytkownika.
        
        Args:
            start_date: Data początkowa.
            end_date: Data końcowa.
            user_preference: Obiekt UserPreference z preferencjami użytkownika (opcjonalny).
            weather_preferences: Słownik z preferencjami pogodowymi (opcjonalny, kompatybilność wsteczna).
            trail_params: Słownik z parametrami tras (opcjonalny).
            limit: Maksymalna liczba rekomendacji.
            
        Returns:
            Lista rekomendowanych tras z oceną.
        """
        logger.info("--- ROZPOCZĘCIE GENEROWANIA REKOMENDACJI ---")
        logger.debug("[recommend_routes] Rozpoczęcie generowania rekomendacji")
        
        # Używamy przekazanych preferencji lub tych zapisanych w obiekcie
        user_pref = user_preference or self.user_preference
        
        # Sprawdzenie poprawności danych wejściowych
        if not self.trail_data.trails or not self.weather_data.records:
            logger.debug("[recommend_routes] Brak danych wejściowych")
            return []
            
        # Sprawdzenie poprawności dat
        if end_date < start_date:
            logger.error("[recommend_routes] Data końcowa wcześniejsza niż początkowa")
            return []
        
        # Sprawdzenie poprawności preferencji pogodowych
        if weather_preferences and 'min_temp' in weather_preferences and 'max_temp' in weather_preferences:
            if weather_preferences['min_temp'] > weather_preferences['max_temp']:
                logger.error("[recommend_routes] Nieprawidłowe preferencje pogodowe: min_temp > max_temp")
                return []
        
        try:
            # Filtrowanie tras według podanych parametrów lub preferencji użytkownika
            if trail_params:
                logger.debug(f"[recommend_routes] Filtrowanie tras wg parametrów: {trail_params}")
                filtered_trails = self.filter_trails_by_params(**trail_params)
            elif user_pref:
                logger.debug("[recommend_routes] Filtrowanie tras wg preferencji użytkownika")
                filtered_trails = [
                    trail for trail in self.trail_data.trails
                    if trail.check_preference_match(
                        min_difficulty=user_pref.min_difficulty,
                        max_difficulty=user_pref.max_difficulty,
                        min_length=user_pref.min_length,
                        max_length=user_pref.max_length,
                        max_elevation_gain=user_pref.max_elevation_gain,
                        preferred_regions=user_pref.preferred_regions,
                        preferred_tags=user_pref.preferred_tags
                    )
                ]
            else:
                logger.debug("[recommend_routes] Brak parametrów filtrowania, używam wszystkich tras")
                filtered_trails = self.trail_data.trails
                
            if not filtered_trails:
                logger.info("[recommend_routes] Brak tras spełniających kryteria")
                return []
                
            # Obliczanie ocen dla tras
            date_range = (start_date, end_date)
            scored_trails = self.calculate_trail_scores(
                filtered_trails, 
                date_range, 
                weather_preferences, 
                user_pref
            )
            
            # Zwracamy najlepsze trasy
            recommendations = scored_trails[:limit]
            
            logger.info(f"[recommend_routes] Wygenerowano {len(recommendations)} rekomendacji")
            logger.debug(f"[recommend_routes] Rekomendacje: {[rec['trail'].name for rec in recommendations]}")
            
            return recommendations
            
        except Exception as e:
            import traceback
            logger.error(f"[recommend_routes] Generowanie rekomendacji nie powiodło się: {str(e)}")
            logger.debug(f"[recommend_routes] Szczegóły błędu: {traceback.format_exc()}")
            return []
    
    def generate_weekly_recommendation(self, 
                                     start_date: Optional[date] = None,
                                     user_preference: UserPreference = None,
                                     weather_preferences: Dict[str, Any] = None,  # Dla kompatybilności wstecznej
                                     trail_params: Dict[str, Any] = None) -> Dict[date, List[Dict[str, Any]]]:
        """
        Generuje rekomendacje tras na kolejne dni tygodnia.
        
        Args:
            start_date: Data początkowa (domyślnie dzisiaj).
            user_preference: Obiekt UserPreference z preferencjami użytkownika (opcjonalny).
            weather_preferences: Słownik z preferencjami pogodowymi (opcjonalny, kompatybilność wsteczna).
            trail_params: Słownik z parametrami tras (opcjonalny).
            
        Returns:
            Słownik z rekomendacjami dla każdego dnia (data -> lista rekomendacji).
        """
        if start_date is None:
            start_date = date.today()
        
        logger.info(f"[generate_weekly_recommendation] Generowanie rekomendacji tygodniowych od {start_date}")
        
        weekly_recommendations = {}
        
        # Generowanie rekomendacji na kolejne 7 dni
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            
            try:
                # Generowanie rekomendacji na dany dzień
                recommendations = self.recommend_routes(
                    current_date, 
                    current_date,
                    user_preference,
                    weather_preferences,
                    trail_params,
                    limit=3  # Mniej rekomendacji na każdy dzień
                )
                
                weekly_recommendations[current_date] = recommendations
            except Exception as e:
                logger.error(f"[generate_weekly_recommendation] Błąd podczas generowania rekomendacji na {current_date}: {e}")
                # W przypadku błędu dodajemy pustą listę dla tego dnia
                weekly_recommendations[current_date] = []
        
        return weekly_recommendations
    
    def find_optimal_weather_periods(self, trail: TrailRecord, 
                                   days_range: int = 30,
                                   min_comfort_index: float = 70,
                                   period_length: int = 3) -> List[Tuple[date, float]]:
        """
        Znajduje optymalne okresy pogodowe dla danej trasy.
        
        Args:
            trail: Obiekt trasy.
            days_range: Liczba dni do przodu do sprawdzenia.
            min_comfort_index: Minimalny indeks komfortu.
            period_length: Długość okresu w dniach.
            
        Returns:
            Lista krotek (data_początkowa, indeks_komfortu) dla najlepszych okresów.
        """
        logger.debug(f"[find_optimal_weather_periods] Szukanie optymalnych okresów dla trasy: {trail.name}")
        
        # Używamy regionu trasy jako identyfikatora lokalizacji
        location_id = trail.region
        
        # Znajdujemy najlepsze okresy pogodowe
        best_periods = self.weather_data.find_best_weather_periods(
            location_id, period_length, min_comfort_index
        )
        
        # Filtrujemy tylko okresy w przyszłości (w zakresie days_range)
        today = date.today()
        end_date = today + timedelta(days=days_range)
        
        future_periods = [
            (start_date, comfort)
            for start_date, comfort in best_periods
            if today <= start_date <= end_date
        ]
        
        logger.debug(f"[find_optimal_weather_periods] Znaleziono {len(future_periods)} optymalnych okresów")
        
        return future_periods
    
    def get_trail_statistics(self, trail: TrailRecord) -> Dict[str, Any]:
        """
        Oblicza statystyki dla danej trasy.
        
        Args:
            trail: Obiekt trasy.
            
        Returns:
            Słownik ze statystykami trasy.
        """
        logger.debug(f"[get_trail_statistics] Obliczanie statystyk dla trasy: {trail.name}")
        
        # Używamy regionu trasy jako identyfikatora lokalizacji
        location_id = trail.region
        
        # Pobieramy statystyki pogodowe
        weather_stats = self.weather_data.calculate_statistics(location_id)
        
        # Dodajemy informacje o trasie
        stats = {
            'name': trail.name,
            'region': trail.region,
            'length_km': trail.length_km,
            'elevation_gain': trail.elevation_gain,
            'difficulty': trail.difficulty,
            'categories': trail.get_categories_names(),
            'estimated_time': trail.estimate_completion_time_formatted(),
            'avg_temperature': weather_stats['avg_temperature'],
            'sunny_days_count': weather_stats['sunny_days_count'],
            'rainy_days_count': weather_stats['rainy_days_count'],
            'avg_comfort_index': weather_stats['avg_comfort_index']
        }
        
        # Znajdujemy optymalne okresy pogodowe
        best_periods = self.weather_data.find_best_weather_periods(
            location_id, period_length=7, min_comfort_index=70
        )
        
        # Grupujemy najlepsze okresy według miesiąca
        months_stats = {}
        for start_date, comfort in best_periods:
            month = start_date.month
            if month not in months_stats:
                months_stats[month] = {'count': 0, 'avg_comfort': 0}
            
            months_stats[month]['count'] += 1
            months_stats[month]['avg_comfort'] += comfort
        
        # Obliczamy średnie wartości
        for month, month_stats in months_stats.items():
            if month_stats['count'] > 0:
                month_stats['avg_comfort'] /= month_stats['count']
        
        # Znajdujemy najlepsze miesiące (sortujemy po liczbie dobrych okresów i indeksie komfortu)
        best_months = sorted(
            months_stats.items(), 
            key=lambda x: (x[1]['count'], x[1]['avg_comfort']),
            reverse=True
        )
        
        # Konwertujemy numery miesięcy na nazwy
        month_names = {
            1: "Styczeń", 2: "Luty", 3: "Marzec", 4: "Kwiecień", 
            5: "Maj", 6: "Czerwiec", 7: "Lipiec", 8: "Sierpień",
            9: "Wrzesień", 10: "Październik", 11: "Listopad", 12: "Grudzień"
        }
        
        stats['best_months'] = [month_names[month] for month, _ in best_months[:3]]
        
        return stats
    
    def export_recommendations_to_csv(self, recommendations: List[Dict[str, Any]], filepath: str) -> None:
        """
        Eksportuje rekomendacje tras do pliku CSV.
        
        Args:
            recommendations: Lista rekomendacji wygenerowanych przez recommend_routes().
            filepath: Ścieżka docelowa pliku CSV.
            
        Raises:
            ValueError: Gdy nie udało się zapisać danych.
        """
        logger.info(f"Eksportowanie {len(recommendations)} rekomendacji do pliku CSV: {filepath}")
        
        try:
            import csv
            with open(filepath, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
                # Nagłówki
                writer.writerow([
                    'Nazwa', 'Region', 'Długość (km)', 'Trudność', 'Przewyższenie (m)',
                    'Kategorie', 'Szacowany czas', 'Komfort pogodowy', 'Dopasowanie', 'Ocena ogólna'
                ])
                
                # Dane
                for rec in recommendations:
                    trail = rec['trail']
                    writer.writerow([
                        trail.name,
                        trail.region,
                        trail.length_km,
                        f"{trail.difficulty}/5",
                        trail.elevation_gain,
                        ', '.join(rec.get('categories', [])),
                        rec.get('estimated_time', ''),
                        rec.get('weather_comfort_index', 0),
                        rec.get('preference_match_score', 0),
                        rec.get('total_score', 0)
                    ])
            
            logger.info(f"Pomyślnie zapisano rekomendacje do pliku CSV: {filepath}")
        except Exception as e:
            error_msg = f"Błąd podczas zapisywania rekomendacji do pliku CSV: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    
    def export_recommendations_to_json(self, recommendations: List[Dict[str, Any]], filepath: str) -> None:
        """
        Eksportuje rekomendacje tras do pliku JSON.
        
        Args:
            recommendations: Lista rekomendacji wygenerowanych przez recommend_routes().
            filepath: Ścieżka docelowa pliku JSON.
            
        Raises:
            ValueError: Gdy nie udało się zapisać danych.
        """
        logger.info(f"Eksportowanie {len(recommendations)} rekomendacji do pliku JSON: {filepath}")
        
        try:
            import json
            from datetime import date
            
            # Klasa do serializacji obiektów dat
            class DateEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, date):
                        return obj.isoformat()
                    return json.JSONEncoder.default(self, obj)
            
            # Przygotowanie danych do eksportu
            export_data = {
                'recommendations': []
            }
            
            for rec in recommendations:
                trail = rec['trail']
                export_data['recommendations'].append({
                    'name': trail.name,
                    'region': trail.region,
                    'length_km': trail.length_km,
                    'difficulty': trail.difficulty,
                    'elevation_gain': trail.elevation_gain,
                    'terrain_type': trail.terrain_type,
                    'tags': trail.tags,
                    'categories': rec.get('categories', []),
                    'estimated_time': rec.get('estimated_time', ''),
                    'weather_comfort_index': rec.get('weather_comfort_index', 0),
                    'preference_match_score': rec.get('preference_match_score', 0),
                    'total_score': rec.get('total_score', 0)
                })
            
            with open(filepath, 'w', encoding='utf-8') as file:
                json.dump(export_data, file, cls=DateEncoder, indent=2, ensure_ascii=False)
            
            logger.info(f"Pomyślnie zapisano rekomendacje do pliku JSON: {filepath}")
        except Exception as e:
            error_msg = f"Błąd podczas zapisywania rekomendacji do pliku JSON: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
