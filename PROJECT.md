# 💳 Expensify API

An asynchronous, cloud-ready REST API built with **FastAPI** and **Supabase (PostgreSQL)** for tracking accounts, credit card dues, income/expense transactions, custom categories, monthly analytics, inter-account transfers, and net available liquid money with custom account exclusion support.

🌐 **Live Production API**: [https://expensify-api-fj8q.onrender.com/docs](https://expensify-api-fj8q.onrender.com/docs)  
📦 **GitHub Repository**: [https://github.com/ship-it-mathus/expensify](https://github.com/ship-it-mathus/expensify)  
🧪 **Test Matrix**: [`TESTCASES.md`](file:///Users/mathews/Projects/Expensify/TESTCASES.md)

---

## 🎯 Vision & Core Features

- **Multi-Account Management**: Track Bank Accounts and Credit Card Dues in one place.
- **Dynamic Net Worth Calculation**:
  $$\text{Actual Liquid Money} = \sum_{\text{Included Bank Balances}} - \sum_{\text{Included Credit Card Dues}}$$
- **Account Exclusion (Hiding)**: Toggle `include_in_net_worth = false` on specific accounts (e.g., Emergency Fund) to keep them safe from daily liquid cash calculations.
- **Automated Transactions Engine**: Logging an income or expense transaction automatically updates target bank balances or credit card dues in real-time.
- **Paisa-Style Category Management**: Pre-seeded default Income & Expense categories (`Salary`, `Side Hustle`, `Food`, `Fuel`, `Rent`, `Shopping`, `Utilities`), plus custom user category creation.
- **Monthly Savings & Spending Analytics**: Monthly income vs expense totals, net savings rate, and percentage breakdown by category.
- **Inter-Account Transfers & Bill Payments**: Transfer funds between accounts (e.g., Bank Account ➔ Credit Card to pay off dues).
- **1000% Quality Test Suite**: 27 automated unit/integration test cases mapped to [`TESTCASES.md`](file:///Users/mathews/Projects/Expensify/TESTCASES.md) with 98% code coverage.
- **Live OpenAPI Documentation**: Auto-generated interactive Swagger UI at `/docs`.

---

## 🛠️ Tech Stack & Architecture

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Framework** | FastAPI | High-performance Python web framework |
| **Web Server** | Uvicorn | Asynchronous Server Gateway Interface (ASGI) server |
| **Database** | Supabase (PostgreSQL) | Managed Cloud Relational Database |
| **ORM** | SQLAlchemy | Python SQL Toolkit and Object Relational Mapper |
| **Validation** | Pydantic v2 | Data validation and settings management |
| **Testing** | Pytest & HTTPX | 27 automated tests with in-memory SQLite isolation (98% coverage) |
| **Container** | Docker | Lightweight Python 3.11-slim container |
| **Hosting** | Render | Automated CI/CD web service deployment |

### 📂 Directory Structure

```
Expensify/
├── .antigravity/        # Project level Antigravity configuration
│   └── instructions.md  # 1000% Quality & test mapping rules
├── app/
│   ├── __init__.py      # Package initialization
│   ├── main.py          # FastAPI app instance, CORS middleware & route registration
│   ├── config.py        # Environment settings loader (.env)
│   ├── database.py      # SQLAlchemy engine setup & DB session dependency
│   ├── models.py        # Database models (Account, Category, Transaction tables & Enums)
│   ├── schemas.py       # Pydantic request/response validation schemas
│   └── routers/
│       ├── __init__.py
│       ├── accounts.py     # Account CRUD, account transactions & net worth summary
│       ├── analytics.py    # Monthly income vs expense analytics & savings rate
│       ├── categories.py   # Income vs Expense categories listing & custom creation
│       └── transactions.py # Transaction logging, transfers & category analytics
├── tests/               # Automated test suite (98-100% coverage)
│   ├── conftest.py          # Pytest fixtures & in-memory DB override
│   ├── test_accounts.py     # Account CRUD, account transactions & net worth tests
│   ├── test_analytics.py    # Monthly analytics & savings rate tests
│   ├── test_categories.py   # Category listing, filtering, duplicate & deletion tests
│   ├── test_database.py     # Database session lifecycle test
│   ├── test_main.py         # Root route health check test
│   └── test_transactions.py # Transaction engine, transfers & analytics tests
├── .env                 # Environment variables (Database URL)
├── .gitignore           # Ignored files (venv, pycache, env)
├── Dockerfile           # Docker container configuration
├── LEARNINGS.md         # Systems architecture & backend engineering learnings
├── PROJECT.md          # Project documentation & reference
├── STATUS.md           # Persistent project status & roadmap tracker
├── TESTCASES.md        # Numbered test case catalog & mapping matrix
└── requirements.txt     # Python package dependencies
```

---

## 🔌 API Reference

### 1. Net Worth Summary
- **`GET /api/v1/summary`**: Calculate net liquid money and account counts.

### 2. Accounts CRUD
- **`POST /api/v1/accounts`**: Create a Bank Account or Credit Card.
- **`GET /api/v1/accounts`**: List all accounts (optional query param `?include_in_net_worth=true`).
- **`GET /api/v1/accounts/{id}`**: Get specific account details.
- **`GET /api/v1/accounts/{id}/transactions`**: Get transaction timeline for specific account.
- **`PATCH /api/v1/accounts/{id}`**: Update account details/balance/exclusion toggle.
- **`DELETE /api/v1/accounts/{id}`**: Delete account.

### 3. Categories Management
- **`GET /api/v1/categories`**: List categories (filter by `category_type=income` vs `category_type=expense`).
- **`POST /api/v1/categories`**: Create custom category.
- **`DELETE /api/v1/categories/{id}`**: Delete custom category.

### 4. Transactions, Transfers & Analytics
- **`POST /api/v1/transactions`**: Log Income or Expense (auto balance update).
- **`POST /api/v1/transfers`**: Inter-account transfer (e.g. Bank ➔ Credit Card bill payment).
- **`GET /api/v1/transactions`**: List transactions (filter by `account_id`, `category`, `transaction_type`).
- **`GET /api/v1/transactions/{id}`**: Get transaction details.
- **`DELETE /api/v1/transactions/{id}`**: Delete transaction & revert balance.
- **`GET /api/v1/transactions/analytics/categories`**: Category expense breakdown.
- **`GET /api/v1/analytics/monthly`**: Monthly income, expenses, net savings, and savings rate percentage.

---

## 🚀 Getting Started

### Local Development Setup

1. **Activate Virtual Environment**:
   ```bash
   source venv/bin/activate
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Test Suite**:
   ```bash
   pytest --cov=app --cov-report=term-missing
   ```

4. **Start Development Server**:
   ```bash
   uvicorn app.main:app --reload
   ```

5. **Access Interactive Docs**:
   - Swagger UI: `http://127.0.0.1:8000/docs`
   - Live Production: `https://expensify-api-fj8q.onrender.com/docs`
