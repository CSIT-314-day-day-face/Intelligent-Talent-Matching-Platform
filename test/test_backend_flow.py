import requests
import time

BASE_URL = "http://127.0.0.1:5001/api"
session = requests.Session()
unique_ts = int(time.time())
TEST_EMAIL = f"test_user_{unique_ts}@uow.edu.au"
TEST_PASS = "password123"

def run_test():
    print(f"Starting Robust Integration Test - Account: {TEST_EMAIL}")
    print("=" * 60)

    # 1. Registration
    print("Step 1: Account Registration")
    r = session.post(f"{BASE_URL}/register", json={"email": TEST_EMAIL, "password": TEST_PASS, "role": "candidate"})
    print(f"   Response: {r.json()} (Status: {r.status_code})")

    # 2. Login
    print("\nStep 2: User Login")
    r = session.post(f"{BASE_URL}/login", json={"email": TEST_EMAIL, "password": TEST_PASS, "role": "candidate"})
    print(f"   Response: {r.json()} (Status: {r.status_code})")
    if r.status_code != 200: return

    # 3. Profile Update (Checking for 500 errors)
    print("\nStep 3: Update Profile")
    r = session.post(f"{BASE_URL}/profile/update", json={
        "full_name": "Jeff Test", "experience": "2 years", "skills": "Python", "mode": "Remote", "location": "Sydney"
    })
    if r.status_code == 200:
        print(f"   Response: Success")
    else:
        print(f"   Response: FAILED (Status: {r.status_code}) - Check Flask console for details")

    # 4. Advanced Search (Using Backend + Sydney for guaranteed results)
    print("\nStep 4: Search Test (Query: Backend, Location: Sydney)")
    r = session.get(f"{BASE_URL}/search", params={"q": "Backend", "location": "Sydney"})
    res = r.json()
    count = res.get('count', 0)
    print(f"   Results: Found {count} matching jobs")

    # 5. View Job Details (Will only run if Step 4 succeeds)
    if count > 0:
        job_id = res['results'][0]['id']
        print(f"\nStep 5: View Job Detail (ID: {job_id})")
        r = session.get(f"{BASE_URL}/jobs/{job_id}")
        print(f"   Detail Response: {r.json().get('title')} (Status: {r.status_code})")

    # 6. Membership Upgrade
    print("\nStep 6: Membership Upgrade")
    r = session.post(f"{BASE_URL}/membership/upgrade")
    print(f"   Response: {r.json().get('message')} (Status: {r.status_code})")

    print("=" * 60)
    print("Test Completed")

if __name__ == "__main__":
    run_test()