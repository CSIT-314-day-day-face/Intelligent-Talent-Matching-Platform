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
    password_hash = generate_password_hash('password123')

    # 3. Insert Multiple Employers (For diverse job postings)
    employers = [
        (1, 'hr@uow.edu.au', password_hash, 'UOW Global Tech', 'Wollongong'),
        (2, 'recruitment@sydneytech.com', password_hash, 'Sydney Tech Solutions', 'Sydney'),
        (3, 'jobs@melbourneai.io', password_hash, 'Melbourne AI Lab', 'Melbourne')
    ]
    cursor.executemany("INSERT INTO Employers (id, email, password, company_name, location) VALUES (?, ?, ?, ?, ?)", employers)

    # 4. Insert 30 Jobs (To thoroughly test Top-10 limits and filtering)
    # Fields: employer_id, title, location, description, salary_range, job_type
    jobs = [
        # Python & AI focus
        (1, 'Python Developer', 'Wollongong', 'Looking for Python expert for AI projects.', '$90k', 'Full-time'),
        (3, 'AI Research Intern', 'Wollongong', 'Supporting AI model training and testing.', '$50k', 'Full-time'),
        (3, 'Machine Learning Engineer', 'Melbourne', 'Develop AI models and matching engines.', '$130k', 'Remote'),
        (3, 'NLP Specialist', 'Melbourne', 'Focus on natural language processing.', '$140k', 'Hybrid'),
        (1, 'Data Analyst', 'Wollongong', 'Analyze complex datasets using Python and SQL.', '$85k', 'Hybrid'),
        (1, 'Junior Python Coder', 'Wollongong', 'Entry level position for CS graduates.', '$65k', 'Full-time'),
        
        # Backend & Infrastructure
        (2, 'Backend Engineer', 'Sydney', 'Focus on Flask and SQL database management.', '$110k', 'Remote'),
        (2, 'Software Architect', 'Sydney', 'System design and backend infrastructure.', '$150k', 'On-site'),
        (2, 'Database Administrator', 'Sydney', 'Optimize PostgreSQL and SQLite performance.', '$105k', 'On-site'),
        (1, 'Big Data Specialist', 'Brisbane', 'Manage large scale database clusters.', '$120k', 'Hybrid'),
        (2, 'Cloud Engineer', 'Sydney', 'Deploying backend services to the cloud.', '$115k', 'Remote'),
        (3, 'DevOps Engineer', 'Melbourne', 'Automation of deployment pipelines.', '$110k', 'Remote'),
        (2, 'Lead Programmer', 'Sydney', 'Managing technical teams and architecture.', '$160k', 'On-site'),
        (1, 'Web API Developer', 'Remote', 'Design and implement RESTful APIs.', '$95k', 'Remote'),
        
        # Web & Frontend
        (2, 'Full Stack Developer', 'Sydney', 'Integration of Next.js and Flask backend.', '$100k', 'Hybrid'),
        (1, 'React Frontend Developer', 'Wollongong', 'Building responsive user interfaces.', '$90k', 'Remote'),
        (2, 'UI/UX Designer', 'Sydney', 'Focus on user experience and prototyping.', '$85k', 'On-site'),
        (3, 'JavaScript Engineer', 'Melbourne', 'Develop core web functionalities.', '$105k', 'Full-time'),
        
        # Management & Security
        (1, 'Project Manager', 'Wollongong', 'Oversee software development lifecycles.', '$120k', 'Hybrid'),
        (2, 'Security Consultant', 'Melbourne', 'Focus on authentication and data encryption.', '$125k', 'Hybrid'),
        (3, 'IT Director', 'Melbourne', 'Strategy and leadership for tech teams.', '$180k', 'On-site'),
        (1, 'Quality Assurance Lead', 'Remote', 'Lead testing and automation efforts.', '$110k', 'Remote'),

        # More Sydney Jobs (To test location filter)
        (2, 'Sydney Systems Analyst', 'Sydney', 'Business requirements analysis.', '$95k', 'Full-time'),
        (2, 'Junior Web Developer', 'Sydney', 'HTML, CSS, and basic JavaScript.', '$70k', 'Hybrid'),
        (2, 'Network Engineer', 'Sydney', 'Manage corporate network infrastructure.', '$100k', 'On-site'),
        (2, 'Cyber Security Analyst', 'Sydney', 'Monitor and respond to security threats.', '$115k', 'Remote'),
        
        # More Remote/Contract Jobs
        (3, 'Freelance Python Dev', 'Remote', 'Short term contract for script automation.', '$50/hr', 'Contract'),
        (1, 'Contract Data Scientist', 'Remote', '3-month contract for data modeling.', '$1000/day', 'Contract'),
        (2, 'Technical Writer', 'Remote', 'Documenting API endpoints and SDKs.', '$80k', 'Contract'),
        (3, 'Research Assistant', 'Melbourne', 'Academic research support.', '$60k', 'Part-time')
    ]

    cursor.executemany('''
        INSERT INTO Jobs (employer_id, title, location, description, salary_range, job_type) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', jobs)

    # 5. Insert Sample Candidates (To test "Employer find candidate" functionality)
    # Fields: email, password, full_name, work_experience, skills, preferred_mode, location, membership_status
    candidates = [
        ('alice@uow.edu.au', password_hash, 'Alice Chen', '3 years', 'Python, SQL, Flask', 'Remote', 'Wollongong', 1),
        ('bob@uow.edu.au', password_hash, 'Bob Smith', '1 year', 'Java, HTML, CSS', 'On-site', 'Sydney', 0),
        ('charlie@uow.edu.au', password_hash, 'Charlie Davis', '5 years', 'Python, AI, PyTorch', 'Hybrid', 'Melbourne', 1),
        ('david@uow.edu.au', password_hash, 'David Wilson', '2 years', 'JavaScript, React', 'Remote', 'Sydney', 0),
        ('eve@uow.edu.au', password_hash, 'Eve Brown', '4 years', 'SQL, Database Management', 'On-site', 'Brisbane', 0),
        ('frank@uow.edu.au', password_hash, 'Frank Miller', 'Junior', 'Python, C++', 'Hybrid', 'Wollongong', 0),
        ('grace@uow.edu.au', password_hash, 'Grace Lee', 'Senior', 'AWS, Cloud, DevOps', 'Remote', 'Sydney', 1),
        ('hank@uow.edu.au', password_hash, 'Hank Moore', '2 years', 'Testing, QA, Selenium', 'Hybrid', 'Melbourne', 0),
        ('ivy@uow.edu.au', password_hash, 'Ivy Taylor', '3 years', 'UI/UX, Figma, Design', 'On-site', 'Sydney', 0),
        ('jack@uow.edu.au', password_hash, 'Jack Anderson', '6 years', 'Software Architecture', 'Remote', 'Wollongong', 1)
    ]

    cursor.executemany('''
        INSERT INTO Candidates (email, password, full_name, work_experience, skills, preferred_mode, location, membership_status) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', candidates)

    conn.commit()
    conn.close()
    print("Database reset successfully.")
    print("Seeded: 3 Employers, 30 Jobs, 10 Candidates.")

if __name__ == "__main__":
    setup_database()