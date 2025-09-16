import asyncio
try:
    import aiosqlite
except Exception:
    aiosqlite = None


async def async_fetch_users():
    """Fetch all users asynchronously using aiosqlite."""
    db_path = 'users.db'
    if aiosqlite is None:
        raise RuntimeError('aiosqlite is not installed')
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT * FROM users") as cursor:
            rows = await cursor.fetchall()
            return rows


async def async_fetch_older_users():
    """Fetch users older than 40 asynchronously."""
    db_path = 'users.db'
    if aiosqlite is None:
        raise RuntimeError('aiosqlite is not installed')
    async with aiosqlite.connect(db_path) as db:
        async with db.execute("SELECT * FROM users WHERE age > ?", (40,)) as cursor:
            rows = await cursor.fetchall()
            return rows


async def fetch_concurrently():
    results = await asyncio.gather(
        async_fetch_users(),
        async_fetch_older_users()
    )
    all_users, older_users = results
    print('All users:', all_users)
    print('Older than 40:', older_users)


if __name__ == '__main__':
    if aiosqlite is None:
        print('aiosqlite is not installed. Install it with: pip install aiosqlite')
    else:
        asyncio.run(fetch_concurrently())
