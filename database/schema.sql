-- Candidates
CREATE TABLE IF NOT EXISTS Candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT NOT NULL,
    work_experience TEXT,
    skills TEXT,
    preferred_mode TEXT, -- Remote, On-site, Hybrid
    location TEXT,
    membership_status INTEGER DEFAULT 0 -- 0: Non-member, 1: Member
);

-- Employers
CREATE TABLE IF NOT EXISTS Employers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    location TEXT,
    membership_status INTEGER DEFAULT 0
);

-- Jobs
CREATE TABLE IF NOT EXISTS Jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INTEGER,
    title TEXT NOT NULL,
    description TEXT,
    location TEXT,
    salary_range TEXT,
    job_type TEXT,
    FOREIGN KEY (employer_id) REFERENCES Employers(id)
);