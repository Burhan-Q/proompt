"""Shared pytest fixtures for the base module tests."""

import pytest


@pytest.fixture
def simple_function():
    """A simple function for testing ToolContext."""
    def add_numbers(x: int, y: int = 1) -> int:
        """Add two numbers together."""
        return x + y
    return add_numbers


@pytest.fixture
def complex_function():
    """A more complex function for testing ToolContext."""
    def process_data(data: list, format_type: str = "json", verbose: bool = False) -> dict:
        """Process data and return formatted result."""
        return {"processed": len(data), "format": format_type, "verbose": verbose}
    return complex_function