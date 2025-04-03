"""
Moduł do komunikacji z zewnętrznymi API, umożliwiający pobieranie danych o trasach
turystycznych i danych pogodowych.
"""

import json
import requests
from typing import Dict, List, Optional
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
import os

from src.utils.logger import logger
from src.core.trail_data import TrailRecord
from src.core.weather_data import WeatherRecord

class ApiClient:
    """
    Klasa do komunikacji z zewnętrznymi API pogodowymi.
    
    Umożliwia pobieranie danych o prognozowanych danych pogodowych.
    """
    
    # Adresy do popularnych API
    WEATHER_APIS = {
        "openweathermap": "https://api.openweathermap.org/data/2.5",
        "weatherapi": "https://api.weatherapi.com/v1",
        "visualcrossing": "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services"
    }
    
    def __init__(self, api_keys: Dict[str, str] = None, cache_dir: str = None):
        """
        Inicjalizacja klienta API.
        
        Args:
            api_keys: Słownik zawierający klucze API dla różnych serwisów.
                      Format: {"openweathermap": "klucz", "weatherapi": "klucz"}.
            cache_dir: Katalog do przechowywania pamięci podręcznej pobranych danych.
        """
        self.api_keys = api_keys or {}
        self.cache_dir = cache_dir
        
        # Jeśli podano katalog cache, upewnij się, że istnieje
        if self.cache_dir:
            os.makedirs(self.cache_dir, exist_ok=True)
        
        logger.debug("Inicjalizacja klienta API")
    
    def set_api_key(self, service: str, api_key: str) -> None:
        """
        Ustawia klucz API dla konkretnego serwisu.
        
        Args:
            service: Nazwa serwisu (np. 'openweathermap').
            api_key: Klucz API.
        """
        self.api_keys[service] = api_key
        logger.debug(f"Ustawiono klucz API dla serwisu: {service}")
    
    @lru_cache(maxsize=128)
    def get_weather_forecast(self, 
                            service: str, 
                            location: str, 
                            days: int = 7) -> List[WeatherRecord]:
        """
        Pobiera prognozę pogody dla danej lokalizacji.
        
        Args:
            service: Nazwa serwisu API (np. 'openweathermap', 'weatherapi').
            location: Nazwa lokalizacji lub współrzędne geograficzne.
            days: Liczba dni prognozy (domyślnie 7).
            
        Returns:
            Lista obiektów WeatherRecord zawierających prognozę pogody.
            
        Raises:
            ValueError: Gdy nazwa serwisu jest nieprawidłowa lub brak klucza API.
            ConnectionError: Gdy nie udało się nawiązać połączenia z API.
        """
        logger.info(f"Pobieranie prognozy pogody dla lokalizacji {location} z serwisu {service}")
        
        if service not in self.WEATHER_APIS:
            raise ValueError(f"Nieobsługiwany serwis pogodowy: {service}")
        
        if service not in self.api_keys:
            raise ValueError(f"Brak klucza API dla serwisu: {service}")
        
        # Wykonanie żądania do odpowiedniego API
        if service == "openweathermap":
            return self._get_openweathermap_forecast(location, days)
        elif service == "weatherapi":
            return self._get_weatherapi_forecast(location, days)
        elif service == "visualcrossing":
            return self._get_visualcrossing_forecast(location, days)
        else:
            raise ValueError(f"Brak implementacji dla serwisu: {service}")
    
    def _get_openweathermap_forecast(self, location: str, days: int) -> List[WeatherRecord]:
        """
        Pobiera prognozę pogody z OpenWeatherMap API.
        
        Args:
            location: Nazwa lokalizacji lub współrzędne geograficzne.
            days: Liczba dni prognozy.
            
        Returns:
            Lista obiektów WeatherRecord.
        """
        try:
            api_key = self.api_keys["openweathermap"]
            
            # Sprawdzenie, czy location to współrzędne geograficzne
            if "," in location:
                lat, lon = location.split(",")
                # Używamy standardowego endpointu prognozy 5-dniowej zamiast godzinowej wersji Pro
                url = f"{self.WEATHER_APIS['openweathermap']}/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
                logger.debug(f"Wysyłanie zapytania do OpenWeatherMap z współrzędnymi: {url}")
            else:
                # Używamy standardowego endpointu prognozy 5-dniowej zamiast godzinowej wersji Pro
                url = f"{self.WEATHER_APIS['openweathermap']}/forecast?q={location}&appid={api_key}&units=metric"
                logger.debug(f"Wysyłanie zapytania do OpenWeatherMap z lokalizacją: {url}")
            
            response = requests.get(url)
            
            # Wyrzuć wyjątek, jeśli wystąpił błąd HTTP
            response.raise_for_status()
            data = response.json()
            
            # Konwersja danych do formatu WeatherRecord
            weather_records = []
            current_date = None
            daily_data = {}
            
            # Posortuj dane według daty (mogą być nieuporządkowane)
            sorted_forecasts = sorted(data["list"], key=lambda x: x["dt"])
            
            for item in sorted_forecasts:
                forecast_date = datetime.fromtimestamp(item["dt"]).date()
                
                if current_date != forecast_date:
                    if current_date and daily_data["count"] > 0:
                        # Zapisz poprzedni dzień
                        weather_records.append(
                            WeatherRecord(
                                date=current_date,
                                location_id=location,
                                avg_temp=daily_data["temp_sum"] / daily_data["count"],
                                min_temp=daily_data["min_temp"],
                                max_temp=daily_data["max_temp"],
                                precipitation=daily_data["precipitation_sum"],
                                sunshine_hours=12.0 - (daily_data["cloud_sum"] / daily_data["count"]) * 0.12,
                                cloud_cover=int(daily_data["cloud_sum"] / daily_data["count"])
                            )
                        )
                    
                    # Zainicjuj nowy dzień
                    current_date = forecast_date
                    daily_data = {
                        "temp_sum": 0,
                        "min_temp": float('inf'),
                        "max_temp": float('-inf'),
                        "precipitation_sum": 0,
                        "cloud_sum": 0,
                        "count": 0
                    }
                
                # Aktualizacja danych dziennych
                temp = item["main"]["temp"]
                daily_data["temp_sum"] += temp
                daily_data["min_temp"] = min(daily_data["min_temp"], item["main"]["temp_min"])
                daily_data["max_temp"] = max(daily_data["max_temp"], item["main"]["temp_max"])
                daily_data["precipitation_sum"] += item.get("rain", {}).get("3h", 0)
                daily_data["cloud_sum"] += item["clouds"]["all"]
                daily_data["count"] += 1
            
            # Dodaj ostatni dzień
            if current_date and daily_data["count"] > 0:
                weather_records.append(
                    WeatherRecord(
                        date=current_date,
                        location_id=location,
                        avg_temp=daily_data["temp_sum"] / daily_data["count"],
                        min_temp=daily_data["min_temp"],
                        max_temp=daily_data["max_temp"],
                        precipitation=daily_data["precipitation_sum"],
                        sunshine_hours=12.0 - (daily_data["cloud_sum"] / daily_data["count"]) * 0.12,
                        cloud_cover=int(daily_data["cloud_sum"] / daily_data["count"])
                    )
                )
            
            logger.info(f"Pobrano prognozę pogody dla {len(weather_records)} dni z OpenWeatherMap")
            # Upewnij się, że zwracamy tylko tyle dni, ile zostało żądane (ale nie więcej niż mamy)
            return weather_records[:min(days, len(weather_records))]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd podczas pobierania prognozy z OpenWeatherMap: {str(e)}")
            raise ConnectionError(f"Nie udało się pobrać prognozy z OpenWeatherMap: {str(e)}")
    
    def _get_weatherapi_forecast(self, location: str, days: int) -> List[WeatherRecord]:
        """
        Pobiera prognozę pogody z WeatherAPI.com.
        
        Args:
            location: Nazwa lokalizacji lub współrzędne geograficzne.
            days: Liczba dni prognozy.
            
        Returns:
            Lista obiektów WeatherRecord.
        """
        try:
            api_key = self.api_keys["weatherapi"]
            url = f"{self.WEATHER_APIS['weatherapi']}/forecast.json?key={api_key}&q={location}&days={days}"
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            weather_records = []
            
            for day in data["forecast"]["forecastday"]:
                forecast_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
                weather_records.append(
                    WeatherRecord(
                        date=forecast_date,
                        location_id=location,
                        avg_temp=day["day"]["avgtemp_c"],
                        min_temp=day["day"]["mintemp_c"],
                        max_temp=day["day"]["maxtemp_c"],
                        precipitation=day["day"]["totalprecip_mm"],
                        sunshine_hours=24 - (day["day"]["daily_will_it_rain"] * 24 * day["day"]["daily_chance_of_rain"] / 100),
                        cloud_cover=int(sum(hour["cloud"] for hour in day["hour"]) / 24)
                    )
                )
            
            logger.info(f"Pobrano prognozę pogody dla {len(weather_records)} dni")
            return weather_records
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd podczas pobierania prognozy z WeatherAPI: {str(e)}")
            raise ConnectionError(f"Nie udało się pobrać prognozy z WeatherAPI: {str(e)}")
    
    def _get_visualcrossing_forecast(self, location: str, days: int) -> List[WeatherRecord]:
        """
        Pobiera prognozę pogody z Visual Crossing Weather API.
        
        Args:
            location: Nazwa lokalizacji lub współrzędne geograficzne.
            days: Liczba dni prognozy.
            
        Returns:
            Lista obiektów WeatherRecord.
        """
        try:
            api_key = self.api_keys["visualcrossing"]
            url = f"{self.WEATHER_APIS['visualcrossing']}/timeline/{location}/next{days}days?unitGroup=metric&key={api_key}"
            
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            
            weather_records = []
            
            for day in data["days"]:
                forecast_date = datetime.strptime(day["datetime"], "%Y-%m-%d").date()
                weather_records.append(
                    WeatherRecord(
                        date=forecast_date,
                        location_id=location,
                        avg_temp=day["temp"],
                        min_temp=day["tempmin"],
                        max_temp=day["tempmax"],
                        precipitation=day["precip"],
                        sunshine_hours=day.get("sunhours", 12.0 - day["cloudcover"] * 0.12),
                        cloud_cover=int(day["cloudcover"])
                    )
                )
            
            logger.info(f"Pobrano prognozę pogody dla {len(weather_records)} dni")
            return weather_records
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd podczas pobierania prognozy z Visual Crossing: {str(e)}")
            raise ConnectionError(f"Nie udało się pobrać prognozy z Visual Crossing: {str(e)}")
    
    def _generate_example_trails(self, region: Optional[str], difficulty: Optional[int]) -> List[TrailRecord]:
        """
        Generuje przykładowe dane o trasach.
        
        Args:
            region: Opcjonalny region do filtrowania tras.
            difficulty: Opcjonalny poziom trudności do filtrowania tras.
            
        Returns:
            Lista wygenerowanych obiektów TrailRecord.
        """
        region = region or "Polska"
        logger.info(f"Generowanie przykładowych tras dla regionu {region}")
        
        trails = []
        trail_types = ["górski", "leśny", "nizinny", "miejski", "mieszany"]
        
        # Lista przykładowych nazw tras
        trail_names = [
            f"Szlak {region} Północny",
            f"Szlak {region} Południowy",
            f"Trasa widokowa {region}",
            f"Ścieżka przyrodnicza {region}",
            f"Główny szlak {region}",
            f"Szlak wokół {region}",
            f"Mała pętla {region}",
            f"Duża pętla {region}",
            f"Trasa historyczna {region}",
            f"Szlak wodny {region}"
        ]
        
        # Wygeneruj 5-10 przykładowych tras
        num_trails = min(len(trail_names), 10)
        
        for i in range(num_trails):
            trail_difficulty = difficulty if difficulty else (i % 5) + 1
            
            trails.append(
                TrailRecord(
                    id=f"EXAMPLE{i+1}",
                    name=trail_names[i] if i < len(trail_names) else f"Przykładowa trasa {i+1} w {region}",
                    region=region,
                    start_lat=50.0 + (i*0.1),
                    start_lon=19.0 + (i*0.1),
                    end_lat=50.0 + (i*0.15),
                    end_lon=19.0 + (i*0.15),
                    length_km=5.0 + (i * 2.5),
                    elevation_gain=50.0 + (i * 50.0),
                    difficulty=trail_difficulty,
                    terrain_type=trail_types[i % len(trail_types)],
                    tags=["przykładowy", "wygenerowany"]
                )
            )
        
        logger.info(f"Wygenerowano {len(trails)} przykładowych tras")
        return trails

    def save_api_response_to_cache(self, service: str, query: str, data: Dict) -> None:
        """
        Zapisuje odpowiedź API do pamięci podręcznej.
        
        Args:
            service: Nazwa serwisu API.
            query: Zapytanie identyfikujące dane.
            data: Dane do zapisania.
        """
        if not self.cache_dir:
            return
        
        cache_path = Path(self.cache_dir) / f"{service}_{query.replace('/', '_')}.json"
        
        try:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Zapisano dane do pamięci podręcznej: {cache_path}")
        except Exception as e:
            logger.warning(f"Nie udało się zapisać danych do pamięci podręcznej: {str(e)}")
    
    def load_api_response_from_cache(self, service: str, query: str) -> Optional[Dict]:
        """
        Wczytuje odpowiedź API z pamięci podręcznej.
        
        Args:
            service: Nazwa serwisu API.
            query: Zapytanie identyfikujące dane.
            
        Returns:
            Dane z pamięci podręcznej lub None, jeśli nie znaleziono.
        """
        if not self.cache_dir:
            return None
        
        cache_path = Path(self.cache_dir) / f"{service}_{query.replace('/', '_')}.json"
        
        if not cache_path.exists():
            return None
        
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.debug(f"Wczytano dane z pamięci podręcznej: {cache_path}")
            return data
        except Exception as e:
            logger.warning(f"Nie udało się wczytać danych z pamięci podręcznej: {str(e)}")
            return None
    
    def test_weather_api(self, service: str) -> bool:
        """
        Testuje połączenie z API pogodowym.
        
        Args:
            service: Nazwa serwisu API.
            
        Returns:
            True jeśli połączenie działa, False w przeciwnym wypadku.
        """
        try:
            if service not in self.WEATHER_APIS:
                logger.error(f"Nieznany serwis API: {service}")
                return False
                
            if service not in self.api_keys and service != "openweathermap":
                logger.error(f"Brak klucza API dla serwisu {service}")
                return False
                
            # Proste sprawdzenie dostępności API
            if service == "openweathermap":
                # Specjalne sprawdzenie dla OpenWeatherMap
                import requests
                url = f"{self.WEATHER_APIS[service]}/weather?q=Warsaw&appid={self.api_keys.get(service, '')}"
                response = requests.get(url, timeout=5)
                return response.status_code == 200
            else:
                # Dla innych serwisów
                records = self.get_weather_forecast(service, "Warsaw", 1)
                return len(records) > 0
                
        except Exception as e:
            logger.error(f"Błąd podczas testowania API {service}: {str(e)}")
            return False 