import sqlite3
import os

def get_db_connection():
    # Dynamically locate the database and return a standardized connection
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    db_path = os.path.join(project_root, 'database', 'platform.db')
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def row_to_dict(row):
    return dict(row) if row else None

def rows_to_dicts(rows):
    return [dict(row) for row in rows]
