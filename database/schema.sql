-- 1. 求職者資料表 (Candidates)
CREATE TABLE IF NOT EXISTS Candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,           -- 存儲經過 Hashing 的密碼
    full_name TEXT DEFAULT '',        -- 移除 NOT NULL，註冊後再由 Profile 頁面更新
    work_experience TEXT,
    skills TEXT,
    preferred_mode TEXT,              -- 儲存值：'Remote', 'On-site', 'Hybrid'
    location TEXT,
    membership_status INTEGER DEFAULT 0 -- 0: 一般, 1: 付費會員
);

-- 2. 雇主資料表 (Employers)
CREATE TABLE IF NOT EXISTS Employers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    company_name TEXT DEFAULT '',     -- 移除 NOT NULL
    location TEXT,
    membership_status INTEGER DEFAULT 0
);

-- 3. 職缺資料表 (Jobs)
CREATE TABLE IF NOT EXISTS Jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INTEGER NOT NULL,      -- 關聯到 Employers.id
    title TEXT NOT NULL,               -- 職稱必填
    description TEXT,
    location TEXT,
    salary_range TEXT,                 -- 儲存字串如 "$80,000 - $100,000"
    job_type TEXT,                     -- 儲存值：'Full-time', 'Part-time', 'Contract'
    FOREIGN KEY (employer_id) REFERENCES Employers(id) ON DELETE CASCADE
);