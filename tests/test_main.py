def test_tc_root_001_root_health_check(client):
    """TC-ROOT-001: Health check root endpoint returns online status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Expensify" in data["message"]
    assert data["docs_url"] == "/docs"


