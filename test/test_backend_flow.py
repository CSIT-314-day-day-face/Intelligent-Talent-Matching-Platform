import time
from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.api_server import app
from backend.database_connection import get_db_connection


PASSWORD = "password123"
RUN_ID = int(time.time())
CANDIDATE_EMAIL = f"full_candidate_{RUN_ID}@uow.edu.au"
SECOND_CANDIDATE_EMAIL = f"full_candidate_two_{RUN_ID}@uow.edu.au"
EMPLOYER_EMAIL = f"full_employer_{RUN_ID}@company.com"
SECOND_EMPLOYER_EMAIL = f"full_employer_two_{RUN_ID}@company.com"


class TestFailure(Exception):
    pass


def cleanup_test_data():
    conn = get_db_connection()
    try:
        candidate_rows = conn.execute(
            "SELECT id FROM Candidates WHERE email IN (?, ?)",
            (CANDIDATE_EMAIL, SECOND_CANDIDATE_EMAIL),
        ).fetchall()
        employer_rows = conn.execute(
            "SELECT id FROM Employers WHERE email IN (?, ?)",
            (EMPLOYER_EMAIL, SECOND_EMPLOYER_EMAIL),
        ).fetchall()

        candidate_ids = [row["id"] for row in candidate_rows]
        employer_ids = [row["id"] for row in employer_rows]
        job_ids = []
        if employer_ids:
            placeholders = ",".join("?" for _ in employer_ids)
            job_rows = conn.execute(
                f"SELECT id FROM Jobs WHERE employer_id IN ({placeholders})",
                employer_ids,
            ).fetchall()
            job_ids = [row["id"] for row in job_rows]

        if candidate_ids:
            placeholders = ",".join("?" for _ in candidate_ids)
            conn.execute(
                f"DELETE FROM Applications WHERE candidate_id IN ({placeholders})",
                candidate_ids,
            )

        if job_ids:
            placeholders = ",".join("?" for _ in job_ids)
            conn.execute(
                f"DELETE FROM Applications WHERE job_id IN ({placeholders})",
                job_ids,
            )
            conn.execute(f"DELETE FROM Jobs WHERE id IN ({placeholders})", job_ids)

        conn.execute(
            "DELETE FROM Candidates WHERE email IN (?, ?)",
            (CANDIDATE_EMAIL, SECOND_CANDIDATE_EMAIL),
        )
        conn.execute(
            "DELETE FROM Employers WHERE email IN (?, ?)",
            (EMPLOYER_EMAIL, SECOND_EMPLOYER_EMAIL),
        )
        conn.commit()
    finally:
        conn.close()


def expect(condition, message, detail=None):
    if not condition:
        raise TestFailure(f"{message}: {detail}")


def salary_floor(value):
    text = str(value or "").lower().replace(",", "")
    match = re.search(r"(\d+(?:\.\d+)?)\s*k", text)
    if match:
        return float(match.group(1))
    match = re.search(r"\$?\s*(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    amount = float(match.group(1))
    return amount / 1000 if amount >= 1000 else amount


def education_rank(value):
    text = str(value or "").lower()
    order = [
        ("phd", 5),
        ("doctor", 5),
        ("master", 4),
        ("bachelor", 3),
        ("equivalent experience", 3),
        ("diploma", 2),
        ("certificate", 1),
        ("high school", 0),
    ]
    for keyword, rank in order:
        if keyword in text:
            return rank
    return None


def request_json(client, method, path, expected_status=None, token=None, **kwargs):
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = getattr(client, method.lower())(path, headers=headers, **kwargs)
    data = response.get_json(silent=True) or {}
    if expected_status is not None:
        if isinstance(expected_status, tuple):
            ok = response.status_code in expected_status
        else:
            ok = response.status_code == expected_status
        expect(ok, f"{method.upper()} {path} returned {response.status_code}", data)
    return response, data


def register_candidate(client, email, name):
    return request_json(
        client,
        "post",
        "/api/register",
        200,
        json={
            "email": email,
            "password": PASSWORD,
            "role": "candidate",
            "full_name": name,
            "contact_info": email,
        },
    )[1]


def register_employer(client, email, company_name):
    return request_json(
        client,
        "post",
        "/api/register",
        200,
        json={
            "email": email,
            "password": PASSWORD,
            "role": "employer",
            "company_name": company_name,
            "contact_info": email,
            "location": "Sydney",
        },
    )[1]


def login(client, email, role):
    data = request_json(
        client,
        "post",
        "/api/login",
        200,
        json={"email": email, "password": PASSWORD, "role": role},
    )[1]
    expect(data.get("auth_token"), f"{role} login did not return auth token", data)
    return data


def create_valid_job(client, token):
    payload = {
        "title": "Full Functionality Test Software Engineer",
        "company_info": "Integration test company building real hiring software.",
        "description": "Build Python APIs, React screens, SQL reports, and recruitment matching features.",
        "required_education": "Bachelor",
        "required_skills": "Python, SQL, React",
        "years_experience": "3-5 Years",
        "work_mode": "Remote",
        "location": "Sydney",
        "salary": "$90k - $110k",
        "job_type": "Full-time",
    }
    request_json(client, "post", "/api/jobs", 200, token=token, json=payload)
    jobs = request_json(client, "get", "/api/employer/jobs", 200, token=token)[1]
    created = [
        job for job in jobs.get("results", [])
        if job.get("title") == payload["title"]
    ]
    expect(created, "created job was not returned by employer job list", jobs)
    return created[0]


def update_candidate_profile(client, token):
    payload = {
        "full_name": "Full Candidate Test",
        "contact_info": CANDIDATE_EMAIL,
        "education": "Bachelor",
        "major": "Computer Science",
        "years_experience": "3-5 Years",
        "summary": "Python backend developer interested in matching platforms.",
        "work_experience": "Three years building Flask APIs and SQL reporting.",
        "skills": "Python, SQL, React",
        "preferred_mode": "Remote",
        "preferred_location": "Sydney",
        "location": "Sydney",
    }
    request_json(client, "post", "/api/profile/update", 200, token=token, json=payload)
    profile_data = request_json(client, "get", "/api/profile", 200, token=token)[1]
    profile = profile_data.get("profile") or {}
    expect(profile.get("skills") == payload["skills"], "candidate skills did not save", profile)
    expect(profile.get("preferred_mode") == "Remote", "candidate preferred mode did not save", profile)
    return profile


def update_second_candidate_profile(client, token):
    payload = {
        "full_name": "Second Candidate Test",
        "contact_info": SECOND_CANDIDATE_EMAIL,
        "education": "Bachelor",
        "major": "Data Science",
        "years_experience": "0-3 Years",
        "summary": "Junior analyst profile for candidate detail access testing.",
        "work_experience": "One year testing data dashboards.",
        "skills": "Excel, SQL",
        "preferred_mode": "Hybrid",
        "preferred_location": "Melbourne",
        "location": "Melbourne",
    }
    request_json(client, "post", "/api/profile/update", 200, token=token, json=payload)
    return request_json(client, "get", "/api/profile", 200, token=token)[1]["profile"]


def update_employer_profile(client, token):
    payload = {
        "company_name": "Full Functionality Test Company",
        "company_info": "A realistic employer profile for integration testing.",
        "contact_info": EMPLOYER_EMAIL,
        "location": "Sydney",
    }
    request_json(client, "put", "/api/profile", 200, token=token, json=payload)
    profile_data = request_json(client, "get", "/api/profile", 200, token=token)[1]
    profile = profile_data.get("profile") or {}
    expect(profile.get("company_name") == payload["company_name"], "employer company name did not save", profile)
    expect(profile.get("location") == "Sydney", "employer location did not save", profile)
    return profile


def run_test():
    cleanup_test_data()
    public_client = app.test_client()
    candidate_client = app.test_client()
    second_candidate_client = app.test_client()
    employer_client = app.test_client()
    second_employer_client = app.test_client()
    passed = []

    try:
        jobs_data = request_json(public_client, "get", "/api/jobs", 200)[1]
        expect(jobs_data.get("count", 0) >= 200, "all jobs endpoint should expose seeded job data", jobs_data.get("count"))
        passed.append("Browse all jobs API")

        limited_jobs = request_json(public_client, "get", "/api/jobs?limit=10", 200)[1]
        expect(limited_jobs.get("count") == 10, "job limit parameter failed", limited_jobs.get("count"))
        passed.append("Job list limit API")

        register_candidate(public_client, CANDIDATE_EMAIL, "Full Candidate Test")
        register_candidate(public_client, SECOND_CANDIDATE_EMAIL, "Second Candidate Test")
        register_employer(public_client, EMPLOYER_EMAIL, "Full Functionality Test Company")
        register_employer(public_client, SECOND_EMPLOYER_EMAIL, "Second Employer Test Company")
        passed.append("Candidate and employer registration")

        duplicate = request_json(
            public_client,
            "post",
            "/api/register",
            400,
            json={"email": CANDIDATE_EMAIL, "password": PASSWORD, "role": "candidate"},
        )[1]
        expect(duplicate.get("status") == "error", "duplicate registration should fail", duplicate)
        passed.append("Duplicate registration validation")

        invalid_login = request_json(
            public_client,
            "post",
            "/api/login",
            400,
            json={"email": CANDIDATE_EMAIL, "password": PASSWORD},
        )[1]
        expect("role" in invalid_login.get("missing", []), "missing login role validation failed", invalid_login)
        passed.append("Login validation")

        wrong_password_login = request_json(
            public_client,
            "post",
            "/api/login",
            401,
            json={"email": CANDIDATE_EMAIL, "password": "wrong-password", "role": "candidate"},
        )[1]
        expect(
            wrong_password_login.get("message") == "Invalid email or password.",
            "wrong password should return a specific login error",
            wrong_password_login,
        )
        passed.append("Wrong password login error message")

        candidate_login = login(candidate_client, CANDIDATE_EMAIL, "candidate")
        candidate_token = candidate_login["auth_token"]
        second_candidate_login = login(second_candidate_client, SECOND_CANDIDATE_EMAIL, "candidate")
        second_candidate_token = second_candidate_login["auth_token"]
        employer_login = login(employer_client, EMPLOYER_EMAIL, "employer")
        employer_token = employer_login["auth_token"]
        second_employer_login = login(second_employer_client, SECOND_EMPLOYER_EMAIL, "employer")
        second_employer_token = second_employer_login["auth_token"]
        passed.append("Candidate and employer login")

        me_data = request_json(candidate_client, "get", "/api/me", 200, token=candidate_token)[1]
        expect(me_data.get("loggedIn") is True and me_data.get("role") == "candidate", "token verification failed", me_data)
        passed.append("Token verification")

        candidate_profile = update_candidate_profile(candidate_client, candidate_token)
        second_candidate_profile = update_second_candidate_profile(second_candidate_client, second_candidate_token)
        employer_profile = update_employer_profile(employer_client, employer_token)
        expect(candidate_profile.get("id") != second_candidate_profile.get("id"), "candidate test profiles share the same id")
        expect(employer_profile.get("company_name"), "employer profile missing company name", employer_profile)
        passed.append("Candidate and employer profile create/edit")

        candidate_self = request_json(
            candidate_client,
            "get",
            f"/api/candidates/{candidate_profile['id']}",
            200,
            token=candidate_token,
        )[1]
        expect(candidate_self.get("email") == CANDIDATE_EMAIL, "candidate cannot view own detail", candidate_self)
        request_json(
            candidate_client,
            "get",
            f"/api/candidates/{second_candidate_profile['id']}",
            403,
            token=candidate_token,
        )
        employer_candidate_detail = request_json(
            employer_client,
            "get",
            f"/api/candidates/{candidate_profile['id']}",
            200,
            token=employer_token,
        )[1]
        expect(employer_candidate_detail.get("email") == CANDIDATE_EMAIL, "employer cannot view candidate detail", employer_candidate_detail)
        passed.append("Candidate detail authorization")

        fuzzy_jobs = request_json(public_client, "get", "/api/search?q=sofware%20enginer", 200)[1]
        expect(fuzzy_jobs.get("count", 0) > 0, "fuzzy job search returned no results", fuzzy_jobs)
        combined_jobs = request_json(
            public_client,
            "get",
            "/api/search?q=software&location=Sydney&work_mode=Remote&skill=Python&education=Bachelor",
            200,
        )[1]
        expect(combined_jobs.get("count", 0) > 0, "combined job search returned no results", combined_jobs)
        salary_filtered_jobs = request_json(public_client, "get", "/api/search?salary=%24100k%2B", 200)[1]
        expect(salary_filtered_jobs.get("count", 0) > 0, "minimum salary filter returned no jobs", salary_filtered_jobs)
        expect(
            all(salary_floor(item.get("salary")) >= 100 for item in salary_filtered_jobs.get("results", [])),
            "minimum salary filter included a job below the selected salary",
            salary_filtered_jobs,
        )
        education_filtered_jobs = request_json(public_client, "get", "/api/search?education=Master", 200)[1]
        expect(education_filtered_jobs.get("count", 0) > 0, "max education job filter returned no jobs", education_filtered_jobs)
        expect(
            all(education_rank(item.get("required_education")) <= 4 for item in education_filtered_jobs.get("results", []) if education_rank(item.get("required_education")) is not None),
            "max education job filter included a higher education requirement",
            education_filtered_jobs,
        )
        candidates_search = request_json(
            employer_client,
            "get",
            "/api/candidates/search?q=Python&location=Sydney&work_mode=Remote&education=Bachelor&skill=Python&experience=3-5%20Years",
            200,
            token=employer_token,
        )[1]
        expect(candidates_search.get("count", 0) > 0, "combined candidate search returned no results", candidates_search)
        candidate_education_search = request_json(
            employer_client,
            "get",
            "/api/candidates/search?education=Master",
            200,
            token=employer_token,
        )[1]
        expect(
            any(item.get("education") == "Bachelor" for item in candidate_education_search.get("results", [])),
            "max education candidate filter should include Bachelor candidates when Master is selected",
            candidate_education_search,
        )
        request_json(candidate_client, "get", "/api/candidates/search?q=Python", 403, token=candidate_token)
        passed.append("Keyword, filter, combined, fuzzy, and role-limited search")

        candidate_recs_before = request_json(candidate_client, "get", "/api/recommendations/jobs", 200, token=candidate_token)[1]
        expect(candidate_recs_before.get("count") == 10, "non-member candidate recommendations should be top 10", candidate_recs_before.get("count"))
        passed.append("Candidate non-member Top 10 recommendations")

        request_json(candidate_client, "post", "/api/membership/upgrade", 200, token=candidate_token)
        candidate_recs_after = request_json(candidate_client, "get", "/api/recommendations/jobs", 200, token=candidate_token)[1]
        expect(candidate_recs_after.get("count", 0) > 10, "member candidate recommendations should be unlimited", candidate_recs_after.get("count"))
        passed.append("Candidate membership unlimited recommendations")

        request_json(employer_client, "post", "/api/jobs", 400, token=employer_token, json={"title": "Incomplete"})
        job = create_valid_job(employer_client, employer_token)
        job_id = job["id"]
        employer_jobs = request_json(employer_client, "get", "/api/employer/jobs", 200, token=employer_token)[1]
        expect(any(item["id"] == job_id for item in employer_jobs.get("results", [])), "employer job list missing created job", employer_jobs)
        passed.append("Employer job create/list validation")

        updated_payload = dict(job)
        updated_payload.update({
            "title": "Updated Full Functionality Test Software Engineer",
            "salary": "$100k - $125k",
            "job_type": "Full-time",
        })
        request_json(employer_client, "put", f"/api/jobs/{job_id}", 200, token=employer_token, json=updated_payload)
        updated_job = request_json(public_client, "get", f"/api/jobs/{job_id}", 200)[1]
        expect(updated_job.get("title") == updated_payload["title"], "job edit did not persist", updated_job)
        request_json(second_employer_client, "delete", f"/api/jobs/{job_id}", 404, token=second_employer_token)
        passed.append("Employer job edit and unauthorized delete protection")

        employer_recs_before = request_json(employer_client, "get", "/api/recommendations/candidates", 200, token=employer_token)[1]
        expect(employer_recs_before.get("count") == 10, "non-member employer recommendations should be top 10", employer_recs_before.get("count"))
        job_candidate_recs = request_json(employer_client, "get", f"/api/jobs/{job_id}/recommendations", 200, token=employer_token)[1]
        expect(job_candidate_recs.get("count") == 10, "job-specific non-member candidate recommendations should be top 10", job_candidate_recs.get("count"))
        request_json(employer_client, "post", "/api/membership/upgrade", 200, token=employer_token)
        employer_recs_after = request_json(employer_client, "get", "/api/recommendations/candidates", 200, token=employer_token)[1]
        expect(employer_recs_after.get("count", 0) > 10, "member employer recommendations should be unlimited", employer_recs_after.get("count"))
        passed.append("Employer Top 10 and VIP unlimited recommendations")

        request_json(employer_client, "post", f"/api/jobs/{job_id}/apply", 403, token=employer_token)
        apply_data = request_json(candidate_client, "post", f"/api/jobs/{job_id}/apply", 201, token=candidate_token)[1]
        expect(apply_data.get("message") == "Application submitted", "job application did not save", apply_data)
        duplicate_apply = request_json(candidate_client, "post", f"/api/jobs/{job_id}/apply", 200, token=candidate_token)[1]
        expect(duplicate_apply.get("message") == "Already applied", "duplicate application should be idempotent", duplicate_apply)
        authed_job = request_json(candidate_client, "get", f"/api/jobs/{job_id}", 200, token=candidate_token)[1]
        expect(authed_job.get("application"), "job detail should include candidate application status", authed_job)
        passed.append("Candidate apply job and duplicate application handling")

        recent_candidate_apps = request_json(candidate_client, "get", "/api/applications/candidate?limit=3", 200, token=candidate_token)[1]
        expect(recent_candidate_apps.get("count", 0) >= 1, "candidate recent applications missing", recent_candidate_apps)
        recent_employer_apps = request_json(employer_client, "get", "/api/applications/employer?limit=3", 200, token=employer_token)[1]
        expect(recent_employer_apps.get("count", 0) >= 1, "employer recent applicants missing", recent_employer_apps)
        passed.append("Recent applications and recent applicants")

        request_json(candidate_client, "post", "/api/jobs", 403, token=candidate_token, json=updated_payload)
        request_json(employer_client, "get", "/api/recommendations/jobs", 403, token=employer_token)
        passed.append("Role authorization for protected endpoints")

        request_json(employer_client, "delete", f"/api/jobs/{job_id}", 200, token=employer_token)
        deleted_job = request_json(public_client, "get", f"/api/jobs/{job_id}", 404)[1]
        expect(deleted_job.get("status") == "error", "job delete did not remove job", deleted_job)
        passed.append("Employer job delete")

        request_json(candidate_client, "post", "/api/logout", 200, token=candidate_token)
        revoked = request_json(candidate_client, "get", "/api/me", 200, token=candidate_token)[1]
        expect(revoked.get("loggedIn") is False, "logout should revoke bearer token", revoked)
        passed.append("Logout and token revocation")

        frontend_candidate_register = (ROOT / "frontend" / "candidate-register.html").read_text(encoding="utf-8")
        frontend_employer_register = (ROOT / "frontend" / "employer-register.html").read_text(encoding="utf-8")
        expect('window.location.href = "login.html"' in frontend_candidate_register, "candidate register page does not redirect to login")
        expect('window.location.href = "login.html"' in frontend_employer_register, "employer register page does not redirect to login")
        passed.append("Frontend sign up redirects to login")

        print("Full functionality test passed")
        print("=" * 72)
        for index, item in enumerate(passed, start=1):
            print(f"{index:02d}. PASS - {item}")
        print("=" * 72)
        print(f"Total passed: {len(passed)}")
    finally:
        cleanup_test_data()


if __name__ == "__main__":
    run_test()
