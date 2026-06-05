Setup Instructions

1. Clone the GitHub repository:
git clone https://github.com/CSIT-314-day-day-face/Intelligent-Talent-Matching-Platform.git
cd Intelligent-Talent-Matching-Platform

2. Create a Python virtual environment:
python -m venv .venv

3. Activate the virtual environment.

Windows:
.venv\Scripts\activate

macOS/Linux:
source .venv/bin/activate

4. Install dependencies:
pip install -r requirements.txt

5. Initialize the SQLite database:
python setup_db.py

6. Run the Flask backend:
python -m backend.api_server

7. Open the frontend:
Open `frontend/index.html` using VS Code Live Server or another static file server.

8. Run the full functionality test:
python test/test_backend_flow.py

Environment Configuration

Required environment:
- Python 3.12 or later
- pip
- SQLite
- VS Code Live Server or another static file server

Main project files:
- Backend entry point: backend/api_server.py
- Frontend entry point: frontend/index.html
- Dependency file: requirements.txt
- Database schema: database/schema.sql
- Database file: database/platform.db
- Database setup script: setup_db.py
- Full functionality test: test/test_backend_flow.py
- CI workflow: .github/workflows/ci.yml