import unittest
import os
import json
import csv
import tempfile
import time
from src.core.trail_data import TrailData, TrailRecord


class TestTrailData(unittest.TestCase):
    """Testy klasy TrailData z modułu core."""

    def setUp(self):
        """Przygotowanie danych do testów."""
        # Inicjalizacja instancji klasy TrailData
        self.trail_data = TrailData()
        
        # Przykladowe dane tras
        self.sample_trails = [
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
        
        # Przygotowanie tymczasowego pliku CSV
        self.temp_csv = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        with open(self.temp_csv.name, 'w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=[
                'id', 'name', 'region', 'start_lat', 'start_lon', 'end_lat', 'end_lon',
                'length_km', 'elevation_gain', 'difficulty', 'terrain_type', 'tags'
            ])
            writer.writeheader()
            for trail in self.sample_trails:
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
        
        # Przygotowanie tymczasowego pliku JSON
        self.temp_json = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        with open(self.temp_json.name, 'w', encoding='utf-8') as file:
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
                    for trail in self.sample_trails
                ]
            }, file, indent=2)
    
    def tearDown(self):
        """Usunięcie tymczasowych plików po zakończeniu testów."""
        # Zamknij pliki przed ich usunięciem
        try:
            self.temp_csv.close()
            self.temp_json.close()
        except:
            pass
        
        # Poczekaj chwilę, aby upewnić się, że pliki zostały zamknięte
        time.sleep(0.1)
        
        # Usuń pliki
        try:
            os.unlink(self.temp_csv.name)
        except:
            pass
        
        try:
            os.unlink(self.temp_json.name)
        except:
            pass
    
    def test_load_from_csv(self):
        """Test wczytywania danych z pliku CSV."""
        self.trail_data.load_from_csv(self.temp_csv.name)
        
        # Sprawdzenie liczby wczytanych tras
        self.assertEqual(len(self.trail_data.trails), 3)
        
        # Sprawdzenie poprawności wczytanych danych
        trail = self.trail_data.trails[0]
        self.assertEqual(trail.id, "T001")
        self.assertEqual(trail.name, "Dolina Kościeliska")
        self.assertEqual(trail.region, "TATRY")
        self.assertEqual(trail.length_km, 7.8)
        self.assertEqual(trail.elevation_gain, 320.0)
        self.assertEqual(trail.difficulty, 2)
        self.assertEqual(trail.terrain_type, "szlak pieszy")
        self.assertEqual(trail.tags, ["dolina", "łatwa", "rodzinna"])
    
    def test_load_from_json(self):
        """Test wczytywania danych z pliku JSON."""
        self.trail_data.load_from_json(self.temp_json.name)
        
        # Sprawdzenie liczby wczytanych tras
        self.assertEqual(len(self.trail_data.trails), 3)
        
        # Sprawdzenie poprawności wczytanych danych
        trail = self.trail_data.trails[0]
        self.assertEqual(trail.id, "T001")
        self.assertEqual(trail.name, "Dolina Kościeliska")
        self.assertEqual(trail.region, "TATRY")
        self.assertEqual(trail.length_km, 7.8)
        self.assertEqual(trail.difficulty, 2)
    
    def test_filter_by_length(self):
        """Test filtrowania tras według długości."""
        # Ustawienie danych testowych
        self.trail_data.trails = self.sample_trails.copy()
        self.trail_data.filtered_trails = self.sample_trails.copy()
        
        # Filtrowanie
        filtered = self.trail_data.filter_by_length(min_length=6.0, max_length=10.0)
        
        # Sprawdzenie liczby przefiltrowanych tras
        self.assertEqual(len(filtered), 1)
        self.assertEqual(len(self.trail_data.filtered_trails), 1)
        
        # Sprawdzenie czy wszystkie trasy są w odpowiednim zakresie długości
        for trail in filtered:
            self.assertTrue(6.0 <= trail.length_km <= 10.0)
    
    def test_filter_by_difficulty(self):
        """Test filtrowania tras według poziomu trudności."""
        # Ustawienie danych testowych
        self.trail_data.trails = self.sample_trails.copy()
        self.trail_data.filtered_trails = self.sample_trails.copy()
        
        # Filtrowanie
        filtered = self.trail_data.filter_by_difficulty(3)
        
        # Sprawdzenie liczby przefiltrowanych tras
        self.assertEqual(len(filtered), 1)
        self.assertEqual(len(self.trail_data.filtered_trails), 1)
        
        # Sprawdzenie czy wszystkie trasy mają właściwy poziom trudności
        for trail in filtered:
            self.assertEqual(trail.difficulty, 3)
    
    def test_filter_by_region(self):
        """Test filtrowania tras według regionu."""
        # Ustawienie danych testowych
        self.trail_data.trails = self.sample_trails.copy()
        self.trail_data.filtered_trails = self.sample_trails.copy()
        
        # Filtrowanie
        filtered = self.trail_data.filter_by_region("TATRY")
        
        # Sprawdzenie liczby przefiltrowanych tras
        self.assertEqual(len(filtered), 2)
        self.assertEqual(len(self.trail_data.filtered_trails), 2)
        
        # Sprawdzenie czy wszystkie trasy są z właściwego regionu
        for trail in filtered:
            self.assertEqual(trail.region, "TATRY")
    
    def test_get_regions(self):
        """Test pobierania unikalnych regionów."""
        # Ustawienie danych testowych
        self.trail_data.trails = self.sample_trails.copy()
        
        # Pobranie regionów
        regions = self.trail_data.get_regions()
        
        # Sprawdzenie listy regionów
        self.assertEqual(len(regions), 2)
        self.assertIn("TATRY", regions)
        self.assertIn("BESKIDY", regions)
    
    def test_get_difficulty_levels(self):
        """Test pobierania unikalnych poziomów trudności."""
        # Ustawienie danych testowych
        self.trail_data.trails = self.sample_trails.copy()
        
        # Pobranie poziomów trudności
        difficulties = self.trail_data.get_difficulty_levels()
        
        # Sprawdzenie listy poziomów trudności
        self.assertEqual(len(difficulties), 3)
        self.assertIn(2, difficulties)
        self.assertIn(3, difficulties)
        self.assertIn(4, difficulties)
    
    def test_get_terrain_types(self):
        """Test pobierania unikalnych typów terenu."""
        # Ustawienie danych testowych
        self.trail_data.trails = self.sample_trails.copy()
        
        # Pobranie typów terenu
        terrain_types = self.trail_data.get_terrain_types()
        
        # Sprawdzenie listy typów terenu
        self.assertEqual(len(terrain_types), 2)
        self.assertIn("szlak pieszy", terrain_types)
        self.assertIn("szlak górski", terrain_types)
    
    def test_get_length_range(self):
        """Test pobierania zakresu długości tras."""
        # Ustawienie danych testowych
        self.trail_data.trails = self.sample_trails.copy()
        
        # Pobranie zakresu długości
        min_length, max_length = self.trail_data.get_length_range()
        
        # Sprawdzenie zakresu
        self.assertEqual(min_length, 5.2)  # Najkrótsza trasa
        self.assertEqual(max_length, 11.2)  # Najdłuższa trasa
    
    def test_save_to_csv(self):
        """Test zapisywania danych do pliku CSV."""
        # Ustawienie danych testowych
        self.trail_data.trails = self.sample_trails.copy()
        self.trail_data.filtered_trails = self.sample_trails.copy()
        
        # Utworzenie tymczasowego pliku do zapisu
        temp_output = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
        temp_output.close()
        
        try:
            # Zapisanie danych
            self.trail_data.save_to_csv(temp_output.name)
            
            # Wczytanie danych z zapisanego pliku
            test_data = TrailData()
            test_data.load_from_csv(temp_output.name)
            
            # Sprawdzenie liczby rekordów
            self.assertEqual(len(test_data.trails), 3)
            
            # Sprawdzenie poprawności danych
            for i, trail in enumerate(test_data.trails):
                original = self.sample_trails[i]
                self.assertEqual(trail.id, original.id)
                self.assertEqual(trail.name, original.name)
                self.assertEqual(trail.region, original.region)
                self.assertEqual(trail.length_km, original.length_km)
        finally:
            # Usunięcie tymczasowego pliku
            os.unlink(temp_output.name)
    
    def test_save_to_json(self):
        """Test zapisywania danych do pliku JSON."""
        # Ustawienie danych testowych
        self.trail_data.trails = self.sample_trails.copy()
        self.trail_data.filtered_trails = self.sample_trails.copy()
        
        # Utworzenie tymczasowego pliku do zapisu
        temp_output = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
        temp_output.close()
        
        try:
            # Zapisanie danych
            self.trail_data.save_to_json(temp_output.name)
            
            # Wczytanie danych z zapisanego pliku
            test_data = TrailData()
            test_data.load_from_json(temp_output.name)
            
            # Sprawdzenie liczby rekordów
            self.assertEqual(len(test_data.trails), 3)
            
            # Sprawdzenie poprawności danych
            for i, trail in enumerate(test_data.trails):
                original = self.sample_trails[i]
                self.assertEqual(trail.id, original.id)
                self.assertEqual(trail.name, original.name)
                self.assertEqual(trail.region, original.region)
                self.assertEqual(trail.length_km, original.length_km)
        finally:
            # Usunięcie tymczasowego pliku
            os.unlink(temp_output.name)


if __name__ == '__main__':
    unittest.main() 