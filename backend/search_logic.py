from thefuzz import fuzz
from backend.db_utils import get_db_connection

def fuzzy_search_jobs(user_query, location=None, job_type=None, membership_status=0):
    try:
        conn = get_db_connection()
        all_jobs = conn.execute("SELECT id, title, location, description, job_type, salary_range FROM Jobs").fetchall()
        conn.close()

        scored_results = []
        for job in all_jobs:
            if location and location.lower() not in job['location'].lower():
                continue
            if job_type and job_type.lower() != job['job_type'].lower():
                continue

            title_score = fuzz.partial_ratio(user_query.lower(), job['title'].lower())
            desc_score = fuzz.partial_ratio(user_query.lower(), job['description'].lower())
            final_score = max(title_score, desc_score)

            if final_score > 60 or user_query == "":
                scored_results.append({
                    "id": job['id'], "title": job['title'], "location": job['location'],
                    "description": job['description'], "job_type": job['job_type'],
                    "salary": job['salary_range'], "score": final_score
                })

        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results if membership_status == 1 else scored_results[:10]
    except Exception as e:
        print(f"Search filtering error: {e}")
        return []