import sqlite3 
import functools

def with_db_connection(func):
    """Decorator that opens a sqlite3 connection (to 'users.db'),
    injects it as the first positional argument to the wrapped function
    and ensures the connection is closed after the call.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('users.db')
        try:
            # If the wrapped function already expects conn as first arg,
            # call it with conn prepended to positional args.
            return func(conn, *args, **kwargs)
        finally:
            conn.close()

    return wrapper

@with_db_connection
def get_user_by_id(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchone()

#### Fetch user by ID with automatic connection handling

user = get_user_by_id(user_id=1)
print(user)