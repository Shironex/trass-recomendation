"""
Testy dla modułu data_processor.py odpowiedzialnego za przetwarzanie danych
i generowanie rekomendacji tras turystycznych.
"""
from datetime import date
from unittest.mock import patch
from src.core.trail_data import TrailRecord


def test_init(route_recommender, sample_trail_data, sample_weather_data):
    """Test inicjalizacji obiektu RouteRecommender."""
    assert route_recommender.trail_data == sample_trail_data
    assert route_recommender.weather_data == sample_weather_data
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


def test_filter_trails_by_params_difficulty(route_recommender, sample_trail):
    """Test filtrowania tras według trudności."""
    filtered = route_recommender.filter_trails_by_params(difficulty=3)
    assert len(filtered) == 1
    assert filtered[0] == sample_trail

    filtered = route_recommender.filter_trails_by_params(difficulty=5)
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
        difficulty=3,
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