from backend.db_utils import get_db_connection, row_to_dict, rows_to_dicts


APPLICATION_SELECT = """
    SELECT
        Applications.id,
        Applications.candidate_id,
        Applications.job_id,
        Applications.status,
        Applications.applied_at,
        Jobs.title,
        Jobs.location,
        Jobs.work_mode,
        Jobs.salary_range,
        Jobs.job_type,
        Jobs.company_info,
        Employers.company_name,
        Employers.email AS employer_email,
        Candidates.full_name,
        Candidates.email AS candidate_email,
        Candidates.contact_info,
        Candidates.education,
        Candidates.major,
        Candidates.years_experience,
        Candidates.skills,
        Candidates.preferred_mode,
        Candidates.preferred_location
    FROM Applications
    JOIN Jobs ON Applications.job_id = Jobs.id
    JOIN Employers ON Jobs.employer_id = Employers.id
    JOIN Candidates ON Applications.candidate_id = Candidates.id
"""


def apply_for_job(candidate_id, job_id):
    conn = get_db_connection()
    try:
        job = conn.execute(
            "SELECT id FROM Jobs WHERE id = ?",
            (job_id,),
        ).fetchone()
        if not job:
            return False, "Job not found"

        existing = conn.execute(
            """
            SELECT id
            FROM Applications
            WHERE candidate_id = ? AND job_id = ?
            """,
            (candidate_id, job_id),
        ).fetchone()
        if existing:
            return True, "Already applied"

        conn.execute(
            """
            INSERT INTO Applications (candidate_id, job_id)
            VALUES (?, ?)
            """,
            (candidate_id, job_id),
        )
        conn.commit()
        return True, "Application submitted"
    except Exception as e:
        print(f"Job application error: {e}")
        return False, "Application failed"
    finally:
        conn.close()


def get_application_for_candidate(candidate_id, job_id):
    conn = get_db_connection()
    row = conn.execute(
        """
        SELECT id, candidate_id, job_id, status, applied_at
        FROM Applications
        WHERE candidate_id = ? AND job_id = ?
        """,
        (candidate_id, job_id),
    ).fetchone()
    conn.close()
    return row_to_dict(row)


def get_recent_applications_for_candidate(candidate_id, limit=3):
    conn = get_db_connection()
    rows = conn.execute(
        f"""
        {APPLICATION_SELECT}
        WHERE Applications.candidate_id = ?
        ORDER BY Applications.applied_at DESC, Applications.id DESC
        LIMIT ?
        """,
        (candidate_id, limit),
    ).fetchall()
    conn.close()
    return rows_to_dicts(rows)


def get_recent_applicants_for_employer(employer_id, limit=3):
    conn = get_db_connection()
    rows = conn.execute(
        f"""
        {APPLICATION_SELECT}
        WHERE Jobs.employer_id = ?
        ORDER BY Applications.applied_at DESC, Applications.id DESC
        LIMIT ?
        """,
        (employer_id, max(limit * 10, 20)),
    ).fetchall()
    conn.close()
    recent_applicants = []
    seen_candidate_ids = set()

    for row in rows_to_dicts(rows):
        candidate_id = row["candidate_id"]
        if candidate_id in seen_candidate_ids:
            continue
        seen_candidate_ids.add(candidate_id)
        recent_applicants.append(row)
        if len(recent_applicants) >= limit:
            break

    return recent_applicants
