import sqlite3
import os
from thefuzz import fuzz

def get_db_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    return os.path.join(project_root, 'database', 'platform.db')

def fuzzy_search_jobs(user_query, membership_status=0):
    # Perform fuzzy matching search on jobs
    db_path = get_db_path()
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, location, description, job_type FROM Jobs")
        all_jobs = cursor.fetchall()
        conn.close()

        scored_results = []
        for job in all_jobs:
            title_score = fuzz.partial_ratio(user_query.lower(), job['title'].lower())
            desc_score = fuzz.partial_ratio(user_query.lower(), job['description'].lower())
            final_score = max(title_score, desc_score)

            if final_score > 60:
                scored_results.append({
                    "id": job['id'],
                    "title": job['title'],
                    "location": job['location'],
                    "description": job['description'],
                    "score": final_score
                })

        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results if membership_status == 1 else scored_results[:10]

    except Exception as e:
        print(f"Search error: {e}")
        return []