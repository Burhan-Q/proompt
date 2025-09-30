import csv
from io import StringIO
from pathlib import Path

from proompt.base.provider import BaseProvider


def to_markdown_table(headers: list[str], rows: list[list]) -> str:
    """Convert headers and rows to a markdown table format."""
    result = "No results found."

    if rows:
        # Create markdown table
        result = "| " + " | ".join(headers) + " |\n"
        result += "| " + " | ".join(["---"] * len(headers)) + " |\n"

        for row in rows:
            # Convert all values to strings and handle None values
            row_values = [str(value) if value is not None else "" for value in row]
            result += "| " + " | ".join(row_values) + " |\n"

    return result


class TableData:
    """Container for tabular data that can be converted to markdown format."""

    def __init__(self, headers: list[str], rows: list[list]) -> None:
        if not headers or not rows:
            raise ValueError("Headers and rows must be non-empty.")
        self.headers = headers
        self.rows = rows

    @classmethod
    def from_rows(cls, headers: list[str], rows: list[list]) -> "TableData":
        """Create TableData directly from headers and rows."""
        return cls(headers, rows)

    @classmethod
    def from_dicts(cls, data: list[dict]) -> "TableData":
        """Create TableData from a list of dictionaries."""
        headers, rows = [], []

        if data:
            headers = list(data[0].keys())
            rows = [[row.get(h, "") for h in headers] for row in data]

        return cls(headers, rows)

    @classmethod
    def from_csv_str(cls, csv_text: str) -> "TableData":
        """Create TableData from CSV text using the csv module."""
        headers, rows = [], []

        if csv_text.strip():
            reader = csv.reader(StringIO(csv_text))

            if row_data := list(reader):
                headers = row_data[0]
                rows = row_data[1:]

        return cls(headers, rows)

    def to_md(self) -> str:
        """Convert to markdown table format."""
        return to_markdown_table(self.headers, self.rows)


class FileDataProvider(BaseProvider, str):
    """A simple provider that returns the contents of a file."""

    def __init__(self, file: str | Path) -> None:
        self.file = Path(file)

    @property
    def name(self) -> str:
        """Get the name of the provider."""
        return f"{self.__class__.__name__} for {self.file}"

    @property
    def provider_ctx(self) -> str:
        """Get informational context about the provider."""
        return f"Used to retrieve data from the file {self.file}."
        # NOTE: Provider context should outline what specific information the provider has access to.

    def run(self, *args, **kwargs) -> str:
        """Return the string contents of the file."""
        return self.file.read_text(*args, **kwargs)


class CsvDataProvider(BaseProvider):
    """A simple provider that returns the contents of a CSV file."""

    def __init__(self, file: str | Path) -> None:
        self.file = Path(file)

    @property
    def name(self) -> str:
        """Get the name of the provider."""
        return f"{self.__class__.__name__} for {self.file}"

    @property
    def provider_ctx(self) -> str:
        """Get informational context about the provider."""
        return f"Returns a markdown formatted table of the CSV data from {self.file}."

    def run(self, *args, **kwargs) -> str:
        """Return the CSV data as a markdown table."""
        csv_text = self.file.read_text(*args, **kwargs)
        table_data = TableData.from_csv_str(csv_text)
        return table_data.to_md()


class SqliteProvider(BaseProvider):
    """A provider that executes SQL queries against a SQLite database and returns formatted results."""

    def __init__(self, database_path: str | Path, query: str, table_name: str | None = None) -> None:
        """Initialize the SQLite provider.

        Args:
            database_path: Path to the SQLite database file
            query: SQL query to execute (should be a SELECT statement for safety)
            table_name: Optional table name for better context description
        """
        self.database_path = Path(database_path)
        self.query = query.strip()
        self.table_name = table_name

        # Basic validation
        if not self.query.upper().strip().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed for security reasons")

    @property
    def name(self) -> str:
        """Get the name of the provider."""
        table_info = f" from {self.table_name}" if self.table_name else ""
        return f"{self.__class__.__name__} for {self.database_path}{table_info}"

    @property
    def provider_ctx(self) -> str:
        """Get informational context about the provider."""
        table_info = f" in table '{self.table_name}'" if self.table_name else ""
        return f"Executes SQL query against SQLite database {self.database_path}{table_info}. Query: {self.query}"

    def run(self, *args, **kwargs) -> str:
        """Execute the SQL query and return results as a markdown table."""
        import sqlite3

        with sqlite3.connect(self.database_path) as conn:
            cursor = conn.cursor()
            cursor.execute(self.query)
            results = cursor.fetchall()

            # Convert to TableData format
            headers = [description[0] for description in cursor.description]
            table_data = TableData.from_rows(headers, results)

            return table_data.to_md()

    async def arun(self, *args, **kwargs) -> str:
        """Asynchronously execute the SQL query and return results as a markdown table."""
        # For SQLite, we'll just run the synchronous version since SQLite is file-based
        # In a real async implementation, you might use aiosqlite or similar
        return self.run(*args, **kwargs)
