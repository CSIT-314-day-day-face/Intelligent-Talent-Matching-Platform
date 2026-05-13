from flask import Flask, request, jsonify, session
from flask_cors import CORS
import os

from backend.auth import verify_login, register_user
from backend.search_logic import fuzzy_search_jobs
from backend.profile import update_candidate_profile
from backend.job_management import create_job, get_employer_jobs
from backend.matching_engine import recommend_candidates
from backend.membership import upgrade_membership

app = Flask(__name__)
app.secret_key = 'csit314_secret_key_2026'
CORS(app, supports_credentials=True)

# Auth Routes
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
        session['user_id'] = user['id']
        session['role'] = data['role']
        session['membership'] = user['membership_status']
        return jsonify({"status": "success", "role": data['role'], "membership": user['membership_status']})
    return jsonify({"status": "error", "message": "Invalid credentials"}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out"})

# Search Routes
@app.route('/api/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    current_membership = session.get('membership', 0)
    results = fuzzy_search_jobs(query, membership_status=current_membership)
    return jsonify({"results": results, "count": len(results)})

# Profile Routes
@app.route('/api/profile/update', methods=['POST'])
def update_profile():
    if session.get('role') != 'candidate':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    data = request.json
    success = update_candidate_profile(session['user_id'], data.get('full_name'), data.get('experience'), data.get('skills'), data.get('mode'), data.get('location'))
    return jsonify({"status": "success"}) if success else jsonify({"status": "error"}), 500

# Job Management Routes
@app.route('/api/jobs', methods=['POST'])
def post_job():
    if session.get('role') != 'employer':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    data = request.json
    success = create_job(session['user_id'], data.get('title'), data.get('location'), data.get('description'), data.get('salary'), data.get('job_type'))
    return jsonify({"status": "success"}) if success else jsonify({"status": "error"}), 500

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
    app.run(host='0.0.0.0', port=5001, debug=True)