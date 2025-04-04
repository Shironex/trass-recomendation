"""
Moduł do komunikacji z zewnętrznymi API, umożliwiający pobieranie danych o trasach
turystycznych i danych pogodowych.
"""

import json
import requests
import os
from typing import Dict, List, Optional
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from src.utils import logger
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
            logger.info(f"Utworzono katalog pamięci podręcznej: {self.cache_dir}")
        
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
        
        # Sprawdzenie cache przed wykonaniem zapytania
        cache_key = f"{service}_{location}_{days}"
        cached_data = self.load_api_response_from_cache(service, cache_key)
        
        if cached_data:
            logger.info("Znaleziono dane w pamięci podręcznej")
            try:
                return self._parse_weather_data(service, cached_data)
            except Exception as e:
                logger.warn(f"Nie udało się przetworzyć danych z cache: {str(e)}")
        
        # Wykonanie żądania do odpowiedniego API
        if service == "openweathermap":
            data = self._get_openweathermap_forecast(location, days)
        elif service == "weatherapi":
            data = self._get_weatherapi_forecast(location, days)
        elif service == "visualcrossing":
            data = self._get_visualcrossing_forecast(location, days)
        else:
            raise ValueError(f"Brak implementacji dla serwisu: {service}")
        
        # Zapisanie odpowiedzi do cache
        if data:
            self.save_api_response_to_cache(service, cache_key, data)
        
        return self._parse_weather_data(service, data)
    
    def _parse_weather_data(self, service: str, data: Dict) -> List[WeatherRecord]:
        """
        Parsuje dane pogodowe z różnych serwisów do jednolitego formatu.
        
        Args:
            service: Nazwa serwisu API.
            data: Dane do sparsowania.
            
        Returns:
            Lista obiektów WeatherRecord.
        """
        if service == "openweathermap":
            return self._parse_openweathermap_data(data)
        elif service == "weatherapi":
            return self._parse_weatherapi_data(data)
        elif service == "visualcrossing":
            return self._parse_visualcrossing_data(data)
        else:
            raise ValueError(f"Brak implementacji parsera dla serwisu: {service}")
    
    def _get_openweathermap_forecast(self, location: str, days: int) -> Dict:
        """
        Pobiera prognozę pogody z OpenWeatherMap.
        
        Args:
            location: Nazwa lokalizacji lub współrzędne geograficzne.
            days: Liczba dni prognozy.
            
        Returns:
            Słownik z danymi pogodowymi.
            
        Raises:
            ConnectionError: Gdy nie udało się nawiązać połączenia z API.
        """
        try:
            api_key = self.api_keys["openweathermap"]
            url = f"{self.WEATHER_APIS['openweathermap']}/forecast?q={location}&appid={api_key}&units=metric"
            
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd podczas pobierania prognozy z OpenWeatherMap: {str(e)}")
            raise ConnectionError(f"Nie udało się pobrać prognozy z OpenWeatherMap: {str(e)}")
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd podczas pobierania prognozy z OpenWeatherMap: {str(e)}")
            raise ConnectionError(f"Nieoczekiwany błąd podczas pobierania prognozy z OpenWeatherMap: {str(e)}")
    
    def _get_weatherapi_forecast(self, location: str, days: int) -> Dict:
        """
        Pobiera prognozę pogody z WeatherAPI.com.
        
        Args:
            location: Nazwa lokalizacji lub współrzędne geograficzne.
            days: Liczba dni prognozy.
            
        Returns:
            Słownik z danymi pogodowymi.
            
        Raises:
            ConnectionError: Gdy nie udało się nawiązać połączenia z API.
        """
        try:
            api_key = self.api_keys["weatherapi"]
            url = f"{self.WEATHER_APIS['weatherapi']}/forecast.json?key={api_key}&q={location}&days={days}"
            
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd podczas pobierania prognozy z WeatherAPI: {str(e)}")
            raise ConnectionError(f"Nie udało się pobrać prognozy z WeatherAPI: {str(e)}")
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd podczas pobierania prognozy z WeatherAPI: {str(e)}")
            raise ConnectionError(f"Nieoczekiwany błąd podczas pobierania prognozy z WeatherAPI: {str(e)}")
    
    def _get_visualcrossing_forecast(self, location: str, days: int) -> Dict:
        """
        Pobiera prognozę pogody z Visual Crossing Weather.
        
        Args:
            location: Nazwa lokalizacji lub współrzędne geograficzne.
            days: Liczba dni prognozy.
            
        Returns:
            Słownik z danymi pogodowymi.
            
        Raises:
            ConnectionError: Gdy nie udało się nawiązać połączenia z API.
        """
        try:
            api_key = self.api_keys["visualcrossing"]
            url = f"{self.WEATHER_APIS['visualcrossing']}/timeline/{location}/{days}days?key={api_key}&unitGroup=metric"
            
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd podczas pobierania prognozy z Visual Crossing: {str(e)}")
            raise ConnectionError(f"Nie udało się pobrać prognozy z Visual Crossing: {str(e)}")
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd podczas pobierania prognozy z Visual Crossing: {str(e)}")
            raise ConnectionError(f"Nieoczekiwany błąd podczas pobierania prognozy z Visual Crossing: {str(e)}")
    
    def _parse_openweathermap_data(self, data: Dict) -> List[WeatherRecord]:
        """
        Parsuje dane z OpenWeatherMap.
        
        Args:
            data: Surowe dane z API OpenWeatherMap.
            
        Returns:
            Lista obiektów WeatherRecord.
        """
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
                            location_id=data["city"]["name"],
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
                    location_id=data["city"]["name"],
                    avg_temp=daily_data["temp_sum"] / daily_data["count"],
                    min_temp=daily_data["min_temp"],
                    max_temp=daily_data["max_temp"],
                    precipitation=daily_data["precipitation_sum"],
                    sunshine_hours=12.0 - (daily_data["cloud_sum"] / daily_data["count"]) * 0.12,
                    cloud_cover=int(daily_data["cloud_sum"] / daily_data["count"])
                )
            )
        
        logger.info(f"Sparsowano prognozę pogody dla {len(weather_records)} dni z OpenWeatherMap")
        return weather_records
    
    def _parse_weatherapi_data(self, data: Dict) -> List[WeatherRecord]:
        """Parsuje dane z WeatherAPI.com."""
        weather_records = []
        for day in data["forecast"]["forecastday"]:
            forecast_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
            
            # Obliczanie godzin słonecznych na podstawie zachmurzenia
            cloud_cover = day["day"].get("avghumidity", 50)  # Używamy wilgotności jako przybliżenia zachmurzenia
            sunshine_hours = 24 * (1 - cloud_cover / 100)  # Im większe zachmurzenie, tym mniej słońca
            
            weather_records.append(
                WeatherRecord(
                    date=forecast_date,
                    location_id=data["location"]["name"],
                    avg_temp=day["day"]["avgtemp_c"],
                    min_temp=day["day"]["mintemp_c"],
                    max_temp=day["day"]["maxtemp_c"],
                    precipitation=day["day"]["totalprecip_mm"],
                    sunshine_hours=sunshine_hours,
                    cloud_cover=int(cloud_cover)
                )
            )
        return weather_records
    
    def _parse_visualcrossing_data(self, data: Dict) -> List[WeatherRecord]:
        """Parsuje dane z Visual Crossing Weather."""
        weather_records = []
        # Implementacja parsowania danych z Visual Crossing
        return weather_records
    
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
            logger.warn(f"Nie udało się zapisać danych do pamięci podręcznej: {str(e)}")
    
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
            logger.warn(f"Nie udało się wczytać danych z pamięci podręcznej: {str(e)}")
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