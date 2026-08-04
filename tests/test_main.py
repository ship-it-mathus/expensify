def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Expensify" in data["message"]
    assert data["docs_url"] == "/docs"
