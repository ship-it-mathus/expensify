# 💳 Expensify API

> A fast, asynchronous, cloud-hosted expense & net worth tracking API built with **FastAPI**, **Supabase (PostgreSQL)**, and **Docker**. Inspired by Paisa's clean workflow.

[![Production API](https://img.shields.io/badge/Production_API-Render-brightgreen)](https://expensify-api-fj8q.onrender.com/docs)
[![Database](https://img.shields.io/badge/Database-Supabase_PostgreSQL-blue)](https://supabase.com)
[![Tests](https://img.shields.io/badge/Tests-27_Passed_98%25_Cov-success)](TESTCASES.md)

---

## 🌟 Features at a Glance

- 🏦 **Multi-Account Management**: Track Bank Accounts and Credit Cards seamlessly in one place.
- 💡 **Actual Liquid Cash Math**:
  $$\text{Actual Liquid Money} = \sum_{\text{Included Bank Balances}} - \sum_{\text{Included Credit Card Dues}}$$
- 🙈 **Account Hiding**: Toggle `include_in_net_worth = false` on accounts (like your Emergency Fund) so they don't skew your daily liquid cash calculations.
- ⚡ **Automated Balance Engine**: Logging an expense or income transaction automatically updates target bank balances or credit card dues in real-time.
- 🔀 **Inter-Account Transfers & Bill Payments**: Transfer funds between accounts (e.g. pay off your Credit Card bill from your Bank Account with 1 API call).
- 🏷️ **Paisa-Style Categories**: Pre-seeded Income (`Salary`, `Side Hustle`, `Freelance`) vs Expense (`Food`, `Fuel`, `Rent`, `Utilities`, `Shopping`) categories + custom user category creation.
- 📊 **Monthly Savings & Spending Analytics**: Real-time spending percentages and monthly net savings rate.
- 🛡️ **1000% Quality Standards**: 27 automated tests with in-memory SQLite isolation cataloged in [`TESTCASES.md`](TESTCASES.md).

---

## 🚀 Interactive API Docs

Explore and test all live endpoints directly in your browser:
👉 **[Live Swagger UI Documentation](https://expensify-api-fj8q.onrender.com/docs)**

---

## 💡 Feature Showcase & Usage Examples

### 1. Check Your Net Available Cash (`GET /api/v1/summary`)
Returns your total liquid money after subtracting credit card dues and filtering out hidden accounts.

```json
// GET /api/v1/summary
{
  "total_bank_balance": 75000.0,
  "total_credit_card_dues": 15000.0,
  "actual_liquid_money": 60000.0,
  "included_accounts_count": 2,
  "excluded_accounts_count": 1,
  "currency": "INR"
}
```

---

### 2. Log an Expense Transaction (`POST /api/v1/transactions`)
Automatically deducts ₹450 from your Bank balance and logs the transaction.

```json
// POST /api/v1/transactions
{
  "account_id": 1,
  "transaction_type": "expense",
  "amount": 450.0,
  "category": "food",
  "description": "Dinner at Swiggy"
}
```

---

### 3. Pay Credit Card Bill / Inter-Account Transfer (`POST /api/v1/transfers`)
Transfers ₹10,000 from Bank Account (ID 1) to Credit Card (ID 2). Automatically reduces your bank balance and pays off your credit card due!

```json
// POST /api/v1/transfers
{
  "from_account_id": 1,
  "to_account_id": 2,
  "amount": 10000.0,
  "description": "July Credit Card Bill Payment"
}
```

---

### 4. Category Spending Breakdown (`GET /api/v1/transactions/analytics/categories`)
Groups expenses by category and returns spending percentages for charts.

```json
// GET /api/v1/transactions/analytics/categories
{
  "total_expense": 2000.0,
  "categories": [
    { "category": "food", "total_amount": 1000.0, "percentage": 50.0 },
    { "category": "shopping", "total_amount": 1000.0, "percentage": 50.0 }
  ]
}
```

---

### 5. Monthly Savings Analytics (`GET /api/v1/analytics/monthly`)
Tracks your monthly cash flow and savings rate.

```json
// GET /api/v1/analytics/monthly?year=2026&month=8
{
  "year": 2026,
  "month": 8,
  "total_income": 100000.0,
  "total_expense": 40000.0,
  "net_savings": 60000.0,
  "savings_rate_percentage": 60.0
}
```

---

## 🛠️ Local Setup & Testing

```bash
# 1. Clone & activate virtual environment
git clone https://github.com/ship-it-mathus/expensify.git
cd expensify
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run automated test suite (27 tests)
pytest --cov=app --cov-report=term-missing

# 4. Start local development server
uvicorn app.main:app --reload
```

---

## 📖 Architecture & Documentation

- [`PROJECT.md`](PROJECT.md): Full technical specification & file mapping.
- [`LEARNINGS.md`](LEARNINGS.md): Systems architecture, ASGI/Uvicorn, and connection pooling learnings.
- [`STATUS.md`](STATUS.md): Persistent roadmap & deployment status tracker.
- [`TESTCASES.md`](TESTCASES.md): 27 cataloged test cases with direct code links.
