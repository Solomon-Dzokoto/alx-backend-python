import sqlite3 
import functools
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


def transactional(func):
	"""Decorator that wraps a DB operation in a transaction. The wrapped
	function is expected to accept a sqlite3 connection as its first
	positional argument. On success commit; on exception rollback and
	re-raise the exception.
	"""
	@functools.wraps(func)
	def wrapper(conn, *args, **kwargs):
		try:
			result = func(conn, *args, **kwargs)
			conn.commit()
			return result
		except Exception:
			conn.rollback()
			raise

	return wrapper

@with_db_connection
@transactional
def update_user_email(conn, user_id, new_email):
	cursor = conn.cursor()
	cursor.execute("UPDATE users SET email = ? WHERE id = ?", (new_email, user_id))

#### Update user's email with automatic transaction handling

update_user_email(user_id=1, new_email='Crawford_Cartwright@hotmail.com')