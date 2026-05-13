from backend.db_utils import get_db_connection

def update_candidate_profile(user_id, full_name, experience, skills, mode, location):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE Candidates 
            SET full_name = ?, work_experience = ?, skills = ?, preferred_mode = ?, location = ?
            WHERE id = ?
        ''', (full_name, experience, skills, mode, location, user_id))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Profile update error: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()