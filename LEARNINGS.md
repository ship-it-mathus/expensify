# 🎓 Backend & Systems Architecture Learnings

A comprehensive guide for Frontend Developers transitioning to Backend & Cloud Engineering, documented during the construction and deployment of the **Expensify API**.

---

## 1. Web Frameworks vs. Web Servers (FastAPI vs. Uvicorn)

### 💡 Core Concept
In Node.js/Express, the web server and application logic are often bundled together. In Python's modern async ecosystem, they are cleanly decoupled using **ASGI (Asynchronous Server Gateway Interface)**.

```
[ Internet / HTTP ] ──► [ Uvicorn (ASGI Web Server) ] ──► [ FastAPI (Application Framework) ]
```

- **FastAPI (Application Framework)**:
  - Writes business logic, routing, schema validation, and OpenAPI documentation.
  - Does **NOT** handle raw TCP/HTTP network sockets directly.
- **Uvicorn (ASGI Server)**:
  - Listens on network ports (e.g. `8000`), manages TCP socket connections, parses incoming raw HTTP packets into standard Python data structures (ASGI events), hands them to FastAPI, and returns HTTP responses to clients.

---

## 2. Request Lifecycle & Modular Layering

A production-grade backend relies on **Separation of Concerns**:

```
Client (Phone/Browser)
  │
  ▼
[ main.py ] ──► CORS & App Router
  │
  ▼
[ routers/accounts.py ] ──► Route Handlers & Math Logic
  │                   │
  │                   ├──► [ schemas.py ] (Validates Input & Formats Output)
  │                   │
  ▼                   ▼
[ database.py ] ──► [ models.py ] (Translates Python Objects ◄► SQL Rows)
  │
  ▼
[ PostgreSQL / Supabase ]
```

1. **`models.py` (SQLAlchemy)**: Defines database tables, data types, primary keys, and foreign keys.
2. **`schemas.py` (Pydantic)**: Defines API payloads. Prevents internal database IDs/hashes from leaking, validates input types before execution.
3. **`database.py` (Session Lifecycle)**: Provides thread-safe DB sessions (`get_db` dependency) that open per request and close automatically upon completion.

---

## 3. Database Connections & Connection Pooling

### 🌐 Direct Connection vs. Connection Pooler
Connecting a serverless/cloud backend to a relational database introduces connection overhead.

- **Direct Connection (`db.[ref].supabase.co:5432`)**:
  - Requires opening a persistent TCP connection per client.
  - Direct hostnames are often **IPv6-only** in modern cloud infrastructure, failing on standard IPv4 networks without IPv6 support.
- **Connection Pooler (`[region].pooler.supabase.com:6543`)**:
  - Acts as a high-throughput proxy sitting in front of PostgreSQL.
  - Accepts incoming IPv4 requests and reuses a small, pre-warmed pool of database connections.

### 🔄 Session Pooling vs. Transaction Pooling
- **Session Pooling**: A client reserves a DB connection for the entire duration of a session. Limited concurrent connections.
- **Transaction Pooling (Port 6543)**: A client reserves a DB connection **only for the execution of a single SQL transaction** (e.g. 2 milliseconds) and immediately releases it back to the pool. Ideal for serverless APIs and mobile applications.

---

## 4. Row Level Security (RLS) vs. Database Owner

- **Supabase Data API (REST/JS SDK)**: Queries sent via client-side SDKs are evaluated through Supabase's PostgREST gateway, enforcing **Row Level Security (RLS)** rules.
- **Direct SQL / SQLAlchemy (Port 6543)**: Backend servers connect using the database superuser connection string (`postgres`). Superuser SQL bypasses RLS policies, giving full read/write access.
- **Dashboard Visibility**: Disabling RLS (`ALTER TABLE accounts DISABLE ROW LEVEL SECURITY;`) or adding default policies ensures data remains visible in the Supabase Table Editor UI without restrictions.

---

## 5. Automated Testing & In-Memory Database Isolation

- **Test Isolation**: Never run automated test suites against production database instances.
- **Dependency Overriding**: In FastAPI testing, we override the `get_db` dependency in `conftest.py` to point to a temporary `sqlite:///:memory:` database.
- **Speed & Reliability**: 10 integration and unit tests run in **0.15 seconds**, ensuring instant feedback without network latency or state pollution.

---

## 6. Containerization & Cloud Deployment Architecture

- **`venv` vs. `Dockerfile`**:
  - **Local (`venv`)**: Manages environment dependencies on the developer machine.
  - **Cloud (`Dockerfile`)**: Package application logic, OS dependencies, and Python runtime into a reproducible container image.
- **Environment Secret Isolation**: Production secrets (like `DATABASE_URL`) are never committed to version control (`.env` in `.gitignore`). Instead, they are injected at runtime via cloud platform environment settings (Render/Koyeb).
- **Continuous Deployment (CD)**: Connecting Render to GitHub enables automated builds; every `git push` triggers container image rebuilds and deployment with zero manual intervention.
