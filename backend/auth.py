from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

def get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, 'database', 'platform.db')

def register_user(email, password, role):
    # Hash password and save user info to database
    hashed_password = generate_password_hash(password)
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    table = "Candidates" if role == "candidate" else "Employers"
    try:
        cursor.execute(f"INSERT INTO {table} (email, password) VALUES (?, ?)", (email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False 
    finally:
        conn.close()

def verify_login(email, password, role):
    # Verify user credentials and return user data
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    table = "Candidates" if role == "candidate" else "Employers"
    cursor.execute(f"SELECT * FROM {table} WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password'], password):
        return user 
    return None