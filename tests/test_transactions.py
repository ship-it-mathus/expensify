def test_expense_on_bank_account_reduces_balance(client):
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

    # Fetch single transaction
    get_tx_res = client.get(f"/api/v1/transactions/{tx['id']}")
    assert get_tx_res.status_code == 200
    assert get_tx_res.json()["id"] == tx["id"]

    # Verify Account balance automatically decreased to 8,500
    acc_check = client.get(f"/api/v1/accounts/{account_id}")
    assert acc_check.json()["balance"] == 8500.0

def test_income_on_bank_account_increases_balance(client):
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

def test_expense_and_payment_on_credit_card(client):
    acc_res = client.post("/api/v1/accounts", json={
        "name": "HDFC Credit Card", "account_type": "credit_card", "balance": 5000.0
    })
    account_id = acc_res.json()["id"]

    # Expense of 2,000 ➔ Increases due to 7,000
    tx1 = client.post("/api/v1/transactions", json={
        "account_id": account_id,
        "transaction_type": "expense",
        "amount": 2000.0,
        "category": "shopping"
    }).json()
    assert client.get(f"/api/v1/accounts/{account_id}").json()["balance"] == 7000.0

    # Income/Payment of 3,000 ➔ Decreases due to 4,000
    tx2 = client.post("/api/v1/transactions", json={
        "account_id": account_id,
        "transaction_type": "income",
        "amount": 3000.0,
        "category": "bill_payment"
    }).json()
    assert client.get(f"/api/v1/accounts/{account_id}").json()["balance"] == 4000.0

    # Delete Credit Card Expense transaction (2,000) ➔ Reverts due from 4,000 to 2,000
    client.delete(f"/api/v1/transactions/{tx1['id']}")
    assert client.get(f"/api/v1/accounts/{account_id}").json()["balance"] == 2000.0

    # Delete Credit Card Income/Payment transaction (3,000) ➔ Reverts due from 2,000 back to 5,000
    client.delete(f"/api/v1/transactions/{tx2['id']}")
    assert client.get(f"/api/v1/accounts/{account_id}").json()["balance"] == 5000.0

def test_delete_bank_income_transaction(client):
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

def test_list_transactions_filters(client):
    acc1 = client.post("/api/v1/accounts", json={"name": "B1", "account_type": "bank", "balance": 100}).json()["id"]
    acc2 = client.post("/api/v1/accounts", json={"name": "B2", "account_type": "bank", "balance": 200}).json()["id"]

    client.post("/api/v1/transactions", json={"account_id": acc1, "transaction_type": "expense", "amount": 50, "category": "food"})
    client.post("/api/v1/transactions", json={"account_id": acc2, "transaction_type": "income", "amount": 100, "category": "salary"})

    # Filter by account_id
    res_acc = client.get(f"/api/v1/transactions?account_id={acc1}")
    assert len(res_acc.json()) == 1

    # Filter by category
    res_cat = client.get("/api/v1/transactions?category=food")
    assert len(res_cat.json()) == 1

    # Filter by transaction_type
    res_type = client.get("/api/v1/transactions?transaction_type=income")
    assert len(res_type.json()) == 1

def test_empty_category_breakdown(client):
    res = client.get("/api/v1/transactions/analytics/categories")
    assert res.status_code == 200
    assert res.json()["total_expense"] == 0.0
    assert len(res.json()["categories"]) == 0

def test_category_spending_breakdown_with_account_filter(client):
    acc1 = client.post("/api/v1/accounts", json={"name": "B1", "account_type": "bank", "balance": 50000.0}).json()["id"]
    acc2 = client.post("/api/v1/accounts", json={"name": "B2", "account_type": "bank", "balance": 50000.0}).json()["id"]

    client.post("/api/v1/transactions", json={"account_id": acc1, "transaction_type": "expense", "amount": 500.0, "category": "food"})
    client.post("/api/v1/transactions", json={"account_id": acc1, "transaction_type": "expense", "amount": 500.0, "category": "food"})
    client.post("/api/v1/transactions", json={"account_id": acc2, "transaction_type": "expense", "amount": 1000.0, "category": "shopping"})

    # Breakdown for acc1 only
    res = client.get(f"/api/v1/transactions/analytics/categories?account_id={acc1}")
    assert res.status_code == 200
    data = res.json()
    assert data["total_expense"] == 1000.0
    assert len(data["categories"]) == 1
    assert data["categories"][0]["category"] == "food"
    assert data["categories"][0]["percentage"] == 100.0
