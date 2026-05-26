from backend.database_connection import get_db_connection, row_to_dict

def _skills_to_text(skills):
    if isinstance(skills, list):
        return ", ".join(str(skill).strip() for skill in skills if str(skill).strip())
    return skills or ""

def get_candidate_profile(user_id):
    conn = get_db_connection()
    profile = conn.execute(
        "SELECT id, email, full_name, contact_info, education, major, years_experience, "
        "summary, work_experience, skills, preferred_mode, preferred_location, location, "
        "membership_status FROM Candidates WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return row_to_dict(profile)

def get_employer_profile(user_id):
    conn = get_db_connection()
    profile = conn.execute(
        "SELECT id, email, company_name, company_info, contact_info, location, "
        "membership_status FROM Employers WHERE id = ?",
        (user_id,),
    ).fetchone()
    conn.close()
    return row_to_dict(profile)

def update_candidate_profile(user_id, **data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Candidates
            SET full_name = ?, contact_info = ?, education = ?, major = ?,
                years_experience = ?, summary = ?, work_experience = ?,
                skills = ?, preferred_mode = ?, preferred_location = ?, location = ?
            WHERE id = ?
            """,
            (
                data.get("full_name", ""),
                data.get("contact_info", data.get("email", "")),
                data.get("education", ""),
                data.get("major", ""),
                data.get("years_experience", data.get("experience", "")),
                data.get("summary", ""),
                data.get("work_experience", data.get("experience", "")),
                _skills_to_text(data.get("skills", "")),
                data.get("preferred_mode", data.get("mode", "")),
                data.get("preferred_location", data.get("location", "")),
                data.get("location", data.get("preferred_location", "")),
                user_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Candidate profile update error: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()

def update_employer_profile(user_id, **data):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE Employers
            SET company_name = ?, company_info = ?, contact_info = ?, location = ?
            WHERE id = ?
            """,
            (
                data.get("company_name", ""),
                data.get("company_info", ""),
                data.get("contact_info", data.get("email", "")),
                data.get("location", ""),
                user_id,
            ),
        )
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Employer profile update error: {e}")
        return False
    finally:
        if 'conn' in locals(): conn.close()
