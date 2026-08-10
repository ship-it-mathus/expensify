# 📌 Expensify Project Status & Progress Tracker

**Last Updated**: August 11, 2026
**Current Phase**: Phase 8 In Progress (Auth UX, Investments & Insights) 🟡
**Next Phase**: Phase 8 continued (Recurring Transactions, Budget Limits, PWA) 🚀

---

## 🔗 Quick Links

- **Live Web Application (Render)**: [https://expensify-api-fj8q.onrender.com/](https://expensify-api-fj8q.onrender.com/)
- **Live Production API Docs (Swagger UI)**: [https://expensify-api-fj8q.onrender.com/docs](https://expensify-api-fj8q.onrender.com/docs)
- **GitHub Repository**: [https://github.com/ship-it-mathus/expensify](https://github.com/ship-it-mathus/expensify)
- **Database**: Supabase PostgreSQL (Managed Cloud DB via Transaction Pooler port 6543)
- **Auth Provider**: Supabase Auth (Email/Password; JWT verified on backend)
- **Test Matrix**: [`TESTCASES.md`](./TESTCASES.md) (36 cataloged test cases, 36/36 passing)
- **Changelog**: [`CHANGELOG.md`](./CHANGELOG.md) (full PR-by-PR history)
- **Antigravity Quality Config**: [`.antigravity/instructions.md`](./.antigravity/instructions.md)

---

## 🎯 Completed Milestones

### ✅ Phase 1: Local Backend & Business Logic
- [x] FastAPI modular app architecture (`app/main.py`, `app/models.py`, `app/schemas.py`, `app/routers/`).
- [x] `GET /api/v1/summary` for net available liquid cash.
- [x] Account exclusion support (`include_in_net_worth = false`).
- [x] Full CRUD endpoints for Bank and Credit Card accounts.

### ✅ Phase 2: Cloud Database (Supabase)
- [x] Connected FastAPI to Supabase PostgreSQL via Transaction Pooler (Port 6543).
- [x] Auto-generated database tables via SQLAlchemy `Base.metadata.create_all()`.
- [x] Configured `DATABASE_URL` via environment variable (Render secret + local `.env`).

### ✅ Phase 3: Testing, Version Control & Production Deployment
- [x] Isolated automated test suite with **`pytest`** using in-memory SQLite fixtures.
- [x] Docker containerization (`Dockerfile`) with multi-stage build.
- [x] Deployed to Render — live at `expensify-api-fj8q.onrender.com`.
- [x] GitHub repository with strict **Pull Request policy** (no direct pushes to `main`).

### ✅ Phase 4: Paisa Feature Parity & 1000% Quality Standard
- [x] Categories Management & Pre-seeding (income/expense filters, default seed guard).
- [x] Monthly Analytics (`GET /api/v1/analytics/monthly`).
- [x] Inter-Account Transfers (`POST /api/v1/transfers`) with auto balance adjustment.
- [x] 27/27 test cases passing at 98% code coverage.

### ✅ Phase 5: Angular Mobile-First Dashboard
- [x] Full Angular 18 SPA frontend — transactions, accounts, analytics, categories.
- [x] Slate dark theme UI with glassmorphism cards.
- [x] Sticky top app bar, 24-hour time display, green/red account balance chips.
- [x] Transfer modal with execute button disabled until all fields filled.
- [x] Edit Transaction page with correct header, back button, and cancel routing.
- [x] Amount display without `+`/`-` prefix; colour-coded green/red only.
- [x] Single-port unified server: Angular SPA served by FastAPI static mount.

### ✅ Phase 6: Multi-User Auth, Data Isolation & Production Fixes
- [x] **Supabase Auth backend (PR #11)**: `User` model, `get_current_user` JWT dependency, auto-provisioning user rows on first login.
- [x] **Angular Auth UI (PR #12)**: `AuthService` (signals), `authInterceptor` (Bearer token), Slate login/signup card.
- [x] **Supabase anon public key (PR #18)**: Fixed "Forbidden use of secret API key in browser" error.
- [x] **Google OAuth removed (PR #16, #21)**: Removed unused `handleGoogleLogin` and `signInWithGoogle` to keep codebase clean.
- [x] **Node.js 22 Docker fix (PR #15)**: Upgraded Dockerfile Stage 1 to `node:22-slim` to meet Angular CLI minimum requirement.
- [x] **Angular cache gitignored (PR #22)**: Added `frontend/.angular/` to `.gitignore` — permanently prevents PR merge conflicts on binary cache files.
- [x] **Per-user data isolation (feat/user-data-isolation)**: All 4 routers (accounts, transactions, categories, analytics) now filter by `user_id`. Each user sees only their own data.
- [x] **Categories scoping**: Global system defaults (no `user_id`) shown to all users; custom categories scoped to owner only.
- [x] **Swagger UI Authorize button (PR #19)**: `HTTPBearer` security scheme registered — green 🔓 Authorize button in `/docs` for testing with JWT tokens.
- [x] **Auth startup race condition fixed (fix/auth-race-condition-effect)**: Replaced `ngOnInit` synchronous check with Angular `effect()` — correctly loads data after Supabase session restores on page reload.
- [x] **PostgreSQL schema migration**: Added `user_id VARCHAR(36)` columns to `accounts`, `transactions`, and `categories` tables in Supabase via `ALTER TABLE`.
- [x] **32/32 tests passing**: Updated `conftest.py` to inject mock authenticated user via `get_current_user` dependency override.

---

## 🔐 Auth Architecture

```
Browser (Angular)
  │
  ├── Supabase Auth JS SDK (anon public key: eyJhbGci...)
  │     └── signInWithPassword() → returns session + JWT access_token
  │
  ├── authInterceptor → attaches Authorization: Bearer <jwt> to every API call
  │
  └── FastAPI Backend (Render)
        └── get_current_user() dependency
              ├── Extracts Bearer JWT
              ├── Decodes sub (UUID) & email
              ├── Auto-provisions User row in DB on first login
              └── Returns User → all queries filtered by user.id
```

---

## 🗃️ Database Schema (Supabase PostgreSQL)

| Table | Key Columns | Notes |
|---|---|---|
| `users` | `id`, `email`, `full_name` | Auto-created on first JWT login |
| `accounts` | `id`, `user_id`, `name`, `account_type`, `balance` | Scoped per user |
| `transactions` | `id`, `user_id`, `account_id`, `amount`, `type`, `date` | Scoped per user |
| `categories` | `id`, `user_id`, `name`, `category_type`, `is_default` | `user_id=NULL` = global default |

---

## 💻 Quick Reference Commands

```bash
# Run unified local server (single port, FastAPI + Angular SPA)
venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload

# Build Angular production bundle
cd frontend && npx ng build
cp -r dist/expensify-angular/browser/* ../app/static/

# Run test suite
venv/bin/pytest -q

# Git workflow (all changes via PR — no direct pushes to main)
git checkout -b feat/your-feature
git push -u origin feat/your-feature
# → Open PR on GitHub → Merge
```

---

- [x] **Investment Account Type (PR #27)**: Option C architecture — added `AccountType.INVESTMENT`. Investment portfolios are tracked in `total_investment_balance` and automatically excluded from liquid net worth calculations.
- [x] **% Income Invested Analytic (PR #27)**: `GET /api/v1/analytics/investment` endpoint calculates monthly investment inflows (SIPs/transfers into investment accounts) as a percentage of total income.
- [x] **Rotating Insights Strip (PR #27)**: Built `InsightsCarouselComponent` in Angular that auto-cycles through fun/quick stats (Food today, Food this month, Fuel, Rent, Shopping, % income invested) every 10 seconds with a visual progress bar and smooth opacity fade.
- [x] **Add Account Modal (PR #27)**: Added "Add Account" button & modal in Settings tab supporting Bank Account, Credit Card, and Investment Portfolio creation.
- [x] **CHANGELOG.md**: Full PR-by-PR code changelog created.
- [x] **Rule enforced**: Docs (STATUS, README, LEARNINGS, CHANGELOG) updated with every PR going forward.

---

## 🔮 Upcoming Roadmap (Phase 8 Continued)

- [ ] **Recurring Transactions**: Auto-log monthly salary/rent entries.
- [ ] **Budget Limits per Category**: Alert when spending exceeds monthly budget.
- [ ] **Multi-Month Trend Chart**: Line chart showing income/expense trend over last 6 months.
- [ ] **PWA Support**: `manifest.json` + service worker for phone home screen install.
- [ ] **Password Reset**: Supabase magic link / OTP reset flow in the UI.
