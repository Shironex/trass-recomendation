"""
Moduł do obsługi hot reload dla aplikacji.
"""

import sys
import time
import subprocess
import threading
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Dodanie katalogu głównego projektu do ścieżki Pythona
sys.path.append('.')
from src.utils import logger, LogLevel


class FileChangeHandler(FileSystemEventHandler):
    """
    Klasa obsługująca zdarzenia zmiany plików.
    """
    
    def __init__(self, directories=None, patterns=None, ignore_patterns=None, reload_callback=None):
        """
        Inicjalizacja handlera zmiany plików.
        
        Args:
            directories (list): Lista katalogów do obserwowania
            patterns (list): Lista wzorców plików do monitorowania (np. *.py)
            ignore_patterns (list): Lista wzorców plików do ignorowania
            reload_callback (function): Funkcja wywoływana przy wykryciu zmiany
        """
        self.directories = directories or ["."]
        self.patterns = patterns or ["*.py"]
        self.ignore_patterns = ignore_patterns or ["*/__pycache__/*", "*.pyc", "*/.git/*"]
        self.reload_callback = reload_callback
        self.last_reload_time = time.time()
        self.reload_cooldown = 1.0  # Minimalny czas (sekundy) między przeładowaniami
    
    def on_modified(self, event):
        """Obsługa zdarzenia modyfikacji pliku."""
        if not event.is_directory and self._should_handle_event(event.src_path):
            current_time = time.time()
            if current_time - self.last_reload_time >= self.reload_cooldown:
                logger.debug(f"Wykryto zmianę w pliku: {event.src_path}")
                if self.reload_callback:
                    # Uruchamiamy callback w nowym wątku, aby uniknąć problemów z wątkami
                    threading.Thread(
                        target=self.reload_callback, 
                        args=(event.src_path,),
                        daemon=True
                    ).start()
                self.last_reload_time = current_time
    
    def on_created(self, event):
        """Obsługa zdarzenia utworzenia pliku."""
        if not event.is_directory and self._should_handle_event(event.src_path):
            current_time = time.time()
            if current_time - self.last_reload_time >= self.reload_cooldown:
                logger.debug(f"Wykryto nowy plik: {event.src_path}")
                if self.reload_callback:
                    # Uruchamiamy callback w nowym wątku, aby uniknąć problemów z wątkami
                    threading.Thread(
                        target=self.reload_callback, 
                        args=(event.src_path,),
                        daemon=True
                    ).start()
                self.last_reload_time = current_time
    
    def _should_handle_event(self, file_path):
        """
        Sprawdza, czy plik powinien być obsługiwany przez handler.
        
        Args:
            file_path (str): Ścieżka do pliku
            
        Returns:
            bool: True, jeśli plik powinien być obsługiwany
        """
        # Sprawdzenie wzorców plików
        matches_pattern = any(Path(file_path).match(pattern) for pattern in self.patterns)
        if not matches_pattern:
            return False
        
        # Sprawdzenie wzorców ignorowania
        matches_ignore = any(Path(file_path).match(pattern) for pattern in self.ignore_patterns)
        if matches_ignore:
            return False
        
        return True


class HotReloader:
    """
    Klasa do obsługi hot reloadu aplikacji.
    """
    
    def __init__(self, app_exit_callback=None, 
                 directories=None, patterns=None, ignore_patterns=None,
                 reload_on_change=True):
        """
        Inicjalizacja hot reloadera.
        
        Args:
            app_exit_callback (function): Funkcja wywoływana przed zamknięciem aplikacji
            directories (list): Lista katalogów do obserwowania
            patterns (list): Lista wzorców plików do monitorowania (np. *.py)
            ignore_patterns (list): Lista wzorców plików do ignorowania
            reload_on_change (bool): Czy automatycznie przeładowywać przy zmianach
        """
        self.app_exit_callback = app_exit_callback
        self.directories = directories or ["src"]
        self.patterns = patterns or ["*.py"]
        self.ignore_patterns = ignore_patterns or ["*/__pycache__/*", "*.pyc", "*/.git/*", "*/.pytest_cache/*"]
        self.reload_on_change = reload_on_change
        self.observer = None
        
        logger.debug("Inicjalizacja hot reloadera")
    
    def start(self):
        """Uruchamia obserwowanie plików."""
        if self.observer:
            logger.warn("Hot reloader już uruchomiony")
            return
        
        handler = FileChangeHandler(
            directories=self.directories,
            patterns=self.patterns,
            ignore_patterns=self.ignore_patterns,
            reload_callback=self.reload_app if self.reload_on_change else None
        )
        
        self.observer = Observer()
        for directory in self.directories:
            abs_path = Path(directory).absolute()
            logger.debug(f"Dodawanie katalogu do obserwacji: {abs_path}")
            self.observer.schedule(handler, str(abs_path), recursive=True)
        
        logger.info("Uruchamianie obserwatora plików dla hot reloadu")
        self.observer.start()
    
    def stop(self):
        """Zatrzymuje obserwowanie plików."""
        if self.observer:
            logger.info("Zatrzymywanie hot reloadera")
            # Używamy funkcji stop bez join, aby uniknąć zakleszczeń wątków
            self.observer.stop()
            # Nie używamy join, gdy jesteśmy w tym samym wątku
            # Sprawdzimy, czy jesteśmy w głównym wątku by uniknąć błędu
            if threading.current_thread() is not threading.main_thread():
                try:
                    self.observer.join()
                except RuntimeError as e:
                    logger.debug(f"Nie można dołączyć wątku: {str(e)}")
            self.observer = None
    
    def reload_app(self, changed_file=None):
        """
        Przeładowuje aplikację.
        
        Args:
            changed_file (str): Plik, który został zmieniony
        """
        logger.info(f"Przeładowywanie aplikacji z powodu zmiany w: {changed_file}")
        
        # Wywołaj callback przed zamknięciem aplikacji
        if self.app_exit_callback:
            try:
                self.app_exit_callback()
            except Exception as e:
                logger.error(f"Błąd podczas wywoływania callback przed zamknięciem: {str(e)}")
        
        # Zatrzymaj obserwatora - używamy tylko stop bez join
        if self.observer:
            self.observer.stop()
            self.observer = None
        
        # Uruchom nową instancję aplikacji
        logger.debug("Uruchamianie nowej instancji aplikacji")
        python = sys.executable
        
        # Przygotowanie argumentów
        script_path = Path(sys.argv[0]).absolute()
        args = [python, str(script_path)] + sys.argv[1:]
        
        logger.debug(f"Wykonywanie: {' '.join(args)}")
        try:
            # Uruchom nową instancję aplikacji
            subprocess.Popen(args)
            
            # Zakończ obecną instancję
            logger.debug("Kończenie obecnej instancji aplikacji")
            sys.exit(0)
        except Exception as e:
            logger.error(f"Błąd podczas uruchamiania nowej instancji aplikacji: {str(e)}")
            
            # Jeśli wystąpił błąd, ponownie uruchom obserwatora
            self.start()


def enable_hot_reload(app_exit_callback=None, directories=None, 
                     patterns=None, ignore_patterns=None):
    """
    Włącza hot reload dla aplikacji.
    
    Args:
        app_exit_callback (function): Funkcja wywoływana przed zamknięciem aplikacji
        directories (list): Lista katalogów do obserwowania
        patterns (list): Lista wzorców plików do monitorowania (np. *.py)
        ignore_patterns (list): Lista wzorców plików do ignorowania
        
    Returns:
        HotReloader: Instancja hot reloadera
    """
    try:
        # Sprawdź, czy watchdog jest zainstalowany
        import watchdog
    except ImportError:
        logger.error("Nie można włączyć hot reloadu - brak biblioteki watchdog")
        logger.info("Zainstaluj watchdog używając: pip install watchdog")
        return None
    
    logger.info("Włączanie hot reloadu dla aplikacji")
    reloader = HotReloader(
        app_exit_callback=app_exit_callback,
        directories=directories,
        patterns=patterns,
        ignore_patterns=ignore_patterns
    )
    reloader.start()
    return reloader 