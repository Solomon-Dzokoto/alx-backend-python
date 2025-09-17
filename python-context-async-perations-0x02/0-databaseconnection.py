#!/usr/bin/env python3
import sqlite3


class DatabaseConnection:
    """Class-based context manager that opens a sqlite3 connection to
    'users.db' and returns a cursor when entering the context. The
    connection is closed when exiting the context.
    """
    def __init__(self, db_path='users.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Ensure we always close the connection
        if self.cursor:
            try:
                self.cursor.close()
            except Exception:
                pass
        if self.conn:
            try:
                # If there was an exception, let caller decide; we just close
                self.conn.close()
            except Exception:
                pass


if __name__ == '__main__':
    # Use the context manager to run a simple query
    query = "SELECT * FROM users"
    with DatabaseConnection() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        print(rows)
