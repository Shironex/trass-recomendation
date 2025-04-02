# Testy

Ta strona zawiera informacje na temat testowania aplikacji Trass Recommendation.

## Przegląd testów

Projekt wykorzystuje framework pytest do testowania różnych aspektów aplikacji. Testy są zorganizowane w następujące kategorie:
- Testy jednostkowe - sprawdzają działanie pojedynczych funkcji i metod
- Testy integracyjne - weryfikują interakcje między komponentami
- Testy UI - testują interfejs użytkownika

## Instalacja zależności testowych

Przed uruchomieniem testów, upewnij się, że zainstalowałeś wszystkie wymagane zależności deweloperskie:

```bash
pip install -e ".[dev]"
```

Ten polecenie zainstaluje:
- pytest - framework do testowania
- pytest-cov - narzędzie do analizy pokrycia kodu testami
- inne niezbędne narzędzia testowe

## Uruchamianie testów

### Uruchamianie wszystkich testów

Aby uruchomić wszystkie testy, użyj polecenia:

```bash
pytest
```

### Uruchamianie określonych testów

Możesz uruchomić tylko określone testy, podając ścieżkę do modułu, klasy lub funkcji testowej:

```bash
# Uruchomienie testów z określonego modułu
pytest tests/test_models/test_route.py

# Uruchomienie konkretnej klasy testowej
pytest tests/test_models/test_route.py::TestRouteModel

# Uruchomienie określonej funkcji testowej
pytest tests/test_models/test_route.py::TestRouteModel::test_route_creation
```

### Uruchamianie testów z określonymi markerami

Możesz także uruchamiać testy oznaczone specjalnymi markerami:

```bash
# Uruchomienie tylko testów jednostkowych
pytest -m "unit"

# Uruchomienie tylko testów integracyjnych
pytest -m "integration"

# Uruchomienie testów UI
pytest -m "ui"
```

## Analiza pokrycia kodu

Aby sprawdzić, jaka część kodu jest pokryta testami, użyj opcji `--cov`:

```bash
# Podstawowa analiza pokrycia
pytest --cov=src

# Bardziej szczegółowa analiza z raportem HTML
pytest --cov=src --cov-report=html
```

Po uruchomieniu drugiego polecenia, raport HTML zostanie wygenerowany w katalogu `htmlcov`. Możesz otworzyć plik `index.html` w przeglądarce, aby zobaczyć szczegółowy raport.

## Pisanie testów

### Struktura testów

Testy powinny być umieszczone w katalogu `tests/` w plikach z prefiksem `test_`. Na przykład, testy dla modułu `src/models/route.py` powinny być w pliku `tests/test_models/test_route.py`.

### Przykład testu jednostkowego

```python
import pytest
from src.models.route import Route

def test_route_creation():
    """Test tworzenia nowej trasy."""
    route = Route(name="Trasa testowa", distance=10.5, difficulty="easy")
    assert route.name == "Trasa testowa"
    assert route.distance == 10.5
    assert route.difficulty == "easy"

def test_route_invalid_difficulty():
    """Test walidacji trudności trasy."""
    with pytest.raises(ValueError):
        Route(name="Trasa testowa", distance=10.5, difficulty="invalid")
```

### Przykład testu z użyciem fixture

```python
import pytest
from src.models.route import Route

@pytest.fixture
def sample_route():
    """Fixture zwracająca przykładową trasę."""
    return Route(name="Trasa testowa", distance=10.5, difficulty="easy")

def test_route_distance_conversion(sample_route):
    """Test konwersji odległości z km na mile."""
    assert sample_route.distance_in_miles() == pytest.approx(6.5, 0.1)
```

## Mockowanie i stubowanie

Do mockowania obiektów w testach używamy biblioteki `unittest.mock`:

```python
from unittest.mock import Mock, patch
from src.controllers.route_controller import RouteController

def test_route_controller_with_mock():
    """Test kontrolera tras z użyciem mocka."""
    mock_model = Mock()
    mock_model.get_routes.return_value = [
        {"name": "Trasa 1", "distance": 10.5, "difficulty": "easy"},
        {"name": "Trasa 2", "distance": 15.2, "difficulty": "medium"}
    ]
    
    controller = RouteController(model=mock_model)
    routes = controller.get_all_routes()
    
    assert len(routes) == 2
    assert routes[0]["name"] == "Trasa 1"
    mock_model.get_routes.assert_called_once()
```

## Automatyzacja testów

Można skonfigurować ciągłą integrację (CI) do automatycznego uruchamiania testów przy każdym commit'cie. W tym celu używamy GitHub Actions lub innych narzędzi CI/CD.

## Najlepsze praktyki

- Pisz testy przed implementacją (TDD - Test-Driven Development)
- Testuj zarówno przypadki poprawne, jak i brzegowe
- Utrzymuj wysoki poziom pokrycia kodu testami
- Używaj odpowiednich asercji dla różnych typów testów
- Unikaj zależności między testami

## Rozwiązywanie problemów

### Testy nie znajdują modułów projektu

Upewnij się, że:
1. Zainstalowałeś pakiet w trybie edycyjnym: `pip install -e .`
2. Uruchamiasz testy z głównego katalogu projektu
3. Struktura importów w testach jest prawidłowa

### Niektóre testy nie działają na CI

Sprawdź:
1. Czy testy nie zależą od specyficznych dla środowiska warunków
2. Czy używasz mocków dla zewnętrznych zasobów
3. Czy nie ma problemów z zależnościami na środowisku CI 