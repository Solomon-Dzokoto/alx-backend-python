import sqlite3


class ExecuteQuery:
    """Context manager that takes a SQL query and params, executes it on
    enter and stores the results. The connection is closed on exit.
    """
    def __init__(self, query, params=None, db_path='users.db'):
        self.query = query
        self.params = params or ()
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.result = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.cursor.execute(self.query, self.params)
        self.result = self.cursor.fetchall()
        return self.result

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close cursor and connection
        if self.cursor:
            try:
                self.cursor.close()
            except Exception:
                pass
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass


if __name__ == '__main__':
    q = "SELECT * FROM users WHERE age > ?"
    with ExecuteQuery(q, params=(25,)) as rows:
        print(rows)
