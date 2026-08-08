def test_tc_tx_001_expense_on_bank_account_reduces_balance(client):
    """TC-TX-001: Expense transaction on Bank account automatically reduces bank balance."""
    acc_res = client.post("/api/v1/accounts", json={
        "name": "Salary Bank", "account_type": "bank", "balance": 10000.0
    })
    account_id = acc_res.json()["id"]

    tx_res = client.post("/api/v1/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": 1500.0,
        "category": "food",
        "description": "Swiggy Dinner"
    })
    assert tx_res.status_code == 201
    tx = tx_res.json()
    assert tx["amount"] == 1500.0
    assert tx["category"] == "food"

    get_tx_res = client.get(f"/api/v1/transactions/{tx['id']}")
    assert get_tx_res.status_code == 200
    assert get_tx_res.json()["id"] == tx["id"]

    acc_check = client.get(f"/api/v1/accounts/{account_id}")
    assert acc_check.json()["balance"] == 8500.0

def test_tc_tx_002_income_on_bank_account_increases_balance(client):
    """TC-TX-002: Income transaction on Bank account automatically increases bank balance."""
    acc_res = client.post("/api/v1/accounts", json={
        "name": "Checking Account", "account_type": "bank", "balance": 5000.0
    })
    account_id = acc_res.json()["id"]

    tx_res = client.post("/api/v1/transactions", json={
        "account_id": account_id,
        "transaction_type": "income",
        "amount": 25000.0,
        "category": "salary",
        "description": "Monthly Salary"
    })
    assert tx_res.status_code == 201

    acc_check = client.get(f"/api/v1/accounts/{account_id}")
    assert acc_check.json()["balance"] == 30000.0

def test_tc_tx_003_expense_and_payment_on_credit_card(client):
    """TC-TX-003: Expense increases credit card dues; Income/Payment decreases dues."""
    acc_res = client.post("/api/v1/accounts", json={
        "name": "HDFC Credit Card", "account_type": "credit_card", "balance": 5000.0
    })
    account_id = acc_res.json()["id"]

    tx1 = client.post("/api/v1/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": 2000.0,
        "category": "shopping"
    }).json()
    assert client.get(f"/api/v1/accounts/{account_id}").json()["balance"] == 7000.0

    tx2 = client.post("/api/v1/transactions", json={
        "account_id": account_id,
        "transaction_type": "income",
        "amount": 3000.0,
        "category": "bill_payment"
    }).json()
    assert client.get(f"/api/v1/accounts/{account_id}").json()["balance"] == 4000.0

    client.delete(f"/api/v1/transactions/{tx1['id']}")
    assert client.get(f"/api/v1/accounts/{account_id}").json()["balance"] == 2000.0

    client.delete(f"/api/v1/transactions/{tx2['id']}")
    assert client.get(f"/api/v1/accounts/{account_id}").json()["balance"] == 5000.0

def test_tc_tx_004_delete_bank_income_transaction(client):
    """TC-TX-004: Delete income transaction on bank account reverts balance."""
    acc_res = client.post("/api/v1/accounts", json={
        "name": "Test Savings", "account_type": "bank", "balance": 1000.0
    })
    account_id = acc_res.json()["id"]

    tx_res = client.post("/api/v1/transactions", json={
        "account_id": account_id, "transaction_type": "income", "amount": 500.0, "category": "bonus"
    })
    tx_id = tx_res.json()["id"]
    assert client.get(f"/api/v1/accounts/{account_id}").json()["balance"] == 1500.0

    client.delete(f"/api/v1/transactions/{tx_id}")
    assert client.get(f"/api/v1/accounts/{account_id}").json()["balance"] == 1000.0

def test_tc_tx_005_list_transactions_filters(client):
    """TC-TX-005: List transactions with account_id, category, and transaction_type filters."""
    acc1 = client.post("/api/v1/accounts", json={"name": "B1", "account_type": "bank", "balance": 100}).json()["id"]
    acc2 = client.post("/api/v1/accounts", json={"name": "B2", "account_type": "bank", "balance": 200}).json()["id"]

    client.post("/api/v1/transactions", json={"account_id": acc1, "transaction_type": "expense", "amount": 50, "category": "food"})
    client.post("/api/v1/transactions", json={"account_id": acc2, "transaction_type": "income", "amount": 100, "category": "salary"})

    res_acc = client.get(f"/api/v1/transactions?account_id={acc1}")
    assert len(res_acc.json()) == 1

    res_cat = client.get("/api/v1/transactions?category=food")
    assert len(res_cat.json()) == 1

    res_type = client.get("/api/v1/transactions?transaction_type=income")
    assert len(res_type.json()) == 1

def test_tc_tx_006_empty_category_breakdown(client):
    """TC-TX-006: Category breakdown returns zero for empty transactions."""
    res = client.get("/api/v1/transactions/analytics/categories")
    assert res.status_code == 200
    assert res.json()["total_expense"] == 0.0
    assert len(res.json()["categories"]) == 0

def test_tc_tx_007_category_spending_breakdown_with_account_filter(client):
    """TC-TX-007: Category breakdown analytics calculates totals and percentages."""
    acc1 = client.post("/api/v1/accounts", json={"name": "B1", "account_type": "bank", "balance": 50000.0}).json()["id"]
    acc2 = client.post("/api/v1/accounts", json={"name": "B2", "account_type": "bank", "balance": 50000.0}).json()["id"]

    client.post("/api/v1/transactions", json={"account_id": acc1, "transaction_type": "expense", "amount": 500.0, "category": "food"})
    client.post("/api/v1/transactions", json={"account_id": acc1, "transaction_type": "expense", "amount": 500.0, "category": "food"})
    client.post("/api/v1/transactions", json={"account_id": acc2, "transaction_type": "expense", "amount": 1000.0, "category": "shopping"})

    res = client.get(f"/api/v1/transactions/analytics/categories?account_id={acc1}")
    assert res.status_code == 200
    data = res.json()
    assert data["total_expense"] == 1000.0
    assert len(data["categories"]) == 1
    assert data["categories"][0]["category"] == "food"
    assert data["categories"][0]["percentage"] == 100.0

def test_tc_tx_008_transfer_bank_to_credit_card_bill_payment(client):
    """TC-TX-008: Inter-account transfer atomically adjusts balances and logs dual transactions."""
    bank_id = client.post("/api/v1/accounts", json={"name": "Salary Bank", "account_type": "bank", "balance": 50000.0}).json()["id"]
    card_id = client.post("/api/v1/accounts", json={"name": "Credit Card", "account_type": "credit_card", "balance": 15000.0}).json()["id"]

    transfer_res = client.post("/api/v1/transfers", json={
        "from_account_id": bank_id,
        "to_account_id": card_id,
        "amount": 10000.0,
        "description": "July Bill Payment"
    })
    assert transfer_res.status_code == 201
    data = transfer_res.json()

    assert data["amount"] == 10000.0
    assert data["transfer_tag"] == "Credit Card Bill Payment"
    assert data["from_account_new_balance"] == 40000.0

    assert client.get(f"/api/v1/accounts/{bank_id}").json()["balance"] == 40000.0
    assert client.get(f"/api/v1/accounts/{card_id}").json()["balance"] == 5000.0

def test_tc_tx_009_transfer_validation_errors(client):
    """TC-TX-009: Transfer validation errors (same account 422, missing account 404)."""
    acc_id = client.post("/api/v1/accounts", json={"name": "B1", "account_type": "bank", "balance": 5000.0}).json()["id"]

    same_res = client.post("/api/v1/transfers", json={
        "from_account_id": acc_id, "to_account_id": acc_id, "amount": 500.0
    })
    assert same_res.status_code == 422

    missing_from = client.post("/api/v1/transfers", json={
        "from_account_id": "non_existent_id", "to_account_id": acc_id, "amount": 500.0
    })
    assert missing_from.status_code == 404

    missing_to = client.post("/api/v1/transfers", json={
        "from_account_id": acc_id, "to_account_id": "non_existent_id", "amount": 500.0
    })
    assert missing_to.status_code == 404

def test_tc_tx_010_implicit_transfer_tag_classifications(client):
    """TC-TX-010: Verify implicit transfer_tag for Self Fund Transfer and Card Cash Advance."""
    b1_id = client.post("/api/v1/accounts", json={"name": "Bank 1", "account_type": "bank", "balance": 10000.0}).json()["id"]
    b2_id = client.post("/api/v1/accounts", json={"name": "Bank 2", "account_type": "bank", "balance": 2000.0}).json()["id"]
    card_id = client.post("/api/v1/accounts", json={"name": "Card 1", "account_type": "credit_card", "balance": 0.0}).json()["id"]

    # 1. Bank -> Bank = Self Fund Transfer
    t1 = client.post("/api/v1/transfers", json={"from_account_id": b1_id, "to_account_id": b2_id, "amount": 1000.0}).json()
    assert t1["transfer_tag"] == "Self Fund Transfer"

    # 2. Card -> Bank = Card Cash Advance
    t2 = client.post("/api/v1/transfers", json={"from_account_id": card_id, "to_account_id": b1_id, "amount": 500.0}).json()
    assert t2["transfer_tag"] == "Card Cash Advance"

