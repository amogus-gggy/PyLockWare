import utils
from config.settings import Config

def main():
    """Main entry point for the example application."""
    config = Config()
    print(f"App Name: {config.app_name}")
    print(f"Version: {config.version}")
    
    result = utils.calculate_sum(10, 20)
    print(f"Calculation result: {result}")
    
    print("Hello from packed PyLock application!")
    
if __name__ == "__main__":
    main()
