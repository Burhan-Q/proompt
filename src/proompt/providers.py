"""Discoverable namespace for concrete data providers.

Re-exports from proompt.data; both import paths are supported.
"""

from proompt.data import (
    CsvDataProvider,
    FileDataProvider,
    SqliteProvider,
    TableData,
    to_markdown_table,
)

__all__ = [
    "FileDataProvider",
    "CsvDataProvider",
    "SqliteProvider",
    "TableData",
    "to_markdown_table",
]
