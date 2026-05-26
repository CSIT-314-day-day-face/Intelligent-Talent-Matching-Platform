from thefuzz import fuzz
from backend.database_connection import get_db_connection
import re

EDUCATION_LEVELS = {
    "high school": 0,
    "certificate": 1,
    "diploma": 2,
    "bachelor": 3,
    "equivalent experience": 3,
    "master": 4,
    "phd": 5,
    "doctor": 5,
}

def _contains(value, needle):
    if not needle:
        return True
    return needle.lower() in (value or "").lower()

def _score(query, text):
    if not query:
        return 0
    query = query.lower().strip()
    text = (text or "").lower()
    return max(
        fuzz.partial_ratio(query, text),
        fuzz.token_set_ratio(query, text),
    )

def _skills_to_list(skills):
    if not skills:
        return []
    return [item.strip().lower() for item in skills.split(",") if item.strip()]

def _salary_floor(value):
    text = str(value or "").lower().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*k", text)
    if match:
        return float(match.group(1))
    match = re.search(r"\$?\s*(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    amount = float(match.group(1))
    return amount / 1000 if amount >= 1000 else amount

def _matches_min_salary(job_salary, selected_salary):
    if not selected_salary:
        return True
    selected_floor = _salary_floor(selected_salary)
    job_floor = _salary_floor(job_salary)
    if selected_floor is None or job_floor is None:
        return _contains(job_salary, selected_salary)
    return job_floor >= selected_floor

def _education_rank(value):
    text = str(value or "").lower()
    for key in ("phd", "doctor", "master", "bachelor", "equivalent experience", "diploma", "certificate", "high school"):
        if key in text:
            return EDUCATION_LEVELS[key]
    return None

def _matches_max_education(actual_education, selected_education):
    if not selected_education:
        return True
    selected_rank = _education_rank(selected_education)
    actual_rank = _education_rank(actual_education)
    if selected_rank is None or actual_rank is None:
        return _contains(actual_education, selected_education)
    return actual_rank <= selected_rank

def fuzzy_search_jobs(
    user_query,
    location=None,
    job_type=None,
    work_mode=None,
    salary=None,
    education=None,
    skill=None,
):
    try:
        conn = get_db_connection()
        all_jobs = conn.execute(
            """
            SELECT
                Jobs.id, Jobs.title, Jobs.location, Jobs.description,
                Jobs.required_education, Jobs.required_skills,
                Jobs.years_experience, Jobs.work_mode, Jobs.salary_range,
                Jobs.job_type, Jobs.company_info, Employers.company_name
            FROM Jobs
            JOIN Employers ON Jobs.employer_id = Employers.id
            """
        ).fetchall()
        conn.close()

        scored_results = []
        for job in all_jobs:
            if not _contains(job["location"], location):
                continue
            if job_type and not _contains(job["job_type"], job_type):
                continue
            if work_mode and not _contains(job["work_mode"], work_mode):
                continue
            if not _matches_min_salary(job["salary_range"], salary):
                continue
            if not _matches_max_education(job["required_education"], education):
                continue
            if skill and not _contains(job["required_skills"], skill):
                continue

            searchable_text = " ".join([
                job["title"] or "",
                job["company_name"] or "",
                job["company_info"] or "",
                job["description"] or "",
                job["required_education"] or "",
                job["required_skills"] or "",
                job["years_experience"] or "",
                job["work_mode"] or "",
                job["location"] or "",
                job["salary_range"] or "",
                job["job_type"] or "",
            ])
            final_score = _score(user_query, searchable_text)

            if final_score > 55 or user_query == "":
                scored_results.append({
                    "id": job["id"],
                    "title": job["title"],
                    "company_name": job["company_name"],
                    "location": job["location"],
                    "description": job["description"],
                    "required_education": job["required_education"],
                    "required_skills": job["required_skills"],
                    "years_experience": job["years_experience"],
                    "work_mode": job["work_mode"],
                    "job_type": job["job_type"],
                    "salary": job["salary_range"],
                    "score": final_score,
                })

        scored_results.sort(key=lambda x: x['score'], reverse=True)
        return scored_results
    except Exception as e:
        print(f"Search filtering error: {e}")
        return []

def fuzzy_search_candidates(
    user_query,
    location=None,
    work_mode=None,
    education=None,
    skill=None,
    experience=None,
):
    try:
        conn = get_db_connection()
        candidates = conn.execute(
            """
            SELECT id, email, full_name, contact_info, education, major,
                   years_experience, summary, work_experience, skills,
                   preferred_mode, preferred_location, location,
                   membership_status
            FROM Candidates
            """
        ).fetchall()
        conn.close()

        scored_results = []
        for candidate in candidates:
            candidate_location = candidate["preferred_location"] or candidate["location"]
            if not _contains(candidate_location, location):
                continue
            if work_mode and not _contains(candidate["preferred_mode"], work_mode):
                continue
            if not _matches_max_education(candidate["education"], education):
                continue
            if skill and not _contains(candidate["skills"], skill):
                continue
            if experience and not _contains(candidate["years_experience"], experience):
                continue

            searchable_text = " ".join([
                candidate["full_name"] or "",
                candidate["email"] or "",
                candidate["contact_info"] or "",
                candidate["education"] or "",
                candidate["major"] or "",
                candidate["years_experience"] or "",
                candidate["summary"] or "",
                candidate["work_experience"] or "",
                candidate["skills"] or "",
                candidate["preferred_mode"] or "",
                candidate["preferred_location"] or "",
                candidate["location"] or "",
            ])
            final_score = _score(user_query, searchable_text)

            if final_score > 55 or user_query == "":
                scored_results.append({
                    "id": candidate["id"],
                    "full_name": candidate["full_name"],
                    "email": candidate["email"],
                    "contact_info": candidate["contact_info"],
                    "education": candidate["education"],
                    "major": candidate["major"],
                    "years_experience": candidate["years_experience"],
                    "summary": candidate["summary"],
                    "work_experience": candidate["work_experience"],
                    "skills": candidate["skills"],
                    "preferred_mode": candidate["preferred_mode"],
                    "preferred_location": candidate_location,
                    "location": candidate_location,
                    "membership_status": candidate["membership_status"],
                    "score": final_score,
                })

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        return scored_results
    except Exception as e:
        print(f"Candidate search error: {e}")
        return []
