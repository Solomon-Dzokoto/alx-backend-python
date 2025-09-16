import time
import sqlite3 
import functools

#### paste your with_db_decorator here

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


def retry_on_failure(retries=3, delay=2):
	"""Decorator factory that retries the wrapped function up to `retries`
	times when it raises an exception. Sleeps `delay` seconds between attempts.
	The wrapped function is expected to accept a sqlite3 connection as its
	first argument when used together with `with_db_connection`.
	"""
	def decorator(func):
		@functools.wraps(func)
		def wrapper(*args, **kwargs):
			last_exc = None
			for attempt in range(1, retries + 1):
				try:
					return func(*args, **kwargs)
				except Exception as e:
					last_exc = e
					if attempt == retries:
						# Exhausted retries — re-raise
						raise
					time.sleep(delay)

		return wrapper

	return decorator

@with_db_connection
@retry_on_failure(retries=3, delay=1)
def fetch_users_with_retry(conn):
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM users")
	return cursor.fetchall()


#### attempt to fetch users with automatic retry on failure

users = fetch_users_with_retry()
print(users)