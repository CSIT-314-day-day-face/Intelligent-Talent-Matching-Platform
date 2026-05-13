from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os

# Import business logic modules
from backend.auth import verify_login, register_user
from backend.search_logic import fuzzy_search_jobs
from backend.profile import update_candidate_profile
from backend.job_management import create_job, get_employer_jobs
from backend.membership import upgrade_membership
from backend.db_utils import get_db_connection

app = Flask(__name__)
# Secret key for session management
app.secret_key = 'csit314_secret_key_2026'
# Enable CORS for frontend integration
CORS(app, supports_credentials=True)

# Authentication Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    success = register_user(data['email'], data['password'], data['role'])
    if success:
        return jsonify({"status": "success", "message": "Registration successful"})
    return jsonify({"status": "error", "message": "Registration failed"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    user = verify_login(data['email'], data['password'], data['role'])
    if user:
        # Session storage for authentication persistence
        session['user_id'] = user['id']
        session['role'] = data['role']
        session['membership'] = user['membership_status']
        return jsonify({
            "status": "success", 
            "role": data['role'], 
            "membership": user['membership_status']
        })
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out"})

# Search Routes (Supports Keywords + Filters)
@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    location = request.args.get('location', None)
    job_type = request.args.get('job_type', None)
    
    current_membership = session.get('membership', 0)
    results = fuzzy_search_jobs(query, location, job_type, current_membership)
    return jsonify({"results": results, "count": len(results)})

# Job Details Route (Requirement Traceability)
@app.route('/api/jobs/<int:job_id>', methods=['GET'])
def get_job_detail(job_id):
    conn = get_db_connection()
    job = conn.execute("SELECT * FROM Jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    if job:
        return jsonify(dict(job))
    return jsonify({"status": "error", "message": "Job not found"}), 404

# Job Management Routes
@app.route('/api/jobs', methods=['POST'])
def post_job():
    if session.get('role') != 'employer':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    data = request.json
    success = create_job(
        session['user_id'], 
        data.get('title'), 
        data.get('location'), 
        data.get('description'), 
        data.get('salary'), 
        data.get('job_type')
    )
    return jsonify({"status": "success"}) if success else jsonify({"status": "error"}), 500

@app.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    if session.get('role') != 'employer':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    conn = get_db_connection()
    conn.execute("DELETE FROM Jobs WHERE id = ? AND employer_id = ?", (job_id, session['user_id']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Job deleted"})

# Profile Routes
@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    # Verify user session and role
    if not session.get('user_id') or session.get('role') != 'candidate':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    data = request.json
    success = update_candidate_profile(
        session['user_id'], 
        data.get('full_name'), 
        data.get('experience'), 
        data.get('skills'), 
        data.get('mode'), 
        data.get('location')
    )
    
    # Explicit status return to avoid tuple packaging error
    if success:
        return jsonify({"status": "success"})
    else:
        return jsonify({"status": "error", "message": "Database update failed"}), 500

# Membership Routes
@app.route('/api/membership/upgrade', methods=['POST'])
def upgrade():
    if not session.get('user_id'):
        return jsonify({"status": "error", "message": "Not logged in"}), 401
    
    if upgrade_membership(session['user_id'], session['role']):
        session['membership'] = 1
        return jsonify({"status": "success", "message": "Membership upgraded"})
    return jsonify({"status": "error"}), 500

if __name__ == '__main__':
    # Run on port 5001 with debug mode enabled for development
    app.run(host='0.0.0.0', port=5001, debug=True)