from app.models import AccountType

def test_tc_acc_001_empty_net_worth_summary(client):
    """TC-ACC-001: Net Worth summary returns zero for empty database."""
    response = client.get("/api/v1/summary")
    assert response.status_code == 200
    data = response.json()
    assert data["total_bank_balance"] == 0.0
    assert data["total_credit_card_dues"] == 0.0
    assert data["actual_liquid_money"] == 0.0
    assert data["included_accounts_count"] == 0
    assert data["excluded_accounts_count"] == 0

def test_tc_acc_002_create_bank_account(client):
    """TC-ACC-002: Create Bank Account successfully."""
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

def test_tc_acc_003_create_credit_card_account(client):
    """TC-ACC-003: Create Credit Card Account successfully."""
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

def test_tc_acc_004_list_accounts_and_filters(client):
    """TC-ACC-004: List all accounts and filter by include_in_net_worth."""
    client.post("/api/v1/accounts", json={
        "name": "Bank 1", "account_type": "bank", "balance": 100.0, "include_in_net_worth": True
    })
    client.post("/api/v1/accounts", json={
        "name": "Bank 2 (Emergency)", "account_type": "bank", "balance": 500.0, "include_in_net_worth": False
    })

    res = client.get("/api/v1/accounts")
    assert res.status_code == 200
    assert len(res.json()) == 2

    res_inc = client.get("/api/v1/accounts?include_in_net_worth=true")
    assert res_inc.status_code == 200
    assert len(res_inc.json()) == 1
    assert res_inc.json()[0]["name"] == "Bank 1"

    res_exc = client.get("/api/v1/accounts?include_in_net_worth=false")
    assert res_exc.status_code == 200
    assert len(res_exc.json()) == 1
    assert res_exc.json()[0]["name"] == "Bank 2 (Emergency)"

def test_tc_acc_005_get_account_by_id(client):
    """TC-ACC-005: Fetch single account by ID and verify 404 for missing account."""
    create_res = client.post("/api/v1/accounts", json={
        "name": "SBI Account", "account_type": "bank", "balance": 25000.0
    })
    account_id = create_res.json()["id"]

    res = client.get(f"/api/v1/accounts/{account_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "SBI Account"

    res_404 = client.get("/api/v1/accounts/9999")
    assert res_404.status_code == 404
    assert "not found" in res_404.json()["detail"].lower()

def test_tc_acc_006_update_account(client):
    """TC-ACC-006: Update account attributes and verify 404 for missing account."""
    create_res = client.post("/api/v1/accounts", json={
        "name": "Old Name", "account_type": "bank", "balance": 1000.0, "include_in_net_worth": True
    })
    account_id = create_res.json()["id"]

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

    patch_404 = client.patch("/api/v1/accounts/9999", json={"balance": 500.0})
    assert patch_404.status_code == 404

def test_tc_acc_007_delete_account(client):
    """TC-ACC-007: Delete account and verify 404 for missing account."""
    create_res = client.post("/api/v1/accounts", json={
        "name": "Temp Account", "account_type": "bank", "balance": 50.0
    })
    account_id = create_res.json()["id"]

    del_res = client.delete(f"/api/v1/accounts/{account_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/v1/accounts/{account_id}")
    assert get_res.status_code == 404

    del_404 = client.delete("/api/v1/accounts/9999")
    assert del_404.status_code == 404

def test_tc_acc_008_net_worth_calculation_logic(client):
    """TC-ACC-008: Verify Net Worth Math (Included Bank Balances - Included Credit Card Dues)."""
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

def test_tc_acc_009_get_account_specific_transactions(client):
    """TC-ACC-009: Get transactions filtered for a specific account."""
    acc1 = client.post("/api/v1/accounts", json={"name": "B1", "account_type": "bank", "balance": 1000}).json()["id"]
    acc2 = client.post("/api/v1/accounts", json={"name": "B2", "account_type": "bank", "balance": 2000}).json()["id"]

    client.post("/api/v1/transactions", json={"account_id": acc1, "transaction_type": "expense", "amount": 100, "category": "food"})
    client.post("/api/v1/transactions", json={"account_id": acc2, "transaction_type": "expense", "amount": 200, "category": "fuel"})

    txs1 = client.get(f"/api/v1/accounts/{acc1}/transactions")
    assert txs1.status_code == 200
    assert len(txs1.json()) == 1
    assert txs1.json()[0]["amount"] == 100.0

    txs_404 = client.get("/api/v1/accounts/99999/transactions")
    assert txs_404.status_code == 404
