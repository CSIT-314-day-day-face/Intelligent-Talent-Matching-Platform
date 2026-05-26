from werkzeug.security import generate_password_hash, check_password_hash
from backend.database_connection import get_db_connection
import sqlite3

VALID_ROLES = {"candidate", "employer"}

def _table_for_role(role):
    if role not in VALID_ROLES:
        raise ValueError("Invalid role")
    return "Candidates" if role == "candidate" else "Employers"

def register_user(email, password, role, **profile_data):
    hashed_password = generate_password_hash(password)
    try:
        conn = get_db_connection()
        if role == "candidate":
            conn.execute(
                """
                INSERT INTO Candidates (
                    email, password, full_name, contact_info, education,
                    major, years_experience, work_experience, skills,
                    preferred_mode, preferred_location, location
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    email,
                    hashed_password,
                    profile_data.get("full_name", ""),
                    profile_data.get("contact_info", email),
                    profile_data.get("education", ""),
                    profile_data.get("major", ""),
                    profile_data.get("years_experience", ""),
                    profile_data.get("work_experience", ""),
                    profile_data.get("skills", ""),
                    profile_data.get("preferred_mode", ""),
                    profile_data.get("preferred_location", ""),
                    profile_data.get("location", profile_data.get("preferred_location", "")),
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO Employers (
                    email, password, company_name, company_info,
                    contact_info, location
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    email,
                    hashed_password,
                    profile_data.get("company_name", ""),
                    profile_data.get("company_info", ""),
                    profile_data.get("contact_info", email),
                    profile_data.get("location", ""),
                ),
            )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        print(f"Registration error: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()

def verify_login(email, password, role):
    try:
        conn = get_db_connection()
        table = _table_for_role(role)
        user = conn.execute(f"SELECT * FROM {table} WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user['password'], password):
            return dict(user)
        return None
    except Exception as e:
        print(f"Login verification error: {e}")
        return None
    finally:
        if 'conn' in locals(): conn.close()
