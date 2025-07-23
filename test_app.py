from app import app  # Adjust import if your app is not in app.py

def test_health_check():
    tester = app.test_client()
    response = tester.get('/health')
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "OK"
