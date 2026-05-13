1. Environment Setup:
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\\Scripts\\activate   # Windows

2. Install Dependencies:
pip install -r requirements.txt

3. Initialize Database:
python3 setup_db.py

4. Running the Backend:
python3 -m backend.app

5. System Verification:
python3 test/test_backend_flow.py
