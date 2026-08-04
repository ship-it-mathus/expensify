from app.models import AccountType

def test_empty_net_worth_summary(client):
    response = client.get("/api/v1/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_bank_balance"] == 0.0
    assert data["total_credit_card_dues"] == 0.0
    assert data["actual_liquid_money"] == 0.0
    assert data["included_accounts_count"] == 0
    assert data["excluded_accounts_count"] == 0

def test_create_bank_account(client):
    payload = {
        "name": "HDFC Savings Account",
        "account_type": "bank",
        "balance": 50000.0,
        "include_in_net_worth": True,
        "currency": "INR",
        "notes": "Salary account"
    }
    response = client.post("/api/v1/accounts", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "HDFC Savings Account"
    assert data["account_type"] == "bank"
    assert data["balance"] == 50000.0
    assert data["include_in_net_worth"] is True

def test_create_credit_card_account(client):
    payload = {
        "name": "ICICI Credit Card",
        "account_type": "credit_card",
        "balance": 12000.0,
        "include_in_net_worth": True,
        "currency": "INR"
    }
    response = client.post("/api/v1/accounts", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "ICICI Credit Card"
    assert data["account_type"] == "credit_card"
    assert data["balance"] == 12000.0

def test_list_accounts_and_filters(client):
    # Create 3 accounts: 2 included, 1 excluded
    client.post("/api/v1/accounts", json={
        "name": "Bank 1", "account_type": "bank", "balance": 100.0, "include_in_net_worth": True
    })
    client.post("/api/v1/accounts", json={
        "name": "Bank 2 (Emergency)", "account_type": "bank", "balance": 500.0, "include_in_net_worth": False
    })

    # List all
    res = client.get("/api/v1/accounts")
    assert res.status_code == 200
    assert len(res.json()) == 2

    # Filter included
    res_inc = client.get("/api/v1/accounts?include_in_net_worth=true")
    assert res_inc.status_code == 200
    assert len(res_inc.json()) == 1
    assert res_inc.json()[0]["name"] == "Bank 1"

    # Filter excluded
    res_exc = client.get("/api/v1/accounts?include_in_net_worth=false")
    assert res_exc.status_code == 200
    assert len(res_exc.json()) == 1
    assert res_exc.json()[0]["name"] == "Bank 2 (Emergency)"

def test_get_account_by_id(client):
    create_res = client.post("/api/v1/accounts", json={
        "name": "SBI Account", "account_type": "bank", "balance": 25000.0
    })
    account_id = create_res.json()["id"]

    # Success case
    res = client.get(f"/api/v1/accounts/{account_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "SBI Account"

    # 404 Not Found case
    res_404 = client.get("/api/v1/accounts/9999")
    assert res_404.status_code == 404
    assert "not found" in res_404.json()["detail"].lower()

def test_update_account(client):
    create_res = client.post("/api/v1/accounts", json={
        "name": "Old Name", "account_type": "bank", "balance": 1000.0, "include_in_net_worth": True
    })
    account_id = create_res.json()["id"]

    # Update balance and toggle inclusion
    patch_res = client.patch(f"/api/v1/accounts/{account_id}", json={
        "name": "Updated Name",
        "balance": 2500.0,
        "include_in_net_worth": False
    })
    assert patch_res.status_code == 200
    updated = patch_res.json()
    assert updated["name"] == "Updated Name"
    assert updated["balance"] == 2500.0
    assert updated["include_in_net_worth"] is False

    # 404 Update test
    patch_404 = client.patch("/api/v1/accounts/9999", json={"balance": 500.0})
    assert patch_404.status_code == 404

def test_delete_account(client):
    create_res = client.post("/api/v1/accounts", json={
        "name": "Temp Account", "account_type": "bank", "balance": 50.0
    })
    account_id = create_res.json()["id"]

    # Delete success
    del_res = client.delete(f"/api/v1/accounts/{account_id}")
    assert del_res.status_code == 204

    # Verify deleted
    get_res = client.get(f"/api/v1/accounts/{account_id}")
    assert get_res.status_code == 404

    # Delete non-existing account 404
    del_404 = client.delete("/api/v1/accounts/9999")
    assert del_404.status_code == 404

def test_net_worth_calculation_logic(client):
    """
    Tests calculation math:
    Bank 1 (Included): 100,000
    Bank 2 (Excluded / Emergency): 500,000
    Credit Card 1 (Included): 20,000
    Credit Card 2 (Included): 5,000

    Expected Liquid Money = 100,000 - (20,000 + 5,000) = 75,000
    """
    client.post("/api/v1/accounts", json={
        "name": "Primary Bank", "account_type": "bank", "balance": 100000.0, "include_in_net_worth": True
    })
    client.post("/api/v1/accounts", json={
        "name": "Emergency Fund", "account_type": "bank", "balance": 500000.0, "include_in_net_worth": False
    })
    client.post("/api/v1/accounts", json={
        "name": "Credit Card 1", "account_type": "credit_card", "balance": 20000.0, "include_in_net_worth": True
    })
    client.post("/api/v1/accounts", json={
        "name": "Credit Card 2", "account_type": "credit_card", "balance": 5000.0, "include_in_net_worth": True
    })

    res = client.get("/api/v1/summary")
    assert res.status_code == 200
    summary = res.json()

    assert summary["total_bank_balance"] == 100000.0
    assert summary["total_credit_card_dues"] == 25000.0
    assert summary["actual_liquid_money"] == 75000.0
    assert summary["included_accounts_count"] == 3
    assert summary["excluded_accounts_count"] == 1
