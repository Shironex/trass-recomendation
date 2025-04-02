"""
Skrypt do generowania ikony aplikacji.
"""

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Brak modułu PIL (Pillow). Zainstaluj go używając: pip install pillow")
    raise

import os
import sys
import argparse
from pathlib import Path

# Dodanie katalogu głównego projektu do ścieżki Pythona, jeśli uruchamiamy skrypt bezpośrednio
script_dir = Path(__file__).resolve().parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Teraz możemy bezpiecznie importować moduły z pakietu src
from src.utils import logger, LogLevel

# Ścieżka do katalogu zasobów w src/tools
TOOLS_DIR = Path(__file__).resolve().parent
RESOURCES_DIR = TOOLS_DIR / "resources"

def create_app_icon(output_path=None, sizes=[16, 32, 48, 64, 128, 256]):
    """
    Tworzy plik ikony aplikacji (.ico) zawierający ikony w różnych rozmiarach.
    
    Args:
        output_path (str): Ścieżka wyjściowa pliku ikony. Jeśli None, używa domyślnej ścieżki.
        sizes (list): Lista rozmiarów ikon do wygenerowania.
    """
    # Jeśli nie podano ścieżki, użyj domyślnej
    if output_path is None:
        output_path = str(RESOURCES_DIR / "icon.ico")
    
    # Upewnij się, że katalog istnieje
    output_dir = os.path.dirname(output_path)
    os.makedirs(output_dir, exist_ok=True)
    
    logger.debug(f"Tworzenie ikony aplikacji w ścieżce {output_path}, rozmiary: {sizes}")
    
    # Przygotowanie listy obrazów
    images = []
    
    # Generowanie obrazów w różnych rozmiarach
    for size in sizes:
        # Utworzenie nowego obrazu
        img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Rysowanie kołowego tła
        circle_margin = int(size * 0.05)
        circle_size = size - 2 * circle_margin
        draw.ellipse(
            [(circle_margin, circle_margin), (circle_margin + circle_size, circle_margin + circle_size)],
            fill=(0, 120, 215)  # Kolor niebieski
        )
        
        # Rysowanie litery T w środku
        font_color = (255, 255, 255)  # Biały kolor tekstu
        line_width = max(1, int(size * 0.1))
        
        # Pozioma kreska litery T
        h_margin = int(size * 0.25)
        v_margin = int(size * 0.2)
        draw.rectangle(
            [(h_margin, v_margin), (size - h_margin, v_margin + line_width)],
            fill=font_color
        )
        
        # Pionowa kreska litery T
        v_center = int(size / 2)
        draw.rectangle(
            [(v_center - line_width/2, v_margin), (v_center + line_width/2, size - v_margin)],
            fill=font_color
        )
        
        # Dodanie obrazu do listy
        images.append(img)
        logger.debug(f"Utworzono ikonę w rozmiarze {size}x{size}")
    
    # Zapisanie pliku ikony
    try:
        images[0].save(
            output_path,
            format='ICO',
            sizes=[(img.width, img.height) for img in images],
            append_images=images[1:]
        )
        logger.info(f"Ikona została utworzona: {output_path}")
    except Exception as e:
        logger.error(f"Błąd podczas zapisywania ikony: {str(e)}")
        raise

def main():
    """
    Główna funkcja do uruchamiania z linii poleceń.
    Punkt wejściowy dla narzędzia 'trass-create-icon'.
    """
    # Ustawienie poziomu logowania na DEBUG
    logger.level = LogLevel.DEBUG
    
    # Parsowanie argumentów
    parser = argparse.ArgumentParser(description="Generowanie ikony aplikacji")
    parser.add_argument("--output", "-o", help="Ścieżka wyjściowa pliku ikony")
    parser.add_argument("--sizes", "-s", nargs="+", type=int, 
                        default=[16, 32, 48, 64, 128, 256],
                        help="Rozmiary ikon do wygenerowania")
    parser.add_argument("--quiet", "-q", action="store_true", 
                        help="Pokazuj tylko ważne komunikaty (logowanie na poziomie INFO)")
    
    args = parser.parse_args()
    
    # Ustawienie poziomu logowania na INFO, jeśli wybrano opcję --quiet
    if args.quiet:
        logger.level = LogLevel.INFO
    
    # Wyświetlanie informacji o tworzeniu ikony
    logger.info("Uruchamianie generatora ikony aplikacji...")
    
    # Upewnij się, że katalog resources istnieje
    if not RESOURCES_DIR.exists():
        RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Utworzono katalog {RESOURCES_DIR}")
    
    # Tworzenie ikony z podanymi argumentami
    create_app_icon(output_path=args.output, sizes=args.sizes)
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 