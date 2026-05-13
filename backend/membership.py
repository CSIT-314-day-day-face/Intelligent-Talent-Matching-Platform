import sqlite3
import os

def get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, 'database', 'platform.db')

def check_membership_status(user_id, role):
    # Check if a user is a premium member
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    table = "Candidates" if role == "candidate" else "Employers"
    
    cursor.execute(f"SELECT membership_status FROM {table} WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result['membership_status'] if result else 0

def upgrade_membership(user_id, role):
    # Upgrade user to premium status
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    table = "Candidates" if role == "candidate" else "Employers"
    
    try:
        cursor.execute(f"UPDATE {table} SET membership_status = 1 WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Upgrade failed: {e}")
        return False
    finally:
        conn.close()

def get_search_limit(membership_status):
    # Return result limit based on membership level
    return 10 if membership_status == 0 else None