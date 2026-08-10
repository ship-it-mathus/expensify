from app.models import AccountType


def test_tc_inv_001_create_investment_account(client):
    """TC-INV-001: Create Investment Account — auto-excluded from net worth."""
    payload = {
        "name": "Zerodha Kite Portfolio",
        "account_type": "investment",
        "balance": 150000.0,
        "currency": "INR",
        "notes": "Equity mutual funds"
    }
    response = client.post("/api/v1/accounts", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["account_type"] == "investment"
    assert data["balance"] == 150000.0
    # Investment accounts must always be excluded from liquid net worth
    assert data["include_in_net_worth"] is False


def test_tc_inv_002_investment_excluded_from_liquid_summary(client):
    """TC-INV-002: Investment account balance never counts towards liquid net worth."""
    client.post("/api/v1/accounts", json={
        "name": "Savings Bank", "account_type": "bank",
        "balance": 100000.0, "include_in_net_worth": True
    })
    client.post("/api/v1/accounts", json={
        "name": "SIP Portfolio", "account_type": "investment",
        "balance": 500000.0
    })

    res = client.get("/api/v1/summary")
    assert res.status_code == 200
    summary = res.json()

    # Liquid money = bank only, investment not included
    assert summary["total_bank_balance"] == 100000.0
    assert summary["actual_liquid_money"] == 100000.0
    # Investment tracked separately
    assert summary["total_investment_balance"] == 500000.0
    # Investment counted as excluded
    assert summary["excluded_accounts_count"] == 1
    assert summary["included_accounts_count"] == 1


def test_tc_inv_003_investment_analytics_endpoint(client):
    """TC-INV-003: Investment analytics returns % of income invested this month."""
    # Create a bank and investment account
    bank_id = client.post("/api/v1/accounts", json={
        "name": "Bank", "account_type": "bank", "balance": 100000.0
    }).json()["id"]
    inv_id = client.post("/api/v1/accounts", json={
        "name": "Portfolio", "account_type": "investment", "balance": 0.0
    }).json()["id"]

    # Log salary income
    client.post("/api/v1/transactions", json={
        "account_id": bank_id,
        "transaction_type": "income",
        "amount": 100000.0,
        "category": "salary"
    })

    # Transfer 20,000 to investment account (simulates SIP)
    client.post("/api/v1/transfers", json={
        "from_account_id": bank_id,
        "to_account_id": inv_id,
        "amount": 20000.0,
        "description": "Monthly SIP"
    })

    res = client.get("/api/v1/analytics/investment")
    assert res.status_code == 200
    data = res.json()

    assert data["total_invested"] == 20000.0
    assert data["total_income"] == 100000.0
    assert data["pct_income_invested"] == 20.0
    assert data["total_investment_balance"] == 20000.0


def test_tc_inv_004_investment_analytics_no_investments(client):
    """TC-INV-004: Investment analytics returns zeros when no investment accounts exist."""
    res = client.get("/api/v1/analytics/investment")
    assert res.status_code == 200
    data = res.json()
    assert data["total_invested"] == 0.0
    assert data["pct_income_invested"] == 0.0
    assert data["total_investment_balance"] == 0.0
