import importlib
import sqlite3
from pathlib import Path

import pytest

from proompt.providers import CsvDataProvider, FileDataProvider, SqliteProvider, TableData


def test_csv_run_returns_raw_tabledata(tmp_path: Path):
    csv = tmp_path / "d.csv"
    csv.write_text("name,role\nAlice,Eng\n")
    result = CsvDataProvider(csv).run()
    assert isinstance(result, TableData)
    assert result.headers == ["name", "role"]
    assert result.rows == [["Alice", "Eng"]]
    assert "| name | role |" in result.to_md()


def test_sqlite_run_returns_raw_tabledata(tmp_path: Path):
    db = tmp_path / "d.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE t (a, b)")
    conn.execute("INSERT INTO t VALUES ('x', 'y')")
    conn.commit()
    conn.close()
    result = SqliteProvider(db, "SELECT a, b FROM t").run()
    assert isinstance(result, TableData)
    assert result.headers == ["a", "b"]
    assert result.rows == [("x", "y")]


def test_file_run_returns_raw_text(tmp_path: Path):
    f = tmp_path / "f.txt"
    f.write_text("hello")
    assert FileDataProvider(f).run() == "hello"


def test_providers_submodule_reexports():
    import proompt
    from proompt import providers
    from proompt.providers import data

    assert providers.CsvDataProvider is data.CsvDataProvider
    assert providers.SqliteProvider is data.SqliteProvider
    assert providers.FileDataProvider is data.FileDataProvider
    assert providers.TableData is data.TableData
    assert providers.to_markdown_table is data.to_markdown_table

    assert proompt.CsvDataProvider is providers.CsvDataProvider
    assert proompt.FileDataProvider is providers.FileDataProvider
    assert proompt.SqliteProvider is providers.SqliteProvider
    assert proompt.TableData is providers.TableData
    assert proompt.to_markdown_table is providers.to_markdown_table


def test_proompt_data_module_removed():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("proompt.data")


def test_empty_rows_renders_no_results_found():
    """A zero-row result set is a normal outcome, not a programming error."""
    result = TableData(["name", "role"], [])
    assert result.to_md() == "No results found."


def test_header_only_csv_end_to_end(tmp_path: Path):
    csv = tmp_path / "d.csv"
    csv.write_text("name,role\n")
    result = CsvDataProvider(csv).run()
    assert result.headers == ["name", "role"]
    assert result.rows == []
    assert result.to_md() == "No results found."


def test_sqlite_zero_row_query_end_to_end(tmp_path: Path):
    db = tmp_path / "d.db"
    conn = sqlite3.connect(db)
    conn.execute("CREATE TABLE t (a, b)")
    conn.commit()
    conn.close()
    result = SqliteProvider(db, "SELECT a, b FROM t").run()
    assert result.headers == ["a", "b"]
    assert result.rows == []
    assert result.to_md() == "No results found."
