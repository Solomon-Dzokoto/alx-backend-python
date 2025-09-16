import sqlite3
import functools

#### decorator to lof SQL queries

def log_queries():
    """Decorator factory that returns a decorator which logs the SQL query
    passed to the wrapped function (either as a positional or keyword arg
    named 'query'). It prints the query before calling the function.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Try to find the SQL query in kwargs first, then in positional args
            query = kwargs.get('query')
            if query is None:
                # Heuristic: find first str-looking arg that starts with a SQL verb
                for a in args:
                    if isinstance(a, str):
                        q = a.strip().lower()
                        if q.startswith(('select', 'insert', 'update', 'delete', 'with')):
                            query = a
                            break
            if query is not None:
                print(f"Executing SQL query: {query}")
            else:
                print("Executing function (no SQL query found in args)")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@log_queries()
def fetch_all_users(query):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

#### fetch users while logging the query
users = fetch_all_users(query="SELECT * FROM users")