import unittest
import os
import json
import csv
import tempfile
import time
import pytest
from src.core.trail_data import TrailData, TrailRecord


@pytest.fixture
def sample_trails():
    """Fixture dostarczająca przykładowe trasy do testów."""
    return [
        TrailRecord(
            id="T001",
            name="Dolina Kościeliska",
            region="TATRY",
            start_lat=49.273,
            start_lon=19.872,
            end_lat=49.258,
            end_lon=19.889,
            length_km=7.8,
            elevation_gain=320.0,
            difficulty=2,
            terrain_type="szlak pieszy",
            tags=["dolina", "łatwa", "rodzinna"]
        ),
        TrailRecord(
            id="T002",
            name="Giewont",
            region="TATRY",
            start_lat=49.273,
            start_lon=19.967,
            end_lat=49.251,
            end_lon=19.932,
            length_km=11.2,
            elevation_gain=935.0,
            difficulty=4,
            terrain_type="szlak górski",
            tags=["szczyt", "trudna", "widoki"]
        ),
        TrailRecord(
            id="B001",
            name="Klimczok",
            region="BESKIDY",
            start_lat=49.768,
            start_lon=19.013,
            end_lat=49.764,
            end_lon=19.036,
            length_km=5.2,
            elevation_gain=450.0,
            difficulty=3,
            terrain_type="szlak górski",
            tags=["szczyt", "średnia", "widoki"]
        ),
    ]


@pytest.fixture
def sample_csv_file(tmp_path, sample_trails):
    """Fixture tworząca tymczasowy plik CSV z przykładowymi danymi tras."""
    csv_file = tmp_path / "test_trails.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=[
            'id', 'name', 'region', 'start_lat', 'start_lon', 'end_lat', 'end_lon',
            'length_km', 'elevation_gain', 'difficulty', 'terrain_type', 'tags'
        ])
        writer.writeheader()
        for trail in sample_trails:
            writer.writerow({
                'id': trail.id,
                'name': trail.name,
                'region': trail.region,
                'start_lat': trail.start_lat,
                'start_lon': trail.start_lon,
                'end_lat': trail.end_lat,
                'end_lon': trail.end_lon,
                'length_km': trail.length_km,
                'elevation_gain': trail.elevation_gain,
                'difficulty': trail.difficulty,
                'terrain_type': trail.terrain_type,
                'tags': ','.join(trail.tags)
            })
    return csv_file


@pytest.fixture
def sample_json_file(tmp_path, sample_trails):
    """Fixture tworząca tymczasowy plik JSON z przykładowymi danymi tras."""
    json_file = tmp_path / "test_trails.json"
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump({
            'trail_records': [
                {
                    'id': trail.id,
                    'name': trail.name,
                    'region': trail.region,
                    'start_lat': trail.start_lat,
                    'start_lon': trail.start_lon,
                    'end_lat': trail.end_lat,
                    'end_lon': trail.end_lon,
                    'length_km': trail.length_km,
                    'elevation_gain': trail.elevation_gain,
                    'difficulty': trail.difficulty,
                    'terrain_type': trail.terrain_type,
                    'tags': trail.tags
                }
                for trail in sample_trails
            ]
        }, file, indent=2)
    return json_file


@pytest.fixture
def trail_data():
    """Fixture dostarczająca instancję klasy TrailData."""
    return TrailData()


class TestTrailData:
    """Testy klasy TrailData z modułu core."""

    def test_load_from_csv(self, trail_data, sample_csv_file, sample_trails):
        """Test wczytywania danych z pliku CSV."""
        trail_data.load_from_csv(sample_csv_file)
        
        # Sprawdzenie liczby wczytanych tras
        assert len(trail_data.trails) == 3
        
        # Sprawdzenie poprawności wczytanych danych
        trail = trail_data.trails[0]
        assert trail.id == "T001"
        assert trail.name == "Dolina Kościeliska"
        assert trail.region == "TATRY"
        assert trail.length_km == 7.8
        assert trail.elevation_gain == 320.0
        assert trail.difficulty == 2
        assert trail.terrain_type == "szlak pieszy"
        assert trail.tags == ["dolina", "łatwa", "rodzinna"]
    
    def test_load_from_json(self, trail_data, sample_json_file, sample_trails):
        """Test wczytywania danych z pliku JSON."""
        trail_data.load_from_json(sample_json_file)
        
        # Sprawdzenie liczby wczytanych tras
        assert len(trail_data.trails) == 3
        
        # Sprawdzenie poprawności wczytanych danych
        trail = trail_data.trails[0]
        assert trail.id == "T001"
        assert trail.name == "Dolina Kościeliska"
        assert trail.region == "TATRY"
        assert trail.length_km == 7.8
        assert trail.difficulty == 2
    
    def test_filter_by_length(self, trail_data, sample_trails):
        """Test filtrowania tras według długości."""
        # Ustawienie danych testowych
        trail_data.trails = sample_trails.copy()
        trail_data.filtered_trails = sample_trails.copy()
        
        # Filtrowanie
        filtered = trail_data.filter_by_length(min_length=6.0, max_length=10.0)
        
        # Sprawdzenie liczby przefiltrowanych tras
        assert len(filtered) == 1
        assert len(trail_data.filtered_trails) == 1
        
        # Sprawdzenie czy wszystkie trasy są w odpowiednim zakresie długości
        for trail in filtered:
            assert 6.0 <= trail.length_km <= 10.0
    
    def test_filter_by_difficulty(self, trail_data, sample_trails):
        """Test filtrowania tras według poziomu trudności."""
        # Ustawienie danych testowych
        trail_data.trails = sample_trails.copy()
        trail_data.filtered_trails = sample_trails.copy()
        
        # Filtrowanie
        filtered = trail_data.filter_by_difficulty(3)
        
        # Sprawdzenie liczby przefiltrowanych tras
        assert len(filtered) == 1
        assert len(trail_data.filtered_trails) == 1
        
        # Sprawdzenie czy wszystkie trasy mają właściwy poziom trudności
        for trail in filtered:
            assert trail.difficulty == 3
    
    def test_filter_by_region(self, trail_data, sample_trails):
        """Test filtrowania tras według regionu."""
        # Ustawienie danych testowych
        trail_data.trails = sample_trails.copy()
        trail_data.filtered_trails = sample_trails.copy()
        
        # Filtrowanie
        filtered = trail_data.filter_by_region("TATRY")
        
        # Sprawdzenie liczby przefiltrowanych tras
        assert len(filtered) == 2
        assert len(trail_data.filtered_trails) == 2
        
        # Sprawdzenie czy wszystkie trasy są z właściwego regionu
        for trail in filtered:
            assert trail.region == "TATRY"
    
    def test_get_regions(self, trail_data, sample_trails):
        """Test pobierania unikalnych regionów."""
        # Ustawienie danych testowych
        trail_data.trails = sample_trails.copy()
        
        # Pobranie regionów
        regions = trail_data.get_regions()
        
        # Sprawdzenie listy regionów
        assert len(regions) == 2
        assert "TATRY" in regions
        assert "BESKIDY" in regions
    
    def test_get_difficulty_levels(self, trail_data, sample_trails):
        """Test pobierania unikalnych poziomów trudności."""
        # Ustawienie danych testowych
        trail_data.trails = sample_trails.copy()
        
        # Pobranie poziomów trudności
        difficulties = trail_data.get_difficulty_levels()
        
        # Sprawdzenie listy poziomów trudności
        assert len(difficulties) == 3
        assert 2 in difficulties
        assert 3 in difficulties
        assert 4 in difficulties
    
    def test_get_terrain_types(self, trail_data, sample_trails):
        """Test pobierania unikalnych typów terenu."""
        # Ustawienie danych testowych
        trail_data.trails = sample_trails.copy()
        
        # Pobranie typów terenu
        terrain_types = trail_data.get_terrain_types()
        
        # Sprawdzenie listy typów terenu
        assert len(terrain_types) == 2
        assert "szlak pieszy" in terrain_types
        assert "szlak górski" in terrain_types
    
    def test_get_length_range(self, trail_data, sample_trails):
        """Test pobierania zakresu długości tras."""
        # Ustawienie danych testowych
        trail_data.trails = sample_trails.copy()
        
        # Pobranie zakresu długości
        min_length, max_length = trail_data.get_length_range()
        
        # Sprawdzenie zakresu
        assert min_length == 5.2  # Najkrótsza trasa
        assert max_length == 11.2  # Najdłuższa trasa
    
    def test_save_to_csv(self, trail_data, sample_trails):
        """Test zapisywania danych do pliku CSV."""
        # Ustawienie danych testowych
        trail_data.trails = sample_trails.copy()
        trail_data.filtered_trails = sample_trails.copy()
        
        # Utworzenie tymczasowego pliku do zapisu
        temp_output = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_output.close()
        
        try:
            # Zapisanie danych
            trail_data.save_to_csv(temp_output.name)
            
            # Wczytanie danych z zapisanego pliku
            test_data = TrailData()
            test_data.load_from_csv(temp_output.name)
            
            # Sprawdzenie liczby rekordów
            assert len(test_data.trails) == 3
            
            # Sprawdzenie poprawności danych
            for i, trail in enumerate(test_data.trails):
                original = sample_trails[i]
                assert trail.id == original.id
                assert trail.name == original.name
                assert trail.region == original.region
                assert trail.length_km == original.length_km
        finally:
            # Usunięcie tymczasowego pliku
            os.unlink(temp_output.name)
    
    def test_save_to_json(self, trail_data, sample_trails):
        """Test zapisywania danych do pliku JSON."""
        # Ustawienie danych testowych
        trail_data.trails = sample_trails.copy()
        trail_data.filtered_trails = sample_trails.copy()
        
        # Utworzenie tymczasowego pliku do zapisu
        temp_output = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        temp_output.close()
        
        try:
            # Zapisanie danych
            trail_data.save_to_json(temp_output.name)
            
            # Wczytanie danych z zapisanego pliku
            test_data = TrailData()
            test_data.load_from_json(temp_output.name)
            
            # Sprawdzenie liczby rekordów
            assert len(test_data.trails) == 3
            
            # Sprawdzenie poprawności danych
            for i, trail in enumerate(test_data.trails):
                original = sample_trails[i]
                assert trail.id == original.id
                assert trail.name == original.name
                assert trail.region == original.region
                assert trail.length_km == original.length_km
        finally:
            # Usunięcie tymczasowego pliku
            os.unlink(temp_output.name)


if __name__ == '__main__':
    pytest.main() 