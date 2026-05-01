"""Application settings."""

class Config:
    """Configuration class for the application."""
    
    def __init__(self):
        self.app_name = "PyLock Example App"
        self.version = "1.0.0"
        self.debug = True
    
    def get_info(self) -> str:
        """Get application information."""
        return f"{self.app_name} v{self.version}"
