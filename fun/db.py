import sqlite3
import os

path = os.path.dirname(os.path.realpath(__file__))
sqlite_file = path + '/botcach.sqlite'

_CONN = sqlite3.connect(sqlite_file)
_DB = _CONN.cursor()


_DB.execute('''
    CREATE TABLE IF NOT EXISTS botcache_follow_counts
    (date TEXT UNIQUE, type TEXT, count INT);
    ''')
_DB.execute('''
    CREATE TABLE IF NOT EXISTS botcache_following_users
    (date TEXT, username TEXT UNIQUE, user_id INT);
        ''')

_DB.execute('''
    CREATE TABLE IF NOT EXISTS botcache_followers_cursor
    (date TEXT, username TEXT UNIQUE, cursor TEXT);
        ''')


async def run_upsert(query):
    _DB.execute(query)
    _CONN.commit()

async def get_follower_cursor(username):
    r = _DB.execute('''
      SELECT cursor FROM botcache_followers_cursor
      WHERE username = '{username}'
      '''.format(username=username)).fetchone()
    if r is None:
        return None
    return r[0]

async def save_followers_cursor(username, cursor):
    await run_upsert('''
      UPDATE botcache_followers_cursor SET cursor = '{cursor}'
      WHERE username = '{username}';
    '''.format(username=username, cursor=cursor))
    await run_upsert('''
      INSERT OR IGNORE INTO botcache_followers_cursor (date, username, cursor)
      VALUES (date('now'), '{username}', '{cursor}');
    '''.format(username=username, cursor=cursor))


async def insert_follow_count():
    await run_upsert('''
      UPDATE botcache_follow_counts SET count = count + 1
      WHERE date = date('now');
    ''')
    await run_upsert('''
      INSERT OR IGNORE INTO botcache_follow_counts (date, type, count)
      VALUES (date('now'), 'follows', 1);
    ''')


async def get_follow_count():
    r = _DB.execute('''
      SELECT count FROM botcache_follow_counts WHERE date = date('now')
      ''').fetchone()
    if r is None:
        return 0
    return r[0]

async def previously_followed(username, user_id):
    r = _DB.execute('''
      SELECT * FROM botcache_following_users
      WHERE username = '{username}'
      OR user_id = '{user_id}'
      '''.format(username=username, user_id=user_id))
    if r.fetchone() is None:
        return False
    return True

async def add_user_to_followed(username, user_id):
    await run_upsert('''
      INSERT OR IGNORE INTO botcache_following_users (date, username, user_id)
      VALUES (date('now'), '{username}', '{user_id}');
    '''.format(username=username, user_id=user_id))
