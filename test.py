import requests

BASE_URL = "https://myrl-hpgxb5gaezembecs.canadacentral-01.azurewebsites.net/"


def log_response(method, endpoint, response):
    print(f"[{method} {endpoint}] ✅ Status Code: {response.status_code}")
    try:
        print(f"[{method} {endpoint}] Response: {response.json()}")
    except Exception:
        print(f"[{method} {endpoint}] Response (raw): {response.text}")

def log_error(method, endpoint, error):
    print(f"[{method} {endpoint}] ❌ Error: {error}")

# Test GET request to "/"
def test_root():
    endpoint = "/"
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        log_response("GET", endpoint, response)
        assert response.status_code == 200
    except Exception as e:
        log_error("GET", endpoint, e)

# Test POST request to "/get-action"
def test_get_action():
    endpoint = "/get-action"
    payload = {"state": [25.0, 0, 1]}  # Customize with realistic values if needed
    try:
        response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=10)
        log_response("POST", endpoint, response)
        assert response.status_code == 200
    except Exception as e:
        log_error("POST", endpoint, e)

if __name__ == "__main__":
    print("🔍 Running API tests...")
    test_root()
    test_get_action()
