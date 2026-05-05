import sqlite3
import os

# 定義資料庫路徑
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'platform.db')

def test_insertion():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. 新增一名求職者 (包含 Week 8 新欄位與會員狀態)
        # 欄位：email, password, name, exp, skills, mode, location, membership
        cursor.execute('''
            INSERT INTO Candidates (email, password, full_name, work_experience, skills, preferred_mode, location, membership_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', ('jeff@example.com', 'hashed_pass_123', 'Jeff Tsai', '3 years in Python development', 'Python, SQL, JavaScript', 'Remote', 'Sydney', 1)) 
        # membership_status 1 代表會員，應可獲得無限推薦

        # 2. 新增一名雇主
        cursor.execute('''
            INSERT INTO Employers (company_name, email, password, location, membership_status)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Tech Corp', 'hr@techcorp.com', 'company_pass', 'Wollongong', 0))

        # 獲取剛才新增的雇主 ID
        employer_id = cursor.lastrowid

        # 3. 為該雇主新增一個職缺
        cursor.execute('''
            INSERT INTO Jobs (employer_id, title, description, location, salary_range, job_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (employer_id, 'Junior Developer', 'Looking for a coder who knows Python', 'Sydney', '70k-90k', 'Full-time'))

        conn.commit()
        print("✅ 測試資料新增成功！")

    except sqlite3.Error as e:
        print(f"❌ 發生錯誤: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    test_insertion()