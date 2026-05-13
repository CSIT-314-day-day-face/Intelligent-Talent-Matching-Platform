import sqlite3
import os
from werkzeug.security import generate_password_hash

def setup_database():
    # 1. Define paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'database', 'platform.db')
    schema_path = os.path.join(current_dir, 'database', 'schema.sql')

    # Ensure database directory exists
    if not os.path.exists('database'):
        os.makedirs('database')

    # 2. Reset Database (Delete and Recreate)
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    
    cursor = conn.cursor()

    # 3. Insert Seed Data - Employer
    hashed_pass = generate_password_hash('password123')
    cursor.execute("INSERT INTO Employers (id, email, password, company_name, location) VALUES (1, 'hr@uow.edu.au', ?, 'UOW Global Tech', 'Wollongong')", (hashed_pass,))

    # 4. Insert Seed Data - 15 Jobs (To test the Top-10 limit)
    jobs = [
        (1, 'Python Developer', 'Wollongong', 'Looking for a Python expert for AI projects.', '$90k', 'Full-time'),
        (1, 'Backend Engineer', 'Sydney', 'Focus on Flask and SQL database management.', '$110k', 'Remote'),
        (1, 'Data Analyst', 'Wollongong', 'Analyze complex datasets using Python and SQL.', '$85k', 'Hybrid'),
        (1, 'Machine Learning Engineer', 'Melbourne', 'Develop AI models and matching engines.', '$130k', 'Remote'),
        (1, 'Software Architect', 'Sydney', 'System design and backend infrastructure.', '$150k', 'On-site'),
        (1, 'Junior Python Coder', 'Wollongong', 'Entry level position for CS graduates.', '$65k', 'Full-time'),
        (1, 'Big Data Specialist', 'Brisbane', 'Manage large scale database clusters.', '$120k', 'Hybrid'),
        (1, 'Web API Developer', 'Remote', 'Design and implement RESTful APIs.', '$95k', 'Remote'),
        (1, 'Database Administrator', 'Sydney', 'Optimize PostgreSQL and SQLite performance.', '$105k', 'On-site'),
        (1, 'Security Consultant', 'Melbourne', 'Focus on authentication and data encryption.', '$125k', 'Hybrid'),
        (1, 'Cloud Engineer', 'Sydney', 'Deploying backend services to the cloud.', '$115k', 'Remote'),
        (1, 'AI Research Intern', 'Wollongong', 'Supporting AI model training and testing.', '$50k', 'Full-time'),
        (1, 'Full Stack Developer', 'Sydney', 'Integration of Next.js and Flask backend.', '$100k', 'Hybrid'),
        (1, 'DevOps Engineer', 'Melbourne', 'Automation of deployment pipelines.', '$110k', 'Remote'),
        (1, 'Lead Programmer', 'Sydney', 'Managing technical teams and architecture.', '$160k', 'On-site')
    ]

    cursor.executemany('''
        INSERT INTO Jobs (employer_id, title, location, description, salary_range, job_type) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', jobs)

    conn.commit()
    conn.close()
    print("Database reset and 15 test jobs seeded successfully.")

if __name__ == "__main__":
    setup_database()