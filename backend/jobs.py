from backend.database_connection import get_db_connection, row_to_dict, rows_to_dicts

JOB_SELECT = """
    SELECT
        Jobs.id, Jobs.employer_id, Jobs.title, Jobs.company_info,
        Jobs.description, Jobs.required_education, Jobs.required_skills,
        Jobs.years_experience, Jobs.work_mode, Jobs.location,
        Jobs.salary_range, Jobs.job_type, Jobs.created_at,
        Employers.company_name, Employers.email AS employer_email
    FROM Jobs
    JOIN Employers ON Jobs.employer_id = Employers.id
"""

def _skills_to_text(skills):
    if isinstance(skills, list):
        return ", ".join(str(skill).strip() for skill in skills if str(skill).strip())
    return skills or ""

def create_job(
    employer_id,
    title,
    location,
    description,
    salary,
    job_type,
    company_info="",
    required_education="",
    required_skills="",
    years_experience="",
    work_mode="",
):
    try:
        conn = get_db_connection()
        conn.execute(
            """
            INSERT INTO Jobs (
                employer_id, title, company_info, description,
                required_education, required_skills, years_experience,
                work_mode, location, salary_range, job_type
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                employer_id,
                title,
                company_info,
                description,
                required_education,
                _skills_to_text(required_skills),
                years_experience,
                work_mode or job_type,
                location,
                salary,
                job_type,
            ),
        )
        conn.commit()
        return True
    except Exception as e:
        print(f"Job creation failed: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()

def get_all_jobs(limit=None):
    conn = get_db_connection()
    sql = f"{JOB_SELECT} ORDER BY Jobs.created_at DESC, Jobs.id DESC"
    params = ()
    if limit:
        sql += " LIMIT ?"
        params = (limit,)
    jobs = conn.execute(sql, params).fetchall()
    conn.close()
    return rows_to_dicts(jobs)

def get_job(job_id):
    conn = get_db_connection()
    job = conn.execute(f"{JOB_SELECT} WHERE Jobs.id = ?", (job_id,)).fetchone()
    conn.close()
    return row_to_dict(job)

def get_employer_jobs(employer_id):
    conn = get_db_connection()
    jobs = conn.execute(
        f"{JOB_SELECT} WHERE Jobs.employer_id = ? ORDER BY Jobs.created_at DESC, Jobs.id DESC",
        (employer_id,),
    ).fetchall()
    conn.close()
    return rows_to_dicts(jobs)

def update_job(job_id, employer_id, **data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Jobs
            SET title = ?, company_info = ?, description = ?,
                required_education = ?, required_skills = ?,
                years_experience = ?, work_mode = ?, location = ?,
                salary_range = ?, job_type = ?
            WHERE id = ? AND employer_id = ?
            """,
            (
                data.get("title", ""),
                data.get("company_info", ""),
                data.get("description", ""),
                data.get("required_education", ""),
                _skills_to_text(data.get("required_skills", "")),
                data.get("years_experience", ""),
                data.get("work_mode", data.get("job_type", "")),
                data.get("location", ""),
                data.get("salary", data.get("salary_range", "")),
                data.get("job_type", data.get("work_mode", "")),
                job_id,
                employer_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Job update failed: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()

def delete_job_for_employer(job_id, employer_id):
    conn = get_db_connection()
    cursor = conn.execute(
        "DELETE FROM Jobs WHERE id = ? AND employer_id = ?",
        (job_id, employer_id),
    )
    conn.commit()
    conn.close()
    return cursor.rowcount > 0
