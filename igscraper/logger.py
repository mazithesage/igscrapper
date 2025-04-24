class Logger:
    """Simple logger class for console output."""
    @staticmethod
    def info(msg: str) -> None:
        print(f"[INFO] {msg}")
    
    @staticmethod
    def error(msg: str) -> None:
        print(f"[ERROR] {msg}")
    
    @staticmethod
    def warning(msg: str) -> None:
        print(f"[WARNING] {msg}")

# Add __init__.py to make it a package
print(default_api.edit_file(target_file="igscraper/__init__.py", instructions="Create an empty __init__.py file.", code_edit="")) 