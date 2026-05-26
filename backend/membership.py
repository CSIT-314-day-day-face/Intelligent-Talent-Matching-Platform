from backend.database_connection import get_db_connection

def check_membership_status(user_id, role):
    conn = get_db_connection()
    table = "Candidates" if role == "candidate" else "Employers"
    result = conn.execute(f"SELECT membership_status FROM {table} WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return result['membership_status'] if result else 0

def upgrade_membership(user_id, role):
    try:
        conn = get_db_connection()
        table = "Candidates" if role == "candidate" else "Employers"
        conn.execute(f"UPDATE {table} SET membership_status = 1 WHERE id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Upgrade failed: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()

def get_search_limit(membership_status):
    return 10 if membership_status == 0 else None
