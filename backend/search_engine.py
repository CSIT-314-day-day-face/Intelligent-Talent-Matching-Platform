import sqlite3
import os

# 定義資料庫路徑
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, 'platform.db')

def search_jobs(keyword=None, location=None, work_mode=None):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 基礎 SQL 指令
    query = "SELECT * FROM Jobs WHERE 1=1"
    params = []

    # 1. 處理關鍵字 (搜尋職稱或描述)
    if keyword:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f'%{keyword}%', f'%{keyword}%'])

    # 2. 處理過濾器 (地點與工作模式)
    if location:
        query += " AND location = ?"
        params.append(location)
    
    if work_mode:
        # 注意：工作模式在 Candidates 表是 preferred_mode，在 Jobs 表需對應設計
        query += " AND job_type = ?" 
        params.append(work_mode)

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results

# 測試：搜尋在 Sydney 的 Python 職缺
print("搜尋結果：", search_jobs(keyword="Python", location="Sydney"))

def get_recommendations(user_id, is_candidate=True):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. 先確認該使用者的會員狀態
    table = "Candidates" if is_candidate else "Employers"
    cursor.execute(f"SELECT membership_status FROM {table} WHERE id = ?", (user_id,))
    is_member = cursor.fetchone()[0]

    # 2. 執行媒合演算法 (此處簡化為 SQL 查詢)
    query = "SELECT * FROM Jobs" # 實際應為媒合邏輯
    
    # 3. 根據會員身分決定 LIMIT
    if not is_member:
        query += " LIMIT 10" # 非會員僅限 Top 10
    
    cursor.execute(query)
    recommendations = cursor.fetchall()
    conn.close()
    return recommendations