1. Environment Setup:
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\\Scripts\\activate   # Windows

2. Install Dependencies:
pip install -r requirements.txt

3. Initialize Database:
python setup_db.py

4. Running the Backend:
python -m backend.api_server

5. System Verification:
python test/test_backend_flow.py

Company
Email: test.company@example.com
Password: 00000000

Candidate
Email: test.candidate@example.com
Password: 00000000