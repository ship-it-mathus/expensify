# 🛡️ Antigravity Workspace Rules for Expensify

## 1. 1000% Quality & Test Standards
- **Mandatory Test Coverage**: No feature, endpoint, or schema change may be committed without corresponding automated unit and integration tests.
- **Numbered Test Case Mapping (`TESTCASES.md`)**:
  - Every single test function in `tests/` must specify an explicit Test Case ID in its docstring and function name (e.g., `TC-ACC-001`, `TC-CAT-001`, `TC-ANA-001`).
  - Every Test Case ID must be cataloged in [`TESTCASES.md`](file:///Users/mathews/Projects/Expensify/TESTCASES.md) with test intent, target endpoint, expected status code, and clickable code links.
- **DB Isolation**: Tests must run against isolated in-memory SQLite fixtures (`conftest.py`). Never touch production database in unit tests.
- **Zero Warning & High Coverage Policy**: All tests must run warning-free with high test coverage (`pytest --cov=app`).

## 2. Mandatory Git & Branch Protection Protocol (PR Required - NO DIRECT MAIN PUSHES)
- **Strict Pull Request Protocol**: NEVER push directly to `main` or bypass branch protection rules, even with admin credentials.
- **Feature Branch Mandate**: All features, bug fixes, and layout tweaks MUST be committed to dedicated feature branches (e.g. `feat/<name>`).
- **Pull Request Link Delivery**: Every update MUST be pushed to `origin feat/<name>` and presented to the user as a clickable GitHub Pull Request link for user review and merging into `main`.
