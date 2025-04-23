from datetime import datetime

class Status:
    warning_count = 0
    error_count = 0

class Color:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"

def debug(component, message):
    """
    Logs a debug message with the component name and a timestamp.

    Args:
        component (str): The name of the component.
        message (str): The debug message to log.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {Color.BLUE}DEBUG{Color.RESET} {component}: {message}")

def log(component, message):
    """
    Logs a message with the component name and a timestamp.

    Args:
        component (str): The name of the component.
        message (str): The message to log.
    """

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {Color.GREEN}LOG{Color.RESET} {component}: {message}")

def log_error(component, message):
    """
    Logs an error message with the component name and a timestamp.

    Args:
        component (str): The name of the component.
        message (str): The error message to log.
    """

    Status.error_count += 1 
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {Color.RED}ERROR{Color.RESET} {component}: {message}")

def log_warning(component, message):
    """
    Logs a warning message with the component name and a timestamp.

    Args:
        component (str): The name of the component.
        message (str): The warning message to log.
    """

    Status.warning_count += 1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {Color.YELLOW}WARN{Color.RESET} {component}: {message}")