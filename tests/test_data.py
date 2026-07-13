import sqlite3
from pathlib import Path

from proompt.data import CsvDataProvider, FileDataProvider, SqliteProvider, TableData


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
