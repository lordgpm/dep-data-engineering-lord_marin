#!/usr/bin/env python3
"""Run the Week 8 analysis queries (scripts/analysis.sql) against the clean dataset.

The clean CSV (data/processed/posts_clean.csv) is loaded into an in-memory
SQLite database as a `posts` table, then every query in scripts/analysis.sql is
executed and its results printed as a readable table.

Usage:
    python3 scripts/run_sql.py
"""

import csv
import os
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV_PATH = os.path.join(ROOT, "data", "processed", "posts_clean.csv")
SQL_PATH = os.path.join(ROOT, "scripts", "analysis.sql")

# Columns that should be stored as integers so that AVG/MIN/MAX and comparisons
# behave correctly. Empty values become NULL.
INT_COLUMNS = {
    "created_utc",
    "hour_manila",
    "year",
    "month",
    "score",
    "num_comments",
    "seeker_age",
}


def to_int(value):
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def load_posts(conn):
    with open(CSV_PATH, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        columns = reader.fieldnames
        if columns is None:
            raise SystemExit("CSV has no header row.")

        col_defs = ", ".join(
            f'"{c}" INTEGER' if c in INT_COLUMNS else f'"{c}" TEXT'
            for c in columns
        )
        conn.execute(f"CREATE TABLE posts ({col_defs})")

        placeholders = ", ".join(["?"] * len(columns))
        insert_sql = f"INSERT INTO posts VALUES ({placeholders})"

        def row_values(row):
            return [
                to_int(row.get(c)) if c in INT_COLUMNS else row.get(c)
                for c in columns
            ]

        conn.executemany(insert_sql, (row_values(r) for r in reader))
        conn.commit()
        n = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        print(f"Loaded {n:,} rows into SQLite table 'posts'.\n")


def split_statements(sql_text):
    """Split the SQL file into individual statements on ';' boundaries.

    The analysis file contains no ';' inside string literals, so a simple split
    is safe. Comment-only fragments are discarded.
    """
    statements = []
    for chunk in sql_text.split(";"):
        body = "\n".join(
            line for line in chunk.splitlines() if not line.strip().startswith("--")
        ).strip()
        if body:
            statements.append(body)
    return statements


def print_table(cursor, rows):
    headers = [d[0] for d in cursor.description]
    str_rows = [[("" if v is None else str(v)) for v in row] for row in rows]
    widths = [len(h) for h in headers]
    for row in str_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(cells):
        return " | ".join(cell.ljust(widths[i]) for i, cell in enumerate(cells))

    print(fmt(headers))
    print("-+-".join("-" * w for w in widths))
    for row in str_rows:
        print(fmt(row))
    print(f"({len(rows)} row{'s' if len(rows) != 1 else ''})\n")


def main():
    if not os.path.exists(CSV_PATH):
        raise SystemExit(
            f"Clean dataset not found at {CSV_PATH}. "
            "Run 'python3 scripts/transform.py' first."
        )

    with open(SQL_PATH, encoding="utf-8") as fh:
        sql_text = fh.read()

    conn = sqlite3.connect(":memory:")
    load_posts(conn)

    for i, stmt in enumerate(split_statements(sql_text), 1):
        print(f"--- Query {i} ---")
        cursor = conn.execute(stmt)
        rows = cursor.fetchall()
        print_table(cursor, rows)

    conn.close()


if __name__ == "__main__":
    main()