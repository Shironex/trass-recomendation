"""
Pakiet zawierający strony aplikacji.
"""

from .home_page import HomePage
from .trail_page import TrailPage
from .weather_page import WeatherPage
from .recommendation_page import RecommendationPage


__all__ = [
    'HomePage',
    'TrailPage',
    'WeatherPage',
    'RecommendationPage'
]

