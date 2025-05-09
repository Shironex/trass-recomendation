"""
Moduł zawierający główne klasy i logikę biznesową aplikacji.
"""

from .api_client import ApiClient
from .data_processor import RouteRecommender
from .trail_data import TrailData, TrailRecord
from .weather_data import WeatherData, WeatherRecord
from .user_preference import UserPreference


__all__ = [
    'ApiClient',
    'RouteRecommender',
    'TrailData',
    'WeatherData',
    'TrailRecord',
    'WeatherRecord',
    'UserPreference'
]

