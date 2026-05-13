import sqlite3
import os

def get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, 'database', 'platform.db')

def update_candidate_profile(user_id, full_name, experience, skills, mode, location):
    # Update detailed candidate profile information
    db_path = get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Candidates 
            SET full_name = ?, 
                work_experience = ?, 
                skills = ?, 
                preferred_mode = ?, 
                location = ?
            WHERE id = ?
        ''', (full_name, experience, skills, mode, location, user_id))
        conn.commit()
        return True
    except Exception as e:
        print(f"Profile update failed: {e}")
        return False
    finally:
        conn.close()