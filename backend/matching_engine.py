from thefuzz import fuzz
from backend.db_utils import get_db_connection

def _skills_to_set(skills):
    if not skills:
        return set()
    return {skill.strip().lower() for skill in skills.split(",") if skill.strip()}

def _has_value(value):
    return bool(str(value or "").strip())

def _limited(results, membership_status):
    return results if int(membership_status or 0) == 1 else results[:10]

def recommend_jobs(candidate_id, membership_status=0):
    try:
        conn = get_db_connection()
        candidate = conn.execute(
            """
            SELECT full_name, education, major, years_experience, summary,
                   work_experience, skills, preferred_mode,
                   preferred_location, location
            FROM Candidates
            WHERE id = ?
            """,
            (candidate_id,),
        ).fetchone()
        if not candidate:
            conn.close()
            return []

        jobs = conn.execute(
            """
            SELECT
                Jobs.id, Jobs.title, Jobs.description, Jobs.required_education,
                Jobs.required_skills, Jobs.years_experience, Jobs.work_mode,
                Jobs.location, Jobs.salary_range, Jobs.job_type,
                Jobs.company_info, Employers.company_name
            FROM Jobs
            JOIN Employers ON Jobs.employer_id = Employers.id
            """
        ).fetchall()
        conn.close()

        candidate_text = " ".join([
            candidate["education"] or "",
            candidate["major"] or "",
            candidate["years_experience"] or "",
            candidate["summary"] or "",
            candidate["work_experience"] or "",
            candidate["skills"] or "",
            candidate["preferred_mode"] or "",
            candidate["preferred_location"] or "",
            candidate["location"] or "",
        ]).lower()
        candidate_skills = _skills_to_set(candidate["skills"])
        candidate_location = (candidate["preferred_location"] or candidate["location"] or "").lower()
        candidate_mode = (candidate["preferred_mode"] or "").lower()

        scored_jobs = []
        for job in jobs:
            job_text = " ".join([
                job["title"] or "",
                job["company_name"] or "",
                job["company_info"] or "",
                job["description"] or "",
                job["required_education"] or "",
                job["required_skills"] or "",
                job["years_experience"] or "",
                job["work_mode"] or "",
                job["location"] or "",
                job["job_type"] or "",
            ]).lower()
            text_score = fuzz.token_set_ratio(candidate_text, job_text)
            required_skills = _skills_to_set(job["required_skills"])
            skill_score = 100 if required_skills and candidate_skills.intersection(required_skills) else 0
            location_score = 100 if candidate_location and candidate_location in (job["location"] or "").lower() else 0
            mode_score = 100 if candidate_mode and candidate_mode == (job["work_mode"] or "").lower() else 0
            final_score = round((text_score * 0.55) + (skill_score * 0.25) + (location_score * 0.1) + (mode_score * 0.1), 2)

            scored_jobs.append({
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

        scored_jobs.sort(key=lambda x: x["score"], reverse=True)
        return _limited(scored_jobs, membership_status)
    except Exception as e:
        print(f"Job recommendation error: {e}")
        return []

def recommend_candidates(job_id, membership_status=0):
    try:
        conn = get_db_connection()
        job = conn.execute(
            """
            SELECT title, description, required_education, required_skills,
                   years_experience, work_mode, location
            FROM Jobs
            WHERE id = ?
            """,
            (job_id,),
        ).fetchone()
        if not job:
            conn.close()
            return []

        all_candidates = conn.execute(
            """
            SELECT id, full_name, email, contact_info, education, major,
                   years_experience, summary, work_experience, skills,
                   preferred_mode, preferred_location, location
            FROM Candidates
            """
        ).fetchall()
        conn.close()

        scored_candidates = []
        job_requirements = " ".join([
            job["title"] or "",
            job["description"] or "",
            job["required_education"] or "",
            job["required_skills"] or "",
            job["years_experience"] or "",
            job["work_mode"] or "",
            job["location"] or "",
        ]).lower()
        job_skills = _skills_to_set(job["required_skills"])
        criteria_fields = [
            job["description"],
            job["required_education"],
            job["required_skills"],
            job["years_experience"],
            job["work_mode"],
            job["location"],
        ]
        filled_criteria_count = sum(1 for field in criteria_fields if _has_value(field))
        criteria_quality = filled_criteria_count / len(criteria_fields)

        for candidate in all_candidates:
            candidate_text = " ".join([
                candidate["education"] or "",
                candidate["major"] or "",
                candidate["years_experience"] or "",
                candidate["summary"] or "",
                candidate["work_experience"] or "",
                candidate["skills"] or "",
                candidate["preferred_mode"] or "",
                candidate["preferred_location"] or "",
                candidate["location"] or "",
            ]).lower()
            text_score = fuzz.token_set_ratio(job_requirements, candidate_text)
            candidate_skills = _skills_to_set(candidate["skills"])
            if job_skills:
                skill_score = round(
                    len(job_skills.intersection(candidate_skills)) / len(job_skills) * 100,
                    2,
                )
            else:
                skill_score = 0
            candidate_location = (candidate["preferred_location"] or candidate["location"] or "").lower()
            location_score = 100 if candidate_location and candidate_location in (job["location"] or "").lower() else 0
            mode_score = 100 if _has_value(job["work_mode"]) and (candidate["preferred_mode"] or "").lower() == (job["work_mode"] or "").lower() else 0
            education_score = 100 if _has_value(job["required_education"]) and (candidate["education"] or "").lower() in (job["required_education"] or "").lower() else 0
            experience_score = 100 if _has_value(job["years_experience"]) and (candidate["years_experience"] or "").lower() == (job["years_experience"] or "").lower() else 0

            final_score = (
                text_score * 0.25
                + skill_score * 0.35
                + education_score * 0.1
                + experience_score * 0.1
                + location_score * 0.1
                + mode_score * 0.1
            )

            if not job_skills:
                final_score = min(final_score, 62)
            if filled_criteria_count <= 2:
                final_score = min(final_score, 45)

            final_score = round(final_score * (0.75 + criteria_quality * 0.25), 2)

            scored_candidates.append({
                "id": candidate["id"],
                "name": candidate["full_name"],
                "full_name": candidate["full_name"],
                "email": candidate["email"],
                "contact_info": candidate["contact_info"],
                "education": candidate["education"],
                "major": candidate["major"],
                "years_experience": candidate["years_experience"],
                "work_experience": candidate["work_experience"],
                "skills": candidate["skills"],
                "preferred_mode": candidate["preferred_mode"],
                "preferred_location": candidate_location,
                "location": candidate_location,
                "score": final_score,
                "match_quality": "Low confidence" if filled_criteria_count <= 2 else "Profile match",
            })

        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return _limited(scored_candidates, membership_status)
    except Exception as e:
        print(f"Matching algorithm error: {e}")
        return []
