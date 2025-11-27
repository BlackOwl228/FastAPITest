import sqlite3
from contextlib import contextmanager

DATABASE_URL = "E:/Web Project/photos.db"

@contextmanager
def get_db():
    connection = sqlite3.connect(DATABASE_URL)
    connection.row_factory = sqlite3.Row  # Чтобы получать словари вместо кортежей
    cursor = connection.cursor()
    try:
        yield cursor
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()