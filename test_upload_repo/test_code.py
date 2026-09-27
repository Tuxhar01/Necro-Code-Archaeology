"""Test repository for upload functionality."""

def dead_function():
    """This function is never called."""
    return "I am dead code"


def used_function_no_docs():
    # No docstring here
    return "I am used but undocumented"


def load_bearing_function():
    """This is referenced in config."""
    return "I am secretly important"


def normal_function():
    """
    A normal, well-documented function.
    
    Returns:
        str: A greeting message
    """
    return "Hello, world!"


# Use some functions
result = used_function_no_docs()
result2 = normal_function()

# Made with Bob
