def test_tc_root_001_health_check(client):
    """TC-ROOT-001: Health check endpoint returns online status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Expensify" in data["message"]
    assert data["docs_url"] == "/docs"

def test_tc_root_002_pwa_dashboard(client):
    """TC-ROOT-002: Root endpoint serves the Mobile Dashboard PWA HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Expensify" in response.text
    assert "text/html" in response.headers["content-type"]

