#!/usr/bin/env python3
"""
Main entry point for the Tourist Route Recommender application.
This module initializes the application and handles the main program flow.
"""

from ui import UserInterface

def main():
    """
    Main function that initializes and runs the application.
    """
    try:
        # Initialize the user interface
        ui = UserInterface()
        
        # Start the application
        ui.run()
        
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")
    finally:
        print("\nThank you for using Tourist Route Recommender!")

if __name__ == "__main__":
    main() 