# 💳 Expensify

> A full-stack personal finance tracker with **Angular 18**, **FastAPI**, **Supabase Auth**, and **Docker**. Multi-user, mobile-first, and live on the web.

[![Live Web App](https://img.shields.io/badge/Live_App-Expensify-purple)](https://expensify-api-fj8q.onrender.com/)
[![Production API](https://img.shields.io/badge/API_Docs-Swagger_UI-brightgreen)](https://expensify-api-fj8q.onrender.com/docs)
[![Database](https://img.shields.io/badge/Database-Supabase_PostgreSQL-blue)](https://supabase.com)
[![Tests](https://img.shields.io/badge/Tests-32_Passed-success)](TESTCASES.md)
[![Auth](https://img.shields.io/badge/Auth-Supabase_JWT-orange)](https://supabase.com/docs/guides/auth)

---

## 🌟 Features

- 🔐 **Multi-User Auth**: Email/password sign-up & sign-in via Supabase Auth. JWT verified on FastAPI backend. Each user sees only their own data.
- 🏦 **Multi-Account Management**: Bank accounts and credit cards in one dashboard.
- 💡 **Actual Liquid Cash Calculation**:
  $$\text{Actual Liquid Money} = \sum_{\text{Bank Balances}} - \sum_{\text{Credit Card Dues}}$$
- 🙈 **Account Hiding**: Toggle `include_in_net_worth = false` to exclude accounts (e.g. Emergency Fund) from net worth.
- ⚡ **Auto Balance Engine**: Logging a transaction automatically adjusts account balances in real-time.
- 🔀 **Inter-Account Transfers**: Pay off Credit Card bills or move funds between accounts in one call.
- 🏷️ **Categories**: Pre-seeded global defaults (Salary, Food, Rent, etc.) + user-created custom categories.
- 📊 **Monthly Analytics**: Income vs Expense totals, net savings rate, category spending breakdown.
- 📱 **Mobile-First Angular UI**: Slate dark theme, sticky app bar, glassmorphism cards, 24-hour time display.

---

## 🚀 Live Application

👉 **[https://expensify-api-fj8q.onrender.com/](https://expensify-api-fj8q.onrender.com/)**

**API Docs (Swagger UI)** — click the green 🔓 **Authorize** button to test authenticated endpoints:
👉 **[https://expensify-api-fj8q.onrender.com/docs](https://expensify-api-fj8q.onrender.com/docs)**

---

## 🔐 Auth Architecture

```
Angular (Browser)
  │
  ├── Supabase Auth SDK (anon public key)
  │     └── signInWithPassword() → session + JWT access_token
  │
  ├── authInterceptor → Authorization: Bearer <jwt> on all API calls
  │
  └── FastAPI (Render)
        └── get_current_user() → decodes JWT → auto-provisions user row
              └── All DB queries filtered by user_id
```

---

## 💡 API Usage Examples

### Check Net Available Cash
```bash
curl -H "Authorization: Bearer <your_jwt>" \
  https://expensify-api-fj8q.onrender.com/api/v1/summary
```
```json
{
  "total_bank_balance": 125000.0,
  "total_credit_card_dues": 14500.0,
  "actual_liquid_money": 110500.0,
  "currency": "INR"
}
```

### Log an Expense
```json
POST /api/v1/transactions
{
  "account_id": "<your_account_id>",
  "transaction_type": "expense",
  "amount": 450.0,
  "category": "food",
  "description": "Dinner at Swiggy"
}
```

### Pay Credit Card Bill (Transfer)
```json
POST /api/v1/transfers
{
  "from_account_id": "<bank_id>",
  "to_account_id": "<credit_card_id>",
  "amount": 10000.0,
  "description": "July Credit Card Bill Payment"
}
```

---

## 🛠️ Local Setup

```bash
# 1. Clone & activate virtual environment
git clone https://github.com/ship-it-mathus/expensify.git
cd expensify
python3 -m venv venv && source venv/bin/activate

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env   # fill in DATABASE_URL, SUPABASE_URL, SUPABASE_SECRET

# 4. Build Angular frontend
cd frontend && npm ci && npx ng build
cp -r dist/expensify-angular/browser/* ../app/static/
cd ..

# 5. Run unified server (Angular + API on single port)
venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# 6. Run test suite (32 tests)
venv/bin/pytest -q
```

---

## 📐 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Angular 18, TypeScript, Vanilla CSS |
| Backend | FastAPI, Python 3.11, SQLAlchemy, Pydantic |
| Auth | Supabase Auth (JWT), Angular authInterceptor |
| Database | Supabase PostgreSQL (Transaction Pooler, port 6543) |
| Containerization | Docker (multi-stage: Node 22 build → Python 3.11 serve) |
| Hosting | Render (auto-deploy on `main` merge) |
| IDs | ULID (universally unique, lexicographically sortable) |

---

## 📖 Documentation

- [`STATUS.md`](STATUS.md) — Roadmap, milestones & deployment tracker
- [`LEARNINGS.md`](LEARNINGS.md) — Engineering lessons (auth, async, Docker, SQLAlchemy)
- [`PROJECT.md`](PROJECT.md) — Full technical specification & file map
- [`TESTCASES.md`](TESTCASES.md) — 32 cataloged test cases with code links
