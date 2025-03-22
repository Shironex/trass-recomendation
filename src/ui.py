"""
User Interface module.
This module handles all user interactions and menu display.
"""

from utils import Utils

class UserInterface:
    def __init__(self):
        """Initialize the UserInterface class."""
        self.running = True
        self.current_menu = "main"
        self.utils = Utils()
        
    def run(self):
        """Main application loop."""
        while self.running:
            self.utils.clear_console()
            self.display_menu()
            choice = self.get_user_input()
            self.handle_choice(choice)
    
    def display_menu(self):
        """Display the current menu based on the current_menu state."""
        if self.current_menu == "main":
            self._display_main_menu()
        elif self.current_menu == "trail_filter":
            self._display_trail_filter_menu()
        elif self.current_menu == "weather_preferences":
            self._display_weather_preferences_menu()
    
    def _display_main_menu(self):
        """Display the main menu options."""
        print("\n=== Tourist Route Recommender ===")
        print("1. Filter trails")
        print("2. Set weather preferences")
        print("3. Get recommendations")
        print("4. Exit")
        print("================================")
    
    def _display_trail_filter_menu(self):
        """Display the trail filtering menu options."""
        print("\n=== Trail Filtering ===")
        print("1. Filter by length")
        print("2. Filter by difficulty")
        print("3. Filter by region")
        print("4. Back to main menu")
        print("======================")
    
    def _display_weather_preferences_menu(self):
        """Display the weather preferences menu options."""
        print("\n=== Weather Preferences ===")
        print("1. Set temperature range")
        print("2. Set precipitation preferences")
        print("3. Set sunshine preferences")
        print("4. Back to main menu")
        print("==========================")
    
    def get_user_input(self):
        """Get and validate user input."""
        while True:
            try:
                choice = input("\nEnter your choice (1-4): ")
                if choice.isdigit() and 1 <= int(choice) <= 4:
                    return int(choice)
                print("Please enter a number between 1 and 4.")
            except ValueError:
                print("Please enter a valid number.")
    
    def handle_choice(self, choice):
        """Handle user menu choices."""
        if self.current_menu == "main":
            self._handle_main_menu_choice(choice)
        elif self.current_menu == "trail_filter":
            self._handle_trail_filter_choice(choice)
        elif self.current_menu == "weather_preferences":
            self._handle_weather_preferences_choice(choice)
    
    def _handle_main_menu_choice(self, choice):
        """Handle choices from the main menu."""
        if choice == 1:
            self.current_menu = "trail_filter"
        elif choice == 2:
            self.current_menu = "weather_preferences"
        elif choice == 3:
            print("\nGetting recommendations... (To be implemented)")
            input("\nPress Enter to continue...")
        elif choice == 4:
            self.running = False
    
    def _handle_trail_filter_choice(self, choice):
        """Handle choices from the trail filter menu."""
        if choice == 1:
            self._get_length_preferences()
        elif choice == 2:
            self._get_difficulty_preferences()
        elif choice == 3:
            self._get_region_preferences()
        elif choice == 4:
            self.current_menu = "main"
    
    def _handle_weather_preferences_choice(self, choice):
        """Handle choices from the weather preferences menu."""
        if choice == 1:
            self._get_temperature_preferences()
        elif choice == 2:
            self._get_precipitation_preferences()
        elif choice == 3:
            self._get_sunshine_preferences()
        elif choice == 4:
            self.current_menu = "main"
    
    def _get_length_preferences(self):
        """Get user preferences for trail length."""
        print("\nEnter preferred trail length range:")
        try:
            min_length = float(input("Minimum length (km): "))
            max_length = float(input("Maximum length (km): "))
            print(f"Trail length preferences set: {min_length}-{max_length} km")
            input("\nPress Enter to continue...")
        except ValueError:
            print("Please enter valid numbers.")
            input("\nPress Enter to continue...")
    
    def _get_difficulty_preferences(self):
        """Get user preferences for trail difficulty."""
        print("\nSelect difficulty level (1-5):")
        print("1 - Very easy")
        print("2 - Easy")
        print("3 - Moderate")
        print("4 - Difficult")
        print("5 - Very difficult")
        try:
            difficulty = int(input("Enter your choice: "))
            if 1 <= difficulty <= 5:
                print(f"Difficulty level set to: {difficulty}")
            else:
                print("Please enter a number between 1 and 5.")
            input("\nPress Enter to continue...")
        except ValueError:
            print("Please enter a valid number.")
            input("\nPress Enter to continue...")
    
    def _get_region_preferences(self):
        """Get user preferences for trail region."""
        region = input("\nEnter preferred region: ")
        print(f"Region preference set to: {region}")
        input("\nPress Enter to continue...")
    
    def _get_temperature_preferences(self):
        """Get user preferences for temperature range."""
        print("\nEnter preferred temperature range:")
        try:
            min_temp = float(input("Minimum temperature (°C): "))
            max_temp = float(input("Maximum temperature (°C): "))
            print(f"Temperature preferences set: {min_temp}-{max_temp}°C")
            input("\nPress Enter to continue...")
        except ValueError:
            print("Please enter valid numbers.")
            input("\nPress Enter to continue...")
    
    def _get_precipitation_preferences(self):
        """Get user preferences for precipitation."""
        print("\nSelect precipitation preference:")
        print("1 - No rain")
        print("2 - Light rain")
        print("3 - Moderate rain")
        print("4 - Heavy rain")
        try:
            preference = int(input("Enter your choice: "))
            if 1 <= preference <= 4:
                print(f"Precipitation preference set to: {preference}")
            else:
                print("Please enter a number between 1 and 4.")
            input("\nPress Enter to continue...")
        except ValueError:
            print("Please enter a valid number.")
            input("\nPress Enter to continue...")
    
    def _get_sunshine_preferences(self):
        """Get user preferences for sunshine."""
        print("\nSelect sunshine preference:")
        print("1 - Full sun")
        print("2 - Partly cloudy")
        print("3 - Mostly cloudy")
        print("4 - Overcast")
        try:
            preference = int(input("Enter your choice: "))
            if 1 <= preference <= 4:
                print(f"Sunshine preference set to: {preference}")
            else:
                print("Please enter a number between 1 and 4.")
            input("\nPress Enter to continue...")
        except ValueError:
            print("Please enter a valid number.")
            input("\nPress Enter to continue...") 