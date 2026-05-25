CREATE TABLE IF NOT EXISTS Candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT DEFAULT '',
    contact_info TEXT DEFAULT '',
    education TEXT DEFAULT '',
    major TEXT DEFAULT '',
    years_experience TEXT DEFAULT '',
    summary TEXT DEFAULT '',
    work_experience TEXT DEFAULT '',
    skills TEXT DEFAULT '',
    preferred_mode TEXT DEFAULT '',
    preferred_location TEXT DEFAULT '',
    location TEXT DEFAULT '',
    membership_status INTEGER DEFAULT 0 
);

CREATE TABLE IF NOT EXISTS Employers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    company_name TEXT DEFAULT '',
    company_info TEXT DEFAULT '',
    contact_info TEXT DEFAULT '',
    location TEXT DEFAULT '',
    membership_status INTEGER DEFAULT 0
);


CREATE TABLE IF NOT EXISTS Jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    company_info TEXT DEFAULT '',
    description TEXT DEFAULT '',
    required_education TEXT DEFAULT '',
    required_skills TEXT DEFAULT '',
    years_experience TEXT DEFAULT '',
    work_mode TEXT DEFAULT '',
    location TEXT DEFAULT '',
    salary_range TEXT DEFAULT '',
    job_type TEXT DEFAULT '',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employer_id) REFERENCES Employers(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id INTEGER NOT NULL,
    job_id INTEGER NOT NULL,
    status TEXT DEFAULT 'Applied',
    applied_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (candidate_id) REFERENCES Candidates(id) ON DELETE CASCADE,
    FOREIGN KEY (job_id) REFERENCES Jobs(id) ON DELETE CASCADE,
    UNIQUE(candidate_id, job_id)
);

CREATE TABLE IF NOT EXISTS AuthTokenRevocations (
    token TEXT PRIMARY KEY,
    revoked_at TEXT DEFAULT CURRENT_TIMESTAMP
);
