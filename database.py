#-*- coding: utf-8 -*-
import psycopg2 # type: ignore
from contextlib import contextmanager

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

DATABASE_URL = "postgresql://fastapi:fastapi@localhost:5432/photos"

@contextmanager
def get_db():
    with psycopg2.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            yield cursor
            cursor.commit()
print(repr(DATABASE_URL))