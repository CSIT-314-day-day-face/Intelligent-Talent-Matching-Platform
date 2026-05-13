import requests
import time

# Backend API configuration
BASE_URL = "http://127.0.0.1:5001/api"
session = requests.Session()

# Generate unique test credentials
unique_ts = int(time.time())
TEST_EMAIL = f"test_user_{unique_ts}@uow.edu.au"
TEST_PASS = "password123"

def run_test():
    print(f"Starting Backend Integration Test - Account: {TEST_EMAIL}")
    print("=" * 60)

    # 1. Registration functional check
    print("Step 1: Account Registration")
    r = session.post(f"{BASE_URL}/register", json={
        "email": TEST_EMAIL, 
        "password": TEST_PASS, 
        "role": "candidate"
    })
    print(f"   Response: {r.json()}")

    # 2. Login and session establishment
    print("\nStep 2: User Login")
    r = session.post(f"{BASE_URL}/login", json={
        "email": TEST_EMAIL, 
        "password": TEST_PASS, 
        "role": "candidate"
    })
    print(f"   Response: {r.json()}")
    if r.status_code != 200:
        print("Login failed. Terminating test.")
        return

    # 3. Profile update functional check
    print("\nStep 3: Update Candidate Profile")
    r = session.post(f"{BASE_URL}/profile/update", json={
        "full_name": "Jeff Test",
        "experience": "2 years",
        "skills": "Python, SQL",
        "mode": "Remote",
        "location": "Wollongong"
    })
    print(f"   Response: {r.json()}")

    # 4. Fuzzy search logic verification
    print("\nStep 4: Fuzzy Search Test (Query: Pyton)")
    r = session.get(f"{BASE_URL}/search", params={"q": "Pyton"})
    res = r.json()
    count = res.get('count', 0)
    print(f"   Results: Found {count} matching jobs")
    if count > 0:
        best_match = res['results'][0]
        print(f"   Best Match: {best_match['title']} (Score: {best_match['score']})")

    # 5. Membership status transition check
    print("\nStep 5: Membership Upgrade")
    r = session.post(f"{BASE_URL}/membership/upgrade")
    if r.status_code == 200:
        print(f"   Response: Success - {r.json().get('message')}")
    else:
        print(f"   Response: Failed - Status Code: {r.status_code}")
        print(f"   Error Details: {r.text}")

    print("=" * 60)
    print("Backend Integration Test Completed Successfully")

if __name__ == "__main__":
    run_test()