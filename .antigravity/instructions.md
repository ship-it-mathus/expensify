# 🛡️ Antigravity Workspace Rules for Expensify

## 1. 1000% Quality & Test Standards
- **Mandatory Test Coverage**: No feature, endpoint, or schema change may be committed without corresponding automated unit and integration tests.
- **Numbered Test Case Mapping (`TESTCASES.md`)**:
  - Every single test function in `tests/` must specify an explicit Test Case ID in its docstring and function name (e.g., `TC-ACC-001`, `TC-CAT-001`, `TC-ANA-001`).
  - Every Test Case ID must be cataloged in [`TESTCASES.md`](file:///Users/mathews/Projects/Expensify/TESTCASES.md) with test intent, target endpoint, expected status code, and clickable code links.
- **DB Isolation**: Tests must run against isolated in-memory SQLite fixtures (`conftest.py`). Never touch production database in unit tests.
- **Zero Warning & High Coverage Policy**: All tests must run warning-free with high test coverage (`pytest --cov=app`).

## 2. Git & Branch Protection Workflow (PR Required)
- **Branch Protection Active**: Direct pushes to `main` branch are blocked on GitHub.
- **Feature Branch Workflow**: All new features must be developed on a dedicated feature branch (e.g., `feature/<name>`).
- **Pull Request Protocol**: Pushes must target `origin feature/<name>`, followed by opening a Pull Request on GitHub for review and merging into `main`.
