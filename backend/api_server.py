from flask import Flask, request, jsonify, session
from flask_cors import CORS
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
import os

from backend.auth import verify_login, register_user
from backend.search import fuzzy_search_jobs, fuzzy_search_candidates
from backend.profiles import (
    get_candidate_profile,
    get_employer_profile,
    update_candidate_profile,
    update_employer_profile,
)
from backend.jobs import (
    create_job,
    delete_job_for_employer,
    get_all_jobs,
    get_employer_jobs,
    get_job,
    update_job,
)
from backend.recommendations import recommend_jobs, recommend_candidates
from backend.membership import upgrade_membership, toggle_membership
from backend.applications import (
    apply_for_job,
    get_application_for_candidate,
    get_recent_applications_for_candidate,
    get_recent_applicants_for_employer,
)
from backend.database_connection import get_db_connection

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'csit314_secret_key_2026')
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
CORS(
    app,
    supports_credentials=True,
    origins=["http://127.0.0.1:5500", "http://localhost:5500"]
)

auth_serializer = URLSafeTimedSerializer(app.secret_key)
AUTH_TOKEN_SALT = "job-radar-auth"
AUTH_TOKEN_MAX_AGE = 60 * 60 * 24 * 7

def _ensure_auth_tables():
    conn = get_db_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS AuthTokenRevocations (
            token TEXT PRIMARY KEY,
            revoked_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()

_ensure_auth_tables()

def _table_for_role(role):
    if role == "candidate":
        return "Candidates"
    if role == "employer":
        return "Employers"
    return None

def _make_auth_token(user_id, role, email):
    return auth_serializer.dumps(
        {"user_id": user_id, "role": role, "email": email},
        salt=AUTH_TOKEN_SALT,
    )

def _extract_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return ""
    return auth_header.replace("Bearer ", "", 1).strip()

def _is_token_revoked(token):
    if not token:
        return False
    conn = get_db_connection()
    row = conn.execute(
        "SELECT token FROM AuthTokenRevocations WHERE token = ?",
        (token,),
    ).fetchone()
    conn.close()
    return row is not None

def _revoke_token(token):
    if not token:
        return
    conn = get_db_connection()
    conn.execute(
        "INSERT OR IGNORE INTO AuthTokenRevocations (token) VALUES (?)",
        (token,),
    )
    conn.commit()
    conn.close()

def _display_name_for_user(user, role):
    if role == "candidate":
        return user.get("full_name") or user.get("contact_info") or user.get("email")

    contact_info = user.get("contact_info") or ""
    if contact_info and "@" not in contact_info:
        return contact_info

    return user.get("company_name") or user.get("email")

def _restore_session_from_token():
    if session.get('user_id'):
        return True

    token = _extract_bearer_token()
    if not token or _is_token_revoked(token):
        return False

    try:
        token_data = auth_serializer.loads(
            token,
            salt=AUTH_TOKEN_SALT,
            max_age=AUTH_TOKEN_MAX_AGE,
        )
    except (BadSignature, SignatureExpired):
        return False

    role = token_data.get("role")
    table = _table_for_role(role)
    if not table:
        return False

    conn = get_db_connection()
    user = conn.execute(
        f"SELECT id, email, membership_status FROM {table} WHERE id = ? AND email = ?",
        (token_data.get("user_id"), token_data.get("email")),
    ).fetchone()
    conn.close()

    if not user:
        return False

    session['user_id'] = user['id']
    session['role'] = role
    session['membership'] = user['membership_status']
    session['email'] = user['email']
    return True

def _require_login(role=None):
    _restore_session_from_token()
    if not session.get('user_id'):
        return jsonify({"status": "error", "message": "Not logged in"}), 401
    if role and session.get('role') != role:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    return None

def _missing_required(data, fields):
    missing = []
    for field in fields:
        value = data.get(field)
        if isinstance(value, list):
            has_value = any(str(item).strip() for item in value)
        else:
            has_value = bool(str(value or "").strip())
        if not has_value:
            missing.append(field)
    return missing

def _normalize_job_payload(data):
    payload = dict(data or {})
    payload["salary"] = payload.get("salary") or payload.get("salary_range", "")
    payload["work_mode"] = payload.get("work_mode") or payload.get("mode", "")
    payload["job_type"] = payload.get("job_type") or ""
    payload["years_experience"] = payload.get("years_experience") or payload.get("experience", "")
    return payload

def _validate_job_payload(data):
    payload = _normalize_job_payload(data)
    missing = _missing_required(
        payload,
        [
            "title",
            "location",
            "description",
            "salary",
            "job_type",
            "required_education",
            "required_skills",
            "years_experience",
            "work_mode",
        ],
    )
    if missing:
        return payload, jsonify({
            "status": "error",
            "message": "Missing required job fields",
            "missing": missing
        }), 400
    return payload, None, None

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json(silent=True) or {}
    if data.get('role') not in ('candidate', 'employer'):
        return jsonify({"status": "error", "message": "Invalid role"}), 400
    if not data.get('email') or not data.get('password'):
        return jsonify({"status": "error", "message": "Email and password are required"}), 400

    success = register_user(
        data['email'],
        data['password'],
        data['role'],
        full_name=data.get('full_name', data.get('name', '')),
        company_name=data.get('company_name', ''),
        contact_info=data.get('contact_info', data.get('email', '')),
        location=data.get('location', ''),
    )
    if success:
        return jsonify({"status": "success", "message": "Registration successful"})
    return jsonify({"status": "error", "message": "Registration failed"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json(silent=True) or {}
    missing = _missing_required(data, ["email", "password", "role"])
    if missing:
        return jsonify({
            "status": "error",
            "message": "Email, password, and role are required",
            "missing": missing
        }), 400
    if data.get('role') not in ('candidate', 'employer'):
        return jsonify({"status": "error", "message": "Invalid role"}), 400

    user = verify_login(data['email'], data['password'], data['role'])
    if user:
        session['user_id'] = user['id']
        session['role'] = data['role']
        session['membership'] = user['membership_status']
        session['email'] = user['email']
        auth_token = _make_auth_token(user['id'], data['role'], user['email'])
        return jsonify({
            "status": "success",
            "role": data['role'],
            "membership": user['membership_status'],
            "email": user['email'],
            "display_name": _display_name_for_user(user, data['role']),
            "auth_token": auth_token
        })
    return jsonify({"status": "error", "message": "Invalid email or password."}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    _revoke_token(_extract_bearer_token())
    session.clear()
    return jsonify({"status": "success", "message": "Logged out"})
@app.route('/api/me', methods=['GET'])
def get_current_user():
    _restore_session_from_token()
    if not session.get('user_id'):
        return jsonify({
            "loggedIn": False
        })
    return jsonify({
        "loggedIn": True,
        "user_id": session.get('user_id'),
        "role": session.get('role'),
        "membership": session.get('membership'),
        "email": session.get('email')
    })

@app.route('/api/profile', methods=['GET'])
def get_profile():
    auth_error = _require_login()
    if auth_error:
        return auth_error

    if session.get('role') == 'candidate':
        profile = get_candidate_profile(session['user_id'])
    else:
        profile = get_employer_profile(session['user_id'])

    return jsonify({"status": "success", "role": session.get('role'), "profile": profile})

@app.route('/api/profile', methods=['PUT', 'POST'])
def save_profile():
    auth_error = _require_login()
    if auth_error:
        return auth_error

    data = request.json or {}
    if session.get('role') == 'candidate':
        success = update_candidate_profile(session['user_id'], **data)
    else:
        success = update_employer_profile(session['user_id'], **data)

    if success:
        return jsonify({"status": "success", "message": "Profile updated"})
    return jsonify({"status": "error", "message": "Profile update failed"}), 500

@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    location = request.args.get('location', None)
    job_type = request.args.get('job_type', None)
    work_mode = request.args.get('work_mode', None) or request.args.get('mode', None)
    salary = request.args.get('salary', None)
    education = request.args.get('education', None)
    skill = request.args.get('skill', None)

    if job_type in ("Remote", "Hybrid", "On-site") and not work_mode:
        work_mode = job_type
        job_type = None

    results = fuzzy_search_jobs(
        query,
        location=location,
        job_type=job_type,
        work_mode=work_mode,
        salary=salary,
        education=education,
        skill=skill,
    )
    return jsonify({"results": results, "count": len(results)})

@app.route('/api/candidates/search', methods=['GET'])
def search_candidates():
    auth_error = _require_login('employer')
    if auth_error:
        return auth_error

    results = fuzzy_search_candidates(
        request.args.get('q', ''),
        location=request.args.get('location', None),
        work_mode=request.args.get('work_mode', None) or request.args.get('mode', None),
        education=request.args.get('education', None),
        skill=request.args.get('skill', None),
        experience=request.args.get('experience', None),
    )
    return jsonify({"results": results, "count": len(results)})

@app.route('/api/candidates', methods=['GET'])
def list_candidates():
    auth_error = _require_login('employer')
    if auth_error:
        return auth_error
    results = fuzzy_search_candidates("")
    return jsonify({"results": results, "count": len(results)})

@app.route('/api/candidates/<int:candidate_id>', methods=['GET'])
def get_candidate_detail(candidate_id):
    auth_error = _require_login()
    if auth_error:
        return auth_error

    if session.get('role') == 'candidate' and session.get('user_id') != candidate_id:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    profile = get_candidate_profile(candidate_id)
    if profile:
        return jsonify(profile)
    return jsonify({"status": "error", "message": "Candidate not found"}), 404

@app.route('/api/recommendations/jobs', methods=['GET'])
def recommended_jobs():
    auth_error = _require_login('candidate')
    if auth_error:
        return auth_error
    results = recommend_jobs(session['user_id'], session.get('membership', 0))
    return jsonify({"results": results, "count": len(results)})

@app.route('/api/recommendations/candidates', methods=['GET'])
def recommended_candidates_for_employer():
    auth_error = _require_login('employer')
    if auth_error:
        return auth_error

    job_id = request.args.get('job_id', type=int)
    if not job_id:
        jobs = get_employer_jobs(session['user_id'])
        if not jobs:
            fallback = fuzzy_search_candidates("")
            limit = None if int(session.get('membership', 0) or 0) == 1 else 10
            results = fallback if limit is None else fallback[:limit]
            for candidate in results:
                candidate["score"] = 0
                candidate["match_quality"] = "Create a job post to calculate match"
            return jsonify({
                "results": results,
                "count": len(results),
                "message": "No posted job; showing candidate list without match scoring"
            })
        job_id = jobs[0]['id']

    results = recommend_candidates(job_id, session.get('membership', 0))
    return jsonify({"results": results, "count": len(results), "job_id": job_id})

@app.route('/api/jobs', methods=['GET'])
def list_jobs():
    limit = request.args.get('limit', type=int)
    jobs = get_all_jobs(limit)
    return jsonify({"results": jobs, "count": len(jobs)})

@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job_detail(job_id):
    job = get_job(job_id)
    if job:
        _restore_session_from_token()
        if session.get('role') == 'candidate':
            job['application'] = get_application_for_candidate(session['user_id'], job_id)
        return jsonify(job)
    return jsonify({"status": "error", "message": "Job not found"}), 404

@app.route('/api/jobs/<int:job_id>/apply', methods=['POST'])
def apply_to_job(job_id):
    auth_error = _require_login('candidate')
    if auth_error:
        return auth_error

    success, message = apply_for_job(session['user_id'], job_id)
    if success:
        status_code = 200 if message == "Already applied" else 201
        return jsonify({"status": "success", "message": message}), status_code
    return jsonify({"status": "error", "message": message}), 404 if message == "Job not found" else 500

@app.route('/api/jobs', methods=['POST'])
def post_job():
    auth_error = _require_login('employer')
    if auth_error:
        return auth_error

    data, validation_error, status_code = _validate_job_payload(request.json or {})
    if validation_error:
        return validation_error, status_code

    success = create_job(
        session['user_id'],
        data.get('title'),
        data.get('location'),
        data.get('description'),
        data.get('salary'),
        data.get('job_type', data.get('work_mode')),
        company_info=data.get('company_info', ''),
        required_education=data.get('required_education', ''),
        required_skills=data.get('required_skills', ''),
        years_experience=data.get('years_experience', data.get('experience', '')),
        work_mode=data.get('work_mode', data.get('mode', ''))
    )
    if success:
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Job creation failed"}), 500

@app.route('/api/employer/jobs', methods=['GET'])
def employer_jobs():
    auth_error = _require_login('employer')
    if auth_error:
        return auth_error
    jobs = get_employer_jobs(session['user_id'])
    return jsonify({"results": jobs, "count": len(jobs)})

@app.route('/api/jobs/<int:job_id>', methods=['PUT'])
def edit_job(job_id):
    auth_error = _require_login('employer')
    if auth_error:
        return auth_error

    data, validation_error, status_code = _validate_job_payload(request.json or {})
    if validation_error:
        return validation_error, status_code

    editable_data = {
        key: data.get(key)
        for key in [
            "title",
            "company_info",
            "description",
            "required_education",
            "required_skills",
            "years_experience",
            "work_mode",
            "location",
            "salary",
            "salary_range",
            "job_type",
        ]
    }
    success = update_job(job_id, session['user_id'], **editable_data)
    if success:
        return jsonify({"status": "success", "message": "Job updated"})
    return jsonify({"status": "error", "message": "Job not found or unauthorized"}), 404

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    auth_error = _require_login('employer')
    if auth_error:
        return auth_error

    if delete_job_for_employer(job_id, session['user_id']):
        return jsonify({"status": "success", "message": "Job deleted"})
    return jsonify({"status": "error", "message": "Job not found or unauthorized"}), 404

@app.route('/api/jobs/<int:job_id>/recommendations', methods=['GET'])
def candidates_for_job(job_id):
    auth_error = _require_login('employer')
    if auth_error:
        return auth_error
    results = recommend_candidates(job_id, session.get('membership', 0))
    return jsonify({"results": results, "count": len(results), "job_id": job_id})

@app.route('/api/applications/candidate', methods=['GET'])
def recent_candidate_applications():
    auth_error = _require_login('candidate')
    if auth_error:
        return auth_error

    limit = request.args.get('limit', default=3, type=int)
    results = get_recent_applications_for_candidate(session['user_id'], limit)
    return jsonify({"results": results, "count": len(results)})

@app.route('/api/applications/employer', methods=['GET'])
def recent_employer_applicants():
    auth_error = _require_login('employer')
    if auth_error:
        return auth_error

    limit = request.args.get('limit', default=3, type=int)
    results = get_recent_applicants_for_employer(session['user_id'], limit)
    return jsonify({"results": results, "count": len(results)})

@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    auth_error = _require_login('candidate')
    if auth_error:
        return auth_error

    data = request.json or {}
    success = update_candidate_profile(session['user_id'], **data)

    if success:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Database update failed"}), 500

@app.route('/api/membership/upgrade', methods=['POST'])
def upgrade():
    _restore_session_from_token()
    if not session.get('user_id'):
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    if upgrade_membership(session['user_id'], session['role']):
        session['membership'] = 1
        auth_token = _make_auth_token(
            session['user_id'],
            session['role'],
            session.get('email', ''),
        )
        return jsonify({
            "status": "success",
            "message": "Membership upgraded",
            "membership": 1,
            "auth_token": auth_token
        })
    return jsonify({"status": "error"}), 500

@app.route('/api/membership/toggle', methods=['POST'])
def toggle_membership_status():
    _restore_session_from_token()
    if not session.get('user_id'):
        return jsonify({"status": "error", "message": "Not logged in"}), 401

    new_status = toggle_membership(session['user_id'], session['role'])
    if new_status is None:
        return jsonify({"status": "error", "message": "Membership update failed"}), 500

    session['membership'] = new_status
    auth_token = _make_auth_token(
        session['user_id'],
        session['role'],
        session.get('email', '')
    )
    return jsonify({
        "status": "success",
        "message": "Membership updated",
        "membership": new_status,
        "auth_token": auth_token
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
