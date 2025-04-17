import requests

BASE_URL = "http://127.0.0.1:8000/"

# Test GET request to "/"
def test_root():
    try:
        response = requests.get(BASE_URL, timeout=10)
        print(f"[GET /] Status Code: {response.status_code}")
        print(f"[GET /] Response: {response.text}")
        assert response.status_code == 200
    except Exception as e:
        print("[GET /] ❌ Error:", e)

# Test POST request to "/get-action"
def test_get_action():
    payload = {"state": [25.0, 0, 1]}  # replace with realistic state values as needed
    try:
        response = requests.post(f"{BASE_URL}/get-action", json=payload, timeout=10)
        print(f"[POST /get-action] Status Code: {response.status_code}")
        print(f"[POST /get-action] Response: {response.json()}")
        assert response.status_code == 200
    except Exception as e:
        print("[POST /get-action] ❌ Error:", e)

if __name__ == "__main__":
    print("🔍 Testing FastAPI App Deployment...")
    test_root()
    test_get_action()
