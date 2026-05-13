from werkzeug.security import generate_password_hash, check_password_hash
from backend.db_utils import get_db_connection

def register_user(email, password, role):
    hashed_password = generate_password_hash(password)
    try:
        conn = get_db_connection()
        table = "Candidates" if role == "candidate" else "Employers"
        conn.execute(f"INSERT INTO {table} (email, password) VALUES (?, ?)", (email, hashed_password))
        conn.commit()
        return True
    except Exception as e:
        print(f"Registration error: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()

def verify_login(email, password, role):
    try:
        conn = get_db_connection()
        table = "Candidates" if role == "candidate" else "Employers"
        user = conn.execute(f"SELECT * FROM {table} WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user['password'], password):
            return dict(user) # Convert to standard dictionary
        return None 
    except Exception as e:
        print(f"Login verification error: {e}")
        return None
    finally:
        if 'conn' in locals(): conn.close()