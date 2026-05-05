import sqlite3
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

db_path = os.path.join(base_dir, 'platform.db')
sql_path = os.path.join(base_dir, 'init_db.sql')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

with open(sql_path, 'r', encoding='utf-8') as f:
    sql_script = f.read()

cursor.executescript(sql_script)
conn.commit()
conn.close()

