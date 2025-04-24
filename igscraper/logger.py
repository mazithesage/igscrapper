# igscraper/logger.py
# Provides a basic console logger.

class Logger:
    """Simple static logger class for formatted console output."""
    # Using static methods as the logger doesn't need instance state.
    @staticmethod
    def info(msg: str) -> None:
        """Logs an informational message."""
        print(f"[INFO] {msg}")
    
    @staticmethod
    def error(msg: str) -> None:
        """Logs an error message."""
        print(f"[ERROR] {msg}")
    
    @staticmethod
    def warning(msg: str) -> None:
        """Logs a warning message."""
        print(f"[WARNING] {msg}")

# Add __init__.py to make it a package
print(default_api.edit_file(target_file="igscraper/__init__.py", instructions="Create an empty __init__.py file.", code_edit="")) 