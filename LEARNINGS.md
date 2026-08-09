# 🎓 Backend & Systems Architecture Learnings

A living guide documenting key engineering lessons learned during the construction and deployment of **Expensify** — a full-stack personal finance tracker with FastAPI, Angular, Supabase, Docker, and Render.

---

## 1. Web Frameworks vs. Web Servers (FastAPI vs. Uvicorn)

```
[ Internet / HTTP ] ──► [ Uvicorn (ASGI Server) ] ──► [ FastAPI (App Framework) ]
```

- **FastAPI**: Routes, business logic, schema validation, OpenAPI docs. Does NOT handle TCP sockets.
- **Uvicorn**: Listens on ports, manages TCP connections, parses HTTP, hands off to FastAPI.

---

## 2. Request Lifecycle & Modular Layering

```
Client (Browser/Phone)
  ▼
main.py (CORS + Router registration)
  ▼
routers/*.py (Route handlers, business logic)
  ├── schemas.py (Pydantic: validates input, shapes output)
  ├── auth.py (get_current_user JWT dependency)
  └── models.py (SQLAlchemy: Python ↔ SQL rows)
  ▼
database.py (get_db session lifecycle)
  ▼
Supabase PostgreSQL
```

---

## 3. Database Connections & Connection Pooling

- **Direct Connection (port 5432)**: IPv6-only on Supabase — fails on standard IPv4 networks.
- **Transaction Pooler (port 6543)**: IPv4-compatible proxy. Reserves DB connection only for the duration of a single SQL transaction then releases it immediately. Ideal for serverless APIs.

---

## 4. Row Level Security (RLS) vs. Application-Level Isolation

Two different approaches to multi-tenancy:

| Approach | Where enforced | How |
|---|---|---|
| **Supabase RLS** | PostgreSQL engine | `USING (user_id = auth.uid())` policies — enforced even for direct SQL |
| **Application-level isolation** (our approach) | FastAPI routers | `filter(Account.user_id == current_user.id)` in every query |

**Why we chose application-level**: Our backend uses the PostgreSQL superuser connection string (bypasses RLS by design). All data scoping is enforced in FastAPI router queries — every endpoint filters by the authenticated user's ID.

---

## 5. Supabase Auth: Secret Key vs. Anon Public Key

| Key Type | Usage | Where |
|---|---|---|
| `sb_secret_...` (service_role) | Backend only — bypasses RLS, admin operations | FastAPI `app/config.py` via env var |
| `eyJhbGci...` (anon public) | Frontend browser — safe to expose, rate-limited | Angular `auth.service.ts` |

**Lesson**: Supabase blocks browser usage of the secret key with `"Forbidden use of secret API key in browser"`. Always use the `anon` public key in any client-side code.

---

## 6. JWT Authentication Flow (Supabase + FastAPI)

```
1. Angular calls supabase.auth.signInWithPassword()
2. Supabase returns { session: { access_token: "eyJ..." } }
3. authInterceptor attaches Authorization: Bearer <access_token> to all API calls
4. FastAPI get_current_user() decodes JWT (without signature verification — Supabase handles that)
5. Extracts sub (UUID) and email from JWT payload
6. Auto-provisions User row in DB on first login
7. All queries filtered by user.id → per-user data isolation
```

**Key insight**: `jwt.decode(token, options={"verify_signature": False})` is safe here because the JWT is already signed and verified by Supabase before being issued to the client. The backend trusts Supabase as the identity provider.

---

## 7. Angular Signals & Async Auth Race Condition

**The Bug**: `ngOnInit()` is synchronous. Supabase `initAuth()` is async. On page reload:
1. `ngOnInit()` runs → checks `isAuthenticated()` → `false` (session not loaded yet)
2. `refreshAll()` is never called
3. Dashboard shows 0 accounts even though user is logged in

**The Fix**: Use Angular `effect()` instead — it reactively re-runs whenever a signal changes:
```typescript
constructor() {
  effect(() => {
    if (this.auth.isAuthenticated()) {
      this.api.refreshAll();
    }
  });
}
```
`effect()` fires again when `isAuthenticated` transitions from `false` → `true` (after Supabase resolves the stored session). Zero race condition.

---

## 8. Docker Multi-Stage Builds & Angular CLI Node Version

**The Build Failure**:
```
The Angular CLI requires a minimum Node.js version of v22.22.3
Node.js version v20.20.2 detected.
```

**The Fix**: Specify `node:22-slim` in Stage 1 of the Dockerfile. Angular 18+ requires Node 22+.

**Lesson**: Always check the Angular CLI release notes for Node.js minimum version requirements before pinning a base image.

---

## 9. Git Angular Cache Merge Conflicts

`frontend/.angular/cache/` contains binary lock files and TypeScript build snapshots that change with every local `ng build`. Tracking these in git causes near-guaranteed merge conflicts on every PR.

**Fix**: Add `frontend/.angular/` to `.gitignore` and `git rm -rf --cached frontend/.angular/` to untrack.

---

## 10. Automated Testing with Auth Dependencies

When endpoints require authentication (`get_current_user` dependency), tests will return `401 Unauthorized` unless the dependency is overridden.

**Pattern for FastAPI test auth override**:
```python
def override_get_current_user():
    return db_session.query(User).filter(User.id == TEST_USER_ID).first()

app.dependency_overrides[get_current_user] = override_get_current_user
```

**Critical detail**: Always return a **fresh DB-bound instance** from the session (not a detached Python object). Returning a detached `User` object causes `sqlalchemy.orm.exc.DetachedInstanceError` when SQLAlchemy tries to lazy-load relationships.

---

## 11. Supabase Storage Budget (500 MB Free Tier)

- ~50 MB is consumed by the Supabase engine baseline (`auth`, `storage`, `vault` schemas + extensions).
- ~450 MB remains for user data.
- A text transaction record is ~400 bytes → ~1,125,000 transactions fit in the remaining budget.
- For 1–3 users with normal usage (~500 transactions/month each), the free tier lasts **62+ years**.

---

## 12. Supabase User Provisioning Pattern

Supabase manages auth in its own `auth.users` table. Our app maintains a separate `public.users` table. The `get_current_user` dependency bridges these:

```python
user = db.query(User).filter(User.id == user_id).first()
if not user:
    # First login — auto-provision row in public.users
    user = User(id=user_id, email=email)
    db.add(user)
    db.commit()
```

This means a user's app data (accounts, transactions) is only accessible after their first authenticated API call, not at the moment of Supabase sign-up.
