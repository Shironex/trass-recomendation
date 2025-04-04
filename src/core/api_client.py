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
from urllib.parse import urlencode
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
        "visualcrossing": "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services"
    }
    
    def __init__(self, api_keys: Dict[str, str] = None, cache_dir: str = None):
        """
        Inicjalizacja klienta API.
        
        Args:
            api_keys: Słownik zawierający klucze API dla różnych serwisów.
                      Format: {"visualcrossing": "klucz"}.
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
                           days: int = None,
                           start_date: str = None,
                           end_date: str = None) -> List[WeatherRecord]:
        """
        Pobiera prognozę pogody dla danej lokalizacji.
        
        Args:
            service: Nazwa serwisu API ('visualcrossing').
            location: Nazwa lokalizacji lub współrzędne geograficzne.
            days: Liczba dni prognozy (opcjonalne, używane tylko gdy nie podano zakresu dat).
            start_date: Data początkowa w formacie YYYY-MM-DD (opcjonalne).
            end_date: Data końcowa w formacie YYYY-MM-DD (opcjonalne).
            
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
        cache_key = f"{service}_{location}_{days}_{start_date}_{end_date}"
        cached_data = self.load_api_response_from_cache(service, cache_key)
        
        if cached_data:
            logger.info("Znaleziono dane w pamięci podręcznej")
            try:
                return self._parse_weather_data(service, cached_data)
            except Exception as e:
                logger.warn(f"Nie udało się przetworzyć danych z cache: {str(e)}")
        
        # Wykonanie żądania do API
        data = self._get_visualcrossing_forecast(location, days, start_date, end_date)
        
        # Zapisanie odpowiedzi do cache
        if data:
            self.save_api_response_to_cache(service, cache_key, data)
        
        return self._parse_weather_data(service, data)
    
    def _parse_weather_data(self, service: str, data: Dict) -> List[WeatherRecord]:
        """
        Parsuje dane pogodowe z serwisu do jednolitego formatu.
        
        Args:
            service: Nazwa serwisu API.
            data: Dane do sparsowania.
            
        Returns:
            Lista obiektów WeatherRecord.
        """
        return self._parse_visualcrossing_data(data)
    
    def _get_visualcrossing_forecast(self, location: str, days: int = None, start_date: str = None, end_date: str = None) -> Dict:
        """
        Pobiera prognozę pogody z Visual Crossing Weather.
        
        Args:
            location: Nazwa lokalizacji lub współrzędne geograficzne.
            days: Liczba dni prognozy (opcjonalne, używane tylko gdy nie podano zakresu dat).
            start_date: Data początkowa w formacie YYYY-MM-DD (opcjonalne).
            end_date: Data końcowa w formacie YYYY-MM-DD (opcjonalne).
            
        Returns:
            Słownik z danymi pogodowymi.
            
        Raises:
            ConnectionError: Gdy nie udało się nawiązać połączenia z API.
            ValueError: Gdy podano nieprawidłowy zakres dat.
        """
        try:
            api_key = self.api_keys["visualcrossing"]
            
            # Budowanie ścieżki URL w zależności od parametrów
            if start_date and end_date:
                # Sprawdzenie formatu dat
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                    datetime.strptime(end_date, "%Y-%m-%d")
                except ValueError as e:
                    raise ValueError("Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD") from e
                
                # Użyj zakresu dat w URL
                base_url = f"{self.WEATHER_APIS['visualcrossing']}/timeline/{location}/{start_date}/{end_date}"
            elif start_date:
                # Jeśli podano tylko datę początkową, pobierz dane dla jednego dnia
                try:
                    datetime.strptime(start_date, "%Y-%m-%d")
                except ValueError as e:
                    raise ValueError("Nieprawidłowy format daty. Użyj formatu YYYY-MM-DD") from e
                
                base_url = f"{self.WEATHER_APIS['visualcrossing']}/timeline/{location}/{start_date}"
            else:
                # Jeśli nie podano dat, użyj podstawowego URL (domyślnie 15 dni)
                base_url = f"{self.WEATHER_APIS['visualcrossing']}/timeline/{location}"
            
            # Dodanie parametrów zapytania
            params = {
                'key': api_key,
                'unitGroup': 'metric'
            }
            
            # Jeśli podano konkretną liczbę dni (bez zakresu dat), dodaj parametr
            if days is not None and not (start_date or end_date):
                if days <= 0 or days > 15:
                    raise ValueError("Liczba dni musi być z zakresu 1-15")
                params['include'] = 'days'
                
            # Kodowanie parametrów URL
            encoded_params = urlencode(params)
            url = f"{base_url}?{encoded_params}"
            
            logger.debug(f"Wysyłanie zapytania do Visual Crossing API: {url}")
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Błąd podczas pobierania prognozy z Visual Crossing: {str(e)}")
            raise ConnectionError(f"Nie udało się pobrać prognozy z Visual Crossing: {str(e)}")
        except ValueError as e:
            logger.error(f"Błąd walidacji parametrów: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Nieoczekiwany błąd podczas pobierania prognozy z Visual Crossing: {str(e)}")
            raise ConnectionError(f"Nieoczekiwany błąd podczas pobierania prognozy z Visual Crossing: {str(e)}")
    
    def _parse_visualcrossing_data(self, data: Dict) -> List[WeatherRecord]:
        """
        Parsuje dane z Visual Crossing Weather.
        
        Args:
            data: Surowe dane z API Visual Crossing.
            
        Returns:
            Lista obiektów WeatherRecord.
        """
        weather_records = []
        
        # Sprawdzenie, czy dane zawierają oczekiwane pola
        if "days" not in data:
            logger.error("Brak danych o prognozie w odpowiedzi z Visual Crossing API")
            return weather_records
        
        # Pobranie nazwy lokalizacji
        location_name = data.get("resolvedAddress", "Unknown")
        
        # Parsowanie danych dla każdego dnia
        for day in data["days"]:
            try:
                # Konwersja daty z formatu ISO
                forecast_date = datetime.strptime(day["datetime"], "%Y-%m-%d").date()
                
                # Pobranie danych pogodowych
                avg_temp = day.get("temp", 0)
                min_temp = day.get("tempmin", 0)
                max_temp = day.get("tempmax", 0)
                precipitation = day.get("precip", 0)
                
                # Obliczanie godzin słonecznych na podstawie zachmurzenia
                cloud_cover = day.get("cloudcover", 50)
                sunshine_hours = 24 * (1 - cloud_cover / 100)  # Im większe zachmurzenie, tym mniej słońca
                
                # Tworzenie rekordu pogodowego
                weather_records.append(
                    WeatherRecord(
                        date=forecast_date,
                        location_id=location_name,
                        avg_temp=avg_temp,
                        min_temp=min_temp,
                        max_temp=max_temp,
                        precipitation=precipitation,
                        sunshine_hours=sunshine_hours,
                        cloud_cover=int(cloud_cover)
                    )
                )
            except Exception as e:
                logger.error(f"Błąd podczas parsowania danych z Visual Crossing API: {str(e)}")
                continue
        
        logger.info(f"Sparsowano {len(weather_records)} rekordów pogodowych z Visual Crossing API")
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
                
            if service not in self.api_keys:
                logger.error(f"Brak klucza API dla serwisu {service}")
                return False
                
            api_key = self.api_keys[service]
            url = f"{self.WEATHER_APIS[service]}/timeline/Warsaw?key={api_key}&unitGroup=metric"
            
            response = requests.get(url, timeout=5)
            return response.status_code == 200
                
        except Exception as e:
            logger.error(f"Błąd podczas testowania API {service}: {str(e)}")
            return False 