import sqlite3
import os
from thefuzz import fuzz

def get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, 'database', 'platform.db')

def recommend_candidates(job_id, membership_status=0):
    # Algorithm to match candidates with job requirements
    db_path = get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("SELECT title, description, location FROM Jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        if not job:
            return []

        cursor.execute("SELECT id, full_name, skills, work_experience, location FROM Candidates")
        all_candidates = cursor.fetchall()
        conn.close()

        scored_candidates = []
        job_requirements = f"{job['title']} {job['description']}".lower()

        for candidate in all_candidates:
            skill_score = fuzz.partial_ratio(job_requirements, (candidate['skills'] or "").lower())
            location_score = 100 if candidate['location'] == job['location'] else 0
            final_score = (skill_score * 0.8) + (location_score * 0.2)

            if final_score > 50:
                scored_candidates.append({
                    "id": candidate['id'],
                    "name": candidate['full_name'],
                    "skills": candidate['skills'],
                    "score": round(final_score, 2)
                })

        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates if membership_status == 1 else scored_candidates[:10]

    except Exception as e:
        print(f"Matching algorithm error: {e}")
        return []