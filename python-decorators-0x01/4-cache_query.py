import time
import sqlite3 
import functools


query_cache = {}


def with_db_connection(func):
    """Open a sqlite3 connection to 'users.db', pass it as the first
    argument to the wrapped function and ensure it's closed afterwards.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            return func(conn, *args, **kwargs)
        finally:
            conn.close()

    return wrapper


def cache_query(func):
    """Decorator that caches results of functions that execute SQL queries.
    It finds the SQL query string either from the 'query' kwarg or by
    scanning positional args for a string starting with a SQL verb.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Locate query string
        query = kwargs.get('query')
        if query is None:
            for a in args:
                if isinstance(a, str):
                    q = a.strip().lower()
                    if q.startswith(('select', 'insert', 'update', 'delete', 'with')):
                        query = a
                        break

        if query is None:
            # Nothing to cache on — just call through
            return func(*args, **kwargs)

        # Use the query string as the cache key
        if query in query_cache:
            # Optionally, we could return a copy if results are mutable
            return query_cache[query]

        result = func(*args, **kwargs)
        query_cache[query] = result
        return result

    return wrapper

@with_db_connection
@cache_query
def fetch_users_with_cache(conn, query):
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchall()

#### First call will cache the result
users = fetch_users_with_cache(query="SELECT * FROM users")

#### Second call will use the cached result
users_again = fetch_users_with_cache(query="SELECT * FROM users")