import sqlite3
import os

def get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, 'database', 'platform.db')

def create_job(employer_id, title, location, description, salary, job_type):
    # Create a new job listing
    db_path = get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Jobs (employer_id, title, location, description, salary_range, job_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (employer_id, title, location, description, salary, job_type))
        conn.commit()
        return True
    except Exception as e:
        print(f"Job creation failed: {e}")
        return False
    finally:
        conn.close()

def get_employer_jobs(employer_id):
    # Retrieve all jobs posted by a specific employer
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Jobs WHERE employer_id = ?", (employer_id,))
    jobs = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jobs