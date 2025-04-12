"""
Testy dla modułu data_processor.py odpowiedzialnego za przetwarzanie danych
i generowanie rekomendacji tras turystycznych.
"""
from datetime import date, timedelta
from unittest.mock import patch
from src.core.trail_data import TrailRecord, TrailData
from src.core.weather_data import WeatherRecord, WeatherData
from src.core.data_processor import RouteRecommender
import pytest


@pytest.fixture
def sample_trail():
    """Przykładowa trasa do testów."""
    return TrailRecord(
        id="test1",
        name="Test Trail",
        region="Test Region",
        start_lat=50.0,
        start_lon=20.0,
        end_lat=50.1,
        end_lon=20.1,
        length_km=10.0,
        elevation_gain=500,
        difficulty=3,
        terrain_type="mountain",
        tags=["test"]
    )

@pytest.fixture
def sample_weather_record():
    """Przykładowy rekord pogodowy do testów."""
    return WeatherRecord(
        date=date.today(),
        location_id="Test Region",
        avg_temp=20.0,
        min_temp=15.0,
        max_temp=25.0,
        precipitation=2.0,
        sunshine_hours=6.0,
        cloud_cover=50
    )

@pytest.fixture
def route_recommender(sample_trail, sample_weather_record):
    """Fixture tworzący obiekt RouteRecommender z przykładowymi danymi."""
    trail_data = TrailData()
    trail_data.trails = [sample_trail]
    
    weather_data = WeatherData()
    weather_data.records = [sample_weather_record]
    
    return RouteRecommender(trail_data, weather_data)


def test_init(route_recommender, sample_trail_data, sample_weather_data):
    """Test inicjalizacji obiektu RouteRecommender."""
    assert len(route_recommender.trail_data.trails) == len(sample_trail_data.trails)
    assert len(route_recommender.weather_data.records) == len(sample_weather_data.records)
    assert route_recommender.WEATHER_SCORE_WEIGHTS == {
        'temperature': 40,
        'precipitation': 30,
        'sunshine': 30
    }


def test_filter_trails_by_params_min_length(route_recommender, sample_trail):
    """Test filtrowania tras według minimalnej długości."""
    filtered = route_recommender.filter_trails_by_params(min_length=5.0)
    assert len(filtered) == 1
    assert filtered[0] == sample_trail

    filtered = route_recommender.filter_trails_by_params(min_length=15.0)
    assert len(filtered) == 0


def test_filter_trails_by_params_max_length(route_recommender, sample_trail):
    """Test filtrowania tras według maksymalnej długości."""
    filtered = route_recommender.filter_trails_by_params(max_length=15.0)
    assert len(filtered) == 1
    assert filtered[0] == sample_trail

    filtered = route_recommender.filter_trails_by_params(max_length=5.0)
    assert len(filtered) == 0


def test_filter_trails_by_params_difficulty_exact(route_recommender, sample_trail):
    """Test filtrowania tras według dokładnej trudności."""
    filtered = route_recommender.filter_trails_by_params(difficulty=3)
    assert len(filtered) == 1
    assert filtered[0] == sample_trail

    filtered = route_recommender.filter_trails_by_params(difficulty=5)
    assert len(filtered) == 0


def test_filter_trails_by_params_difficulty_range(route_recommender, sample_trail):
    """Test filtrowania tras według zakresu trudności."""
    # Test zakresu zawierającego trudność trasy
    filtered = route_recommender.filter_trails_by_params(min_difficulty=2, max_difficulty=4)
    assert len(filtered) == 1
    assert filtered[0] == sample_trail

    # Test zakresu poniżej trudności trasy
    filtered = route_recommender.filter_trails_by_params(min_difficulty=1, max_difficulty=2)
    assert len(filtered) == 0

    # Test zakresu powyżej trudności trasy
    filtered = route_recommender.filter_trails_by_params(min_difficulty=4, max_difficulty=5)
    assert len(filtered) == 0


def test_filter_trails_by_params_region(route_recommender, sample_trail):
    """Test filtrowania tras według regionu."""
    filtered = route_recommender.filter_trails_by_params(region="Test Region")
    assert len(filtered) == 1
    assert filtered[0] == sample_trail

    filtered = route_recommender.filter_trails_by_params(region="Other Region")
    assert len(filtered) == 0


def test_filter_trails_by_params_multiple(route_recommender, sample_trail):
    """Test filtrowania tras według wielu parametrów."""
    filtered = route_recommender.filter_trails_by_params(
        min_length=5.0,
        max_length=15.0,
        min_difficulty=3,
        max_difficulty=3,
        region="Test Region"
    )
    assert len(filtered) == 1
    assert filtered[0] == sample_trail


def test_calculate_weather_score(route_recommender, sample_weather_record):
    """Test obliczania oceny pogody."""
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.return_value = {
            'avg_temperature': 20.0,
            'total_precipitation': 0.0,
            'sunny_days_count': 1
        }
        
        score = route_recommender._calculate_weather_score(
            "Test Region",
            (date(2023, 7, 15), date(2023, 7, 15))
        )
        assert score > 0
        assert score <= 100


def test_calculate_weather_score_error(route_recommender):
    """Test obsługi błędów przy obliczaniu oceny pogody."""
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.side_effect = Exception("Test error")
        
        score = route_recommender._calculate_weather_score(
            "Test Region",
            (date(2023, 7, 15), date(2023, 7, 15))
        )
        assert score == 0.0


def test_calculate_weather_score_sunshine_range(route_recommender):
    """Test obliczania oceny pogody z uwzględnieniem zakresu nasłonecznienia."""
    # Test dla wartości w zakresie
    score = route_recommender._calculate_weather_score(
        "Test Region",
        (date.today(), date.today()),
        min_sunshine_hours=4.0,
        max_sunshine_hours=8.0
    )
    assert score > 0  # Wartość nasłonecznienia (6.0) jest w zakresie
    assert score <= 100  # Maksymalna możliwa ocena

    # Test dla wartości poza zakresem
    score = route_recommender._calculate_weather_score(
        "Test Region",
        (date.today(), date.today()),
        min_sunshine_hours=7.0,
        max_sunshine_hours=10.0,
        # Ustawiamy wszystkie wagi na 0 oprócz nasłonecznienia
        temperature_weight=0,
        precipitation_weight=0,
        sunshine_weight=30
    )
    # Wartość nasłonecznienia (6.0) jest poza zakresem (7.0-10.0),
    # więc ocena powinna być mniejsza niż maksymalna waga dla nasłonecznienia
    assert score < route_recommender.WEATHER_SCORE_WEIGHTS['sunshine']


def test_recommend_routes(route_recommender, sample_trail, sample_weather_record):
    """Test generowania rekomendacji tras."""
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.return_value = {
            'avg_temperature': 20.0,
            'total_precipitation': 0.0,
            'sunny_days_count': 1
        }
        
        recommendations = route_recommender.recommend_routes(
            weather_preferences={
                'min_temp': 15.0,
                'max_temp': 25.0,
                'max_precipitation': 5.0,
                'min_sunshine_hours': 4.0
            },
            trail_params={
                'min_length': 5.0,
                'max_length': 15.0,
                'difficulty': 3,
                'region': 'Test Region'
            },
            start_date=date(2023, 7, 15),
            end_date=date(2023, 7, 15)
        )
        
        assert len(recommendations) == 1
        assert recommendations[0]['id'] == sample_trail.id
        assert recommendations[0]['name'] == sample_trail.name
        assert 'weather_score' in recommendations[0]
        assert 'total_score' in recommendations[0]


def test_recommend_routes_no_data(route_recommender):
    """Test generowania rekomendacji przy braku danych."""
    route_recommender.trail_data.trails = []
    route_recommender.weather_data.records = []
    
    recommendations = route_recommender.recommend_routes(
        weather_preferences={},
        trail_params={},
        start_date=date(2023, 7, 15),
        end_date=date(2023, 7, 15)
    )
    
    assert len(recommendations) == 0


def test_recommend_routes_no_matches(route_recommender):
    """Test generowania rekomendacji gdy nie ma pasujących tras."""
    recommendations = route_recommender.recommend_routes(
        weather_preferences={},
        trail_params={'region': 'Non-existent Region'},
        start_date=date(2023, 7, 15),
        end_date=date(2023, 7, 15)
    )
    
    assert len(recommendations) == 0


def test_recommend_routes_limit(route_recommender, sample_trail, sample_weather_record):
    """Test ograniczenia liczby rekomendacji."""
    # Dodajemy więcej tras do testów
    route_recommender.trail_data.trails = [
        TrailRecord(
            id=str(i),
            name=f"Trail {i}",
            region="Test Region",
            start_lat=50.0,
            start_lon=20.0,
            end_lat=50.1,
            end_lon=20.1,
            length_km=10.0,
            elevation_gain=500,
            difficulty=3,
            terrain_type="mountain",
            tags=["scenic", "challenging"]
        ) for i in range(10)
    ]
    
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.return_value = {
            'avg_temperature': 20.0,
            'total_precipitation': 0.0,
            'sunny_days_count': 1
        }
        
        recommendations = route_recommender.recommend_routes(
            weather_preferences={},
            trail_params={},
            start_date=date(2023, 7, 15),
            end_date=date(2023, 7, 15),
            limit=3
        )
        
        assert len(recommendations) == 3


def test_calculate_weather_score_invalid_dates(route_recommender):
    """Test obsługi błędów przy nieprawidłowych datach w obliczaniu oceny pogody."""
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.side_effect = Exception("Invalid date range")
        
        score = route_recommender._calculate_weather_score(
            "Test Region",
            (date(2023, 7, 15), date(2023, 7, 10))  # Data końcowa wcześniejsza niż początkowa
        )
        assert score == 0.0


def test_recommend_routes_invalid_dates(route_recommender):
    """Test obsługi błędów przy nieprawidłowych datach w rekomendacji tras."""
    with patch.object(route_recommender, '_calculate_weather_score') as mock_score:
        mock_score.side_effect = Exception("Invalid date range")
        
        recommendations = route_recommender.recommend_routes(
            weather_preferences={},
            trail_params={},
            start_date=date(2023, 7, 15),
            end_date=date(2023, 7, 10)  # Data końcowa wcześniejsza niż początkowa
        )
        assert len(recommendations) == 0


def test_recommend_routes_invalid_preferences(route_recommender):
    """Test obsługi błędów przy nieprawidłowych preferencjach pogodowych."""
    with patch.object(route_recommender, '_calculate_weather_score') as mock_score:
        mock_score.side_effect = Exception("Invalid preferences")
        
        recommendations = route_recommender.recommend_routes(
            weather_preferences={
                'min_temp': 25.0,
                'max_temp': 15.0  # Maksymalna temperatura niższa niż minimalna
            },
            trail_params={},
            start_date=date(2023, 7, 15),
            end_date=date(2023, 7, 15)
        )
        assert len(recommendations) == 0


def test_generate_weekly_recommendation_invalid_dates(route_recommender):
    """Test obsługi błędów przy nieprawidłowych datach w generowaniu rekomendacji tygodniowej."""
    with patch.object(route_recommender, 'recommend_routes') as mock_recommend:
        mock_recommend.return_value = []  # Symulujemy brak rekomendacji zamiast rzucania wyjątku
        
        recommendations = route_recommender.generate_weekly_recommendation(
            weather_preferences={},
            trail_params={},
            start_date=date(2023, 7, 15)
        )
        assert len(recommendations) == 7  # Powinniśmy mieć 7 dni
        assert all(len(recs) == 0 for recs in recommendations.values())  # Każdy dzień powinien mieć pustą listę


def test_generate_weekly_recommendation_invalid_preferences(route_recommender):
    """Test obsługi błędów przy nieprawidłowych preferencjach w generowaniu rekomendacji tygodniowej."""
    with patch.object(route_recommender, 'recommend_routes') as mock_recommend:
        mock_recommend.return_value = []  # Symulujemy brak rekomendacji zamiast rzucania wyjątku
        
        recommendations = route_recommender.generate_weekly_recommendation(
            weather_preferences={
                'min_temp': 25.0,
                'max_temp': 15.0  # Maksymalna temperatura niższa niż minimalna
            },
            trail_params={},
            start_date=date(2023, 7, 15)
        )
        assert len(recommendations) == 7  # Powinniśmy mieć 7 dni
        assert all(len(recs) == 0 for recs in recommendations.values())  # Każdy dzień powinien mieć pustą listę


def test_calculate_statistics_invalid_data(route_recommender):
    """Test obsługi błędów przy nieprawidłowych danych statystycznych."""
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.return_value = None  # Symulujemy brak danych
        
        score = route_recommender._calculate_weather_score(
            "Test Region",
            (date(2023, 7, 15), date(2023, 7, 15))
        )
        assert score == 0.0


def test_calculate_statistics_missing_fields(route_recommender):
    """Test obsługi błędów przy brakujących polach w danych statystycznych."""
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.return_value = {
            'avg_temperature': 20.0
            # Brak pozostałych wymaganych pól
        }
        
        score = route_recommender._calculate_weather_score(
            "Test Region",
            (date(2023, 7, 15), date(2023, 7, 15))
        )
        assert score == 0.0


def test_calculate_statistics_invalid_values(route_recommender):
    """Test obsługi błędów przy nieprawidłowych wartościach w danych statystycznych."""
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.return_value = {
            'avg_temperature': 'invalid',
            'total_precipitation': -1.0,
            'sunny_days_count': 'invalid'
        }
        
        score = route_recommender._calculate_weather_score(
            "Test Region",
            (date(2023, 7, 15), date(2023, 7, 15))
        )
        assert score == 0.0


def test_calculate_weather_score_missing_stats(route_recommender):
    """Test obliczania oceny pogody przy brakujących statystykach."""
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.return_value = {}  # Puste statystyki
        
        score = route_recommender._calculate_weather_score(
            "Test Region",
            (date(2023, 7, 15), date(2023, 7, 15))
        )
        assert score == 0.0


def test_recommend_routes_error_preparing_results(route_recommender, sample_trail):
    """Test obsługi błędów przy przygotowywaniu wyników rekomendacji."""
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.return_value = {
            'avg_temperature': 20.0,
            'total_precipitation': 0.0,
            'sunny_days_count': 1
        }
        
        # Modyfikujemy obiekt trasy, aby wywołać błąd przy dostępie do atrybutów
        broken_trail = sample_trail
        delattr(broken_trail, 'terrain_type')  # Usuwamy atrybut, który jest używany w wynikach
        route_recommender.trail_data.trails = [broken_trail]
        
        recommendations = route_recommender.recommend_routes(
            weather_preferences={},
            trail_params={},
            start_date=date(2023, 7, 15),
            end_date=date(2023, 7, 15)
        )
        assert len(recommendations) == 0


def test_generate_weekly_recommendation_error_handling(route_recommender):
    """Test obsługi błędów w generowaniu rekomendacji tygodniowych."""
    with patch.object(route_recommender, 'recommend_routes') as mock_recommend:
        # Symulujemy błąd dla niektórych dni
        def side_effect(*args, **kwargs):
            if kwargs.get('start_date') and kwargs.get('end_date'):
                if kwargs['start_date'].day % 2 == 0:
                    return []  # Dla parzystych dni zwracamy pustą listę
                return [{'id': 'test', 'name': 'Test Trail'}]  # Dla nieparzystych zwracamy przykładową trasę
            return []
        
        mock_recommend.side_effect = side_effect
        
        recommendations = route_recommender.generate_weekly_recommendation(
            weather_preferences={},
            trail_params={},
            start_date=date(2023, 7, 15)
        )
        
        assert len(recommendations) == 7  # Powinniśmy mieć wpisy dla wszystkich dni
        # Sprawdzamy, czy mamy odpowiednie rekomendacje dla każdego dnia
        for day, recs in recommendations.items():
            assert isinstance(recs, list)
            if day.day % 2 == 0:
                assert len(recs) == 0  # Parzyste dni powinny mieć puste listy
            else:
                assert len(recs) == 1  # Nieparzyste dni powinny mieć jedną rekomendację


def test_calculate_weather_score_invalid_preferences(route_recommender):
    """Test obliczania oceny pogody przy nieprawidłowych preferencjach pogodowych."""
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.return_value = {
            'avg_temperature': 20.0,
            'total_precipitation': 0.0,
            'sunny_days_count': 1
        }
        
        # Test z nieprawidłowymi wartościami preferencji
        score = route_recommender._calculate_weather_score(
            "Test Region",
            (date(2023, 7, 15), date(2023, 7, 15)),
            min_temp='invalid',  # Nieprawidłowy typ
            max_temp=25.0,
            max_precipitation=5.0,
            min_sunshine_hours=4.0
        )
        assert score == 0.0  # Powinniśmy otrzymać 0 przy nieprawidłowych preferencjach 

def test_calculate_weather_score_error_in_calculation(route_recommender):
    """Test obsługi błędów podczas obliczeń w _calculate_weather_score."""
    with patch.object(route_recommender.weather_data, 'calculate_statistics') as mock_stats:
        mock_stats.return_value = {
            'avg_temperature': 20.0,
            'total_precipitation': 0.0,
            'sunny_days_count': 1,
            'avg_sunshine_hours': None  # Nieprawidłowa wartość, która spowoduje błąd w obliczeniach
        }
        
        score = route_recommender._calculate_weather_score(
            "Test Region",
            (date(2023, 7, 15), date(2023, 7, 15)),
            min_temp=15.0,
            max_temp=25.0,
            max_precipitation=5.0,
            min_sunshine_hours=4.0,
            max_sunshine_hours=8.0
        )
        assert score == 0.0  # Powinniśmy otrzymać 0 przy błędzie w obliczeniach 