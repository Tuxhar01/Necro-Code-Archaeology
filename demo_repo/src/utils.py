"""
Utility functions for the application.
Contains both dead code and undocumented-but-used code.
"""


def validate_input(data):
    # CASE 4: Undocumented but clearly used
    # No docstring, no comments, but called in main.py
    if not data or not isinstance(data, dict):
        return False
    if "id" not in data or "timestamp" not in data:
        return False
    return True


def format_old_date(timestamp):
    """
    CASE 2: Genuinely Dead Function #2
    Date formatter from v1.0 - no longer used.
    This was replaced by the new datetime handling system.
    Different pattern: leftover from removed feature.
    """
    from datetime import datetime
    if isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp)
    else:
        dt = timestamp
    return dt.strftime("%d/%m/%Y")


def parse_config_value(value):
    """
    Helper to parse configuration values.
    Used by the configuration system.
    """
    if isinstance(value, str):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        try:
            return int(value)
        except ValueError:
            return value
    return value

# Made with Bob
