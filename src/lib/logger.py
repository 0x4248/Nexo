def log(component, message):
    """
    Logs a message with the component name and a timestamp.

    Args:
        component (str): The name of the component.
        message (str): The message to log.
    """
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"NEXO LOG [{timestamp}] [{component}] {message}")

def log_error(component, message):
    """
    Logs an error message with the component name and a timestamp.

    Args:
        component (str): The name of the component.
        message (str): The error message to log.
    """
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"NEXO ERROR [{timestamp}] [{component}] {message}")

def log_warning(component, message):
    """
    Logs a warning message with the component name and a timestamp.

    Args:
        component (str): The name of the component.
        message (str): The warning message to log.
    """
    from datetime import datetime

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"NEXO WARNING [{timestamp}] [{component}] {message}")