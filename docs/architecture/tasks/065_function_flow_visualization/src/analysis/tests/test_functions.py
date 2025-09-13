"""
Test functions for AST parser testing.

These functions are defined at module level to ensure proper source code access.
"""

def simple_test_function(x, y):
    """Add two numbers."""
    return x + y

def complex_test_function(x):
    """Function with control flow."""
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                print(i)
        return x * 2
    else:
        return 0

def imports_test_function():
    """Function with imports."""
    import os
    from datetime import datetime
    return os.path.join("test", "file.txt")

def try_test_function():
    """Function with try-except."""
    try:
        x = 1 / 0
    except ZeroDivisionError:
        return "Error occurred"
    finally:
        return "Done"
