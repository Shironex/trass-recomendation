"""
Console-related utility functions.
"""

import os
import platform

class ConsoleUtils:
    @staticmethod
    def clear_console():
        """
        Clear the console screen in a cross-platform way.
        Works on Windows, Linux, and macOS.
        """
        system = platform.system().lower()
        
        if system == 'windows':
            os.system('cls')
        elif system in ('linux', 'darwin'):  # darwin is macOS
            os.system('clear')
        else:
            # Fallback for unknown systems
            print('\n' * 100) 