CREATE TABLE IF NOT EXISTS Candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,           
    full_name TEXT DEFAULT '',        
    work_experience TEXT,
    skills TEXT,
    preferred_mode TEXT,              
    location TEXT,
    membership_status INTEGER DEFAULT 0 
);

CREATE TABLE IF NOT EXISTS Employers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    company_name TEXT DEFAULT '',     
    location TEXT,
    membership_status INTEGER DEFAULT 0
);


CREATE TABLE IF NOT EXISTS Jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INTEGER NOT NULL,      
    title TEXT NOT NULL,               
    description TEXT,
    location TEXT,
    salary_range TEXT,                 
    job_type TEXT,                     
    FOREIGN KEY (employer_id) REFERENCES Employers(id) ON DELETE CASCADE
);