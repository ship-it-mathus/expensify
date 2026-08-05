# 💳 Expensify API

An asynchronous, cloud-ready REST API built with **FastAPI** and **Supabase (PostgreSQL)** for tracking accounts, credit card dues, income/expense transactions, category analytics, and net available liquid money with custom account exclusion support.

🌐 **Live Production API**: [https://expensify-api-fj8q.onrender.com/docs](https://expensify-api-fj8q.onrender.com/docs)  
📦 **GitHub Repository**: [https://github.com/ship-it-mathus/expensify](https://github.com/ship-it-mathus/expensify)

---

## 🎯 Vision & Core Features

- **Multi-Account Management**: Track Bank Accounts and Credit Card Dues in one place.
- **Dynamic Net Worth Calculation**:
  $$\text{Actual Liquid Money} = \sum_{\text{Included Bank Balances}} - \sum_{\text{Included Credit Card Dues}}$$
- **Account Exclusion (Hiding)**: Toggle `include_in_net_worth = false` on specific accounts (e.g., Emergency Fund) to keep them safe from daily liquid cash calculations.
- **Automated Transactions Engine**: Logging an income or expense transaction automatically updates target bank balances or credit card dues in real-time.
- **Category Spending Analytics**: Group expense transactions by category (Food, Shopping, Salary, Utilities) and calculate spending percentages.
- **Live OpenAPI Documentation**: Auto-generated interactive Swagger UI at `/docs`.
- **Cloud Database Integration**: Connected to a managed PostgreSQL instance on Supabase via Transaction Pooler.
- **Container Ready**: Prepared with Dockerfile for Koyeb or Render serverless deployment.

---

## 🛠️ Tech Stack & Architecture

| Layer | Technology | Description |
| :--- | :--- | :--- |
| **Framework** | FastAPI | High-performance Python web framework |
| **Web Server** | Uvicorn | Asynchronous Server Gateway Interface (ASGI) server |
| **Database** | Supabase (PostgreSQL) | Managed Cloud Relational Database |
| **ORM** | SQLAlchemy | Python SQL Toolkit and Object Relational Mapper |
| **Validation** | Pydantic v2 | Data validation and settings management |
| **Testing** | Pytest & HTTPX | 17 automated tests with in-memory SQLite isolation (98% coverage) |
| **Container** | Docker | Lightweight Python 3.11-slim container |
| **Hosting** | Render | Automated CI/CD web service deployment |

### 📂 Directory Structure

```
Expensify/
├── app/
│   ├── __init__.py      # Package initialization
│   ├── main.py          # FastAPI app instance, CORS middleware & route registration
│   ├── config.py        # Environment settings loader (.env)
│   ├── database.py      # SQLAlchemy engine setup & DB session dependency
│   ├── models.py        # Database models (Account, Transaction tables & Enums)
│   ├── schemas.py       # Pydantic request/response validation schemas
│   └── routers/
│       ├── __init__.py
│       ├── accounts.py  # Endpoints for CRUD ops & net worth calculation
│       └── transactions.py # Endpoints for transaction logging & category analytics
├── tests/               # Automated test suite (98-100% coverage)
│   ├── conftest.py      # Pytest fixtures & in-memory DB override
│   ├── test_accounts.py # Account CRUD & net worth math tests
│   ├── test_database.py # Database session lifecycle test
│   ├── test_main.py     # Root route health check test
│   └── test_transactions.py # Transaction engine & category analytics tests
├── .env                 # Environment variables (Database URL)
├── .gitignore           # Ignored files (venv, pycache, env)
├── Dockerfile           # Docker container configuration
├── LEARNINGS.md         # Systems architecture & backend engineering learnings
├── PROJECT.md          # Project documentation & reference
├── STATUS.md           # Persistent project status & roadmap tracker
└── requirements.txt     # Python package dependencies
```

---

## 🔌 API Reference

### 1. Net Worth Summary
- **`GET /api/v1/summary`**
  - **Summary**: Returns total bank balances, total credit card dues, net liquid cash, and account counts.
  - **Logic**: Automatically filters out accounts where `include_in_net_worth == false`.

### 2. Accounts CRUD
- **`POST /api/v1/accounts`**: Create a new Bank Account or Credit Card.
- **`GET /api/v1/accounts`**: List all accounts (optional query param: `?include_in_net_worth=true`).
- **`GET /api/v1/accounts/{id}`**: Get specific account details.
- **`PATCH /api/v1/accounts/{id}`**: Update account attributes (balance, name, exclusion toggle).
- **`DELETE /api/v1/accounts/{id}`**: Remove an account.

### 3. Transactions & Category Analytics
- **`POST /api/v1/transactions`**: Log Income or Expense (automatically updates target account balance).
- **`GET /api/v1/transactions`**: List transactions (filter by `account_id`, `category`, `transaction_type`).
- **`GET /api/v1/transactions/{id}`**: Get transaction details.
- **`DELETE /api/v1/transactions/{id}`**: Delete transaction and reverse the account balance adjustment.
- **`GET /api/v1/transactions/analytics/categories`**: Return category breakdown and percentage spending.

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
