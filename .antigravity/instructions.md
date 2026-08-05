# 🛡️ Antigravity Workspace Rules for Expensify

## 1000% Quality & Test Standards
1. **Mandatory Test Coverage**: No feature, endpoint, or schema change may be committed without corresponding automated unit and integration tests.
2. **Numbered Test Case Mapping (`TESTCASES.md`)**:
   - Every single test function in `tests/` must specify an explicit Test Case ID in its docstring and function name (e.g., `TC-ACC-001`, `TC-CAT-001`, `TC-ANA-001`).
   - Every Test Case ID must be cataloged in [`TESTCASES.md`](file:///Users/mathews/Projects/Expensify/TESTCASES.md) with:
     - Test ID & Title
     - Target Endpoint & Method
     - Test Intent & Boundary Conditions
     - Expected HTTP Status & Payload
     - Direct Clickable Link to the test implementation in `tests/`
3. **DB Isolation**: Tests must run against isolated in-memory SQLite fixtures (`conftest.py`). Never touch production database in unit tests.
4. **Zero Warning & High Coverage Policy**: All tests must run warning-free with high test coverage (`pytest --cov=app`).
