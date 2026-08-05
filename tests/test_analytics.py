def test_tc_ana_001_monthly_analytics_empty_state(client):
    """TC-ANA-001: Verify monthly analytics with no transactions."""
    res = client.get("/api/v1/analytics/monthly?year=2026&month=8")
    assert res.status_code == 200
    data = res.json()
    assert data["total_income"] == 0.0
    assert data["total_expense"] == 0.0
    assert data["net_savings"] == 0.0
    assert data["savings_rate_percentage"] == 0.0
    assert len(data["categories"]) == 0

def test_tc_ana_002_monthly_analytics_income_expense_savings(client):
    """TC-ANA-002: Verify monthly income, expenses, net savings, and savings rate math."""
    acc_res = client.post("/api/v1/accounts", json={"name": "Bank 1", "account_type": "bank", "balance": 100000.0})
    acc_id = acc_res.json()["id"]

    # Log Income of 100,000
    client.post("/api/v1/transactions", json={
        "account_id": acc_id, "transaction_type": "income", "amount": 100000.0, "category": "salary"
    })

    # Log Expenses of 40,000 (Food: 10k, Rent: 30k)
    client.post("/api/v1/transactions", json={
        "account_id": acc_id, "transaction_type": "expense", "amount": 10000.0, "category": "food"
    })
    client.post("/api/v1/transactions", json={
        "account_id": acc_id, "transaction_type": "expense", "amount": 30000.0, "category": "rent"
    })

    res = client.get("/api/v1/analytics/monthly")
    assert res.status_code == 200
    data = res.json()

    assert data["total_income"] == 100000.0
    assert data["total_expense"] == 40000.0
    assert data["net_savings"] == 60000.0
    assert data["savings_rate_percentage"] == 60.0
    assert len(data["categories"]) == 2
