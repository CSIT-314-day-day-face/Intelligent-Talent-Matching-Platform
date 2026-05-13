from backend.db_utils import get_db_connection

def create_job(employer_id, title, location, description, salary, job_type):
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO Jobs (employer_id, title, location, description, salary_range, job_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (employer_id, title, location, description, salary, job_type))
        conn.commit()
        return True
    except Exception as e:
        print(f"Job creation failed: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()

def get_employer_jobs(employer_id):
    conn = get_db_connection()
    jobs = conn.execute("SELECT * FROM Jobs WHERE employer_id = ?", (employer_id,)).fetchall()
    conn.close()
    return [dict(row) for row in jobs]