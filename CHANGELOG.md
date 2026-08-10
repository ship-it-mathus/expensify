# 📝 Expensify Changelog

All notable changes to this project are documented here.
Format: `[PR #] — type: description | Date`

---

## [Unreleased]

---

## [PR #26] — feat/fix: email confirmation flow, donut chart fix, auth button guard | 2026-08-10

### feat: Email Confirmation Flow
- `feat` `auth.service.ts`: Added `pendingConfirmation`, `pendingEmail`, `resendSuccess`, `isResending` Angular signals to drive the confirmation screen
- `feat` `auth.service.ts`: `handleAuthCallback()` runs on every page load — exchanges Supabase PKCE `?code=...` token or applies implicit `#access_token=...` hash so clicking the email link auto-logs the user into the dashboard
- `feat` `auth.service.ts`: `signUp()` now sets `pendingConfirmation=true` when Supabase returns no session (email unconfirmed)
- `feat` `auth.service.ts`: `resendConfirmationEmail()` with 4-second auto-clear success state; `cancelConfirmation()` resets all pending state
- `feat` `app.ts`: `handleAuthSubmit()` skips `refreshAll()` on sign-up when confirmation is pending (no session exists yet)
- `feat` `app.ts`: `handleResendConfirmation()` and `handleCancelConfirmation()` wrappers
- `feat` `app.html`: Two-state auth UI — pulsing envelope "Check your inbox" screen (email pill, resend button, back link) and login/signup form with inline hint text
- `feat` `styles.css`: `pulse-ring` `@keyframes` animation for the confirmation envelope icon

### fix: Donut chart shows "No expense data this month" despite having data
- `fix` `charts.component.ts`: `DonutChartComponent` was built at `AfterViewInit` with empty data (analytics not loaded yet); `ngOnChanges` pushed data in but Chart.js failed to repaint after empty initialisation
- `fix` Detect empty→has-data transition in `ngOnChanges` and `destroy()` + rebuild the chart for a clean render instead of calling `update()`

### fix: Transaction + Transfer buttons visible when logged out
- `fix` `app.html`: Action buttons in top app bar had no auth guard — wrapped in `@if (auth.isAuthenticated())` so they only appear for signed-in users

---

## [PR #25b] — feat: Chart.js analytics tab | 2026-08-10

- `feat` Added Chart.js powered analytics tab with Donut chart (category spending breakdown) and Bar chart (monthly income vs expense vs savings)
- `feat` New standalone Angular components: `DonutChartComponent`, `BarChartComponent` in `frontend/src/app/components/charts.component.ts`
- `feat` Savings Rate Hero card redesigned with 3 coloured mini-tiles (Income 🟢 / Expense 🔴 / Saved 🟣)
- `feat` Category breakdown list below donut chart with ₹ amounts and % per category

---

## [PR #25] — docs: Phase 6 recap — README, STATUS, LEARNINGS | 2026-08-10

- `docs` Full rewrite of `README.md` — added auth architecture diagram, tech stack table, live links, API usage examples
- `docs` `STATUS.md` updated to Phase 6 — added milestones, DB schema table, auth flow, Phase 7 roadmap
- `docs` `LEARNINGS.md` expanded with 6 new lessons: Supabase key types, JWT flow, Angular `effect()` race condition, Docker Node version requirement, git Angular cache conflicts, SQLAlchemy DetachedInstanceError pattern

---

## [PR #24] — fix: auth race condition with effect() | 2026-08-10

- `fix` Replaced `ngOnInit()` synchronous `isAuthenticated()` check with Angular `effect()` in constructor
- `fix` Resolved "0 Active Accounts on page reload" bug — `effect()` fires reactively when Supabase session restores from storage

---

## [PR #23] — feat: per-user data isolation across all API endpoints | 2026-08-10

- `feat` All 4 routers (`accounts`, `transactions`, `categories`, `analytics`) now filter queries by `user_id`
- `feat` `categories`: global system defaults (`user_id = NULL`) shown to all users; custom categories scoped to owner only
- `feat` New records (accounts, transactions) stamped with `user_id` on creation
- `fix` `conftest.py` updated to inject mock authenticated user via `get_current_user` dependency override — 32/32 tests passing

---

## [PR #22] — fix: add frontend/.angular/ to .gitignore | 2026-08-10

- `fix` Added `frontend/.angular/` to `.gitignore` to permanently stop PR merge conflicts on Angular binary cache files
- `fix` Untracked and removed all committed Angular cache files from git history

---

## [PR #21] — fix: purge unused Google auth dead code | 2026-08-10

- `fix` Removed `handleGoogleLogin()` from `app.ts`
- `fix` Removed `signInWithGoogle()` from `auth.service.ts`

---

## [PR #20] — fix: DB user_id column migration + startup auth guard | 2026-08-10

- `fix` Executed PostgreSQL `ALTER TABLE` migration: added `user_id VARCHAR(36)` to `accounts`, `transactions`, `categories` tables in Supabase
- `fix` `ngOnInit()` now guards `refreshAll()` behind `isAuthenticated()` check (later replaced by `effect()` in PR #24)

---

## [PR #19] — feat: Swagger UI Authorize button | 2026-08-10

- `feat` Registered `HTTPBearer` security scheme in `app/auth.py`
- `feat` `/docs` Swagger UI now shows green 🔓 **Authorize** button — paste JWT token to test auth-guarded endpoints

---

## [PR #18] — fix: use Supabase anon public key in browser | 2026-08-10

- `fix` Replaced `sb_secret_...` service role key with `eyJhbGci...` anon public key in `auth.service.ts`
- `fix` Resolved `"Forbidden use of secret API key in browser"` Supabase error

---

## [PR #16] — fix: disable Google OAuth button | 2026-08-10

- `fix` Removed `Continue with Google` button, `or` divider from Auth login card in `app.html`

---

## [PR #15] — fix: upgrade Dockerfile to node:22-slim | 2026-08-10

- `fix` Upgraded Docker Stage 1 builder from `node:20-slim` to `node:22-slim`
- `fix` Resolved Angular CLI build error: `"minimum Node.js version of v22.22.3 required"`

---

## [PR #14] — fix: clean static cache + document live URL | 2026-08-09

- `fix` Removed legacy tracked `app/static/` bundle files (`main-JQRVI4OQ.js`, `index.html`) from git
- `fix` Updated `Dockerfile` to `RUN rm -rf ./app/static` before copying fresh Angular build
- `docs` Added live URL `https://expensify-api-fj8q.onrender.com/` to `README.md`, `PROJECT.md`, `STATUS.md`

---

## [PR #13] — ux: 8 UI/UX improvements | 2026-08-09

- `ux` Removed `+`/`-` prefixes from transaction amounts; kept green/red colour coding only
- `ux` Made `.top-app-bar` sticky with `backdrop-filter: blur(12px)`
- `ux` Removed "Live Net Worth & Financial Tracking" subtitle text
- `ux` Account balance chips on Add/Edit Transaction: Bank = green, Credit Card = red
- `ux` Simplified amount placeholder to `"Enter amount"` (removed `e.g. 500`)
- `ux` Edit Transaction page: correct `"Edit Transaction"` heading + `"Back to Transactions"` button
- `ux` Transfer modal: Execute Transfer button disabled until `from`, `to` (must differ), and `amount > 0` filled
- `ux` Transaction dates formatted as `d MMM • HH:mm` (24-hour time)

---

## [PR #12] — feat: Angular Supabase Auth UI | 2026-08-09

- `feat` Created `AuthService` with Angular Signals (`session`, `user`, `isAuthenticated`, `isLoading`)
- `feat` Created `authInterceptor` — attaches `Authorization: Bearer <token>` to all API calls
- `feat` Registered `authInterceptor` in `app.config.ts`
- `feat` Built Slate dark Auth login/signup card with email + password form in `app.html`
- `feat` Added user email badge + Sign Out button in top app bar header

---

## [PR #11] — feat: Supabase Auth backend user model | 2026-08-09

- `feat` Added `User` SQLAlchemy model (`users` table) in `app/models.py`
- `feat` Added `user_id` foreign key columns to `Account`, `Transaction`, `Category` models
- `feat` Created `get_current_user` FastAPI dependency in `app/auth.py` — decodes Supabase JWT, auto-provisions user row
- `feat` Added `X-User-ID` dev header fallback for local testing without JWT
- `test` Added `TC-USR-001`, `TC-USR-002`, `TC-USR-003` unit tests — 32/32 passing

---

## [PR #10] — docs: strict Pull Request git workflow rules | 2026-08-09

- `docs` Created `.agents/rules/git-workflow.md` — prohibits direct pushes to `main`, mandates feature branches + PR links
- `docs` Updated `.antigravity/instructions.md` with PR policy

---

## [PR #9] — feat: Angular frontend + transaction edit | 2026-08-08

- `feat` Full Angular 18 mobile-first SPA with Slate dark theme
- `feat` Dashboard overview, transactions feed, add/edit transaction, analytics, settings tabs
- `feat` Transfer modal with from/to account selectors
- `feat` Single-port unified server: Angular SPA served via FastAPI `StaticFiles` mount

---

## [Earlier PRs #1–#8] — Initial Backend, Tests, Docker, Supabase | 2026-08-07 to 2026-08-08

- `feat` FastAPI modular backend: accounts, transactions, categories, analytics, transfers
- `feat` Supabase PostgreSQL integration via Transaction Pooler (port 6543)
- `feat` Automated pytest suite with in-memory SQLite isolation (27 → 32 test cases)
- `feat` Docker multi-stage build + Render deployment
- `feat` ULID primary keys, Pydantic schemas, auto balance adjustment engine
- `feat` Inter-account transfers with automatic debit/credit pair creation
- `feat` Monthly analytics + category spending breakdown endpoints
