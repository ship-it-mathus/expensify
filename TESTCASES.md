# 🧪 Expensify Automated Test Case Matrix (`TESTCASES.md`)

This file catalogs every unit and integration test case implemented in the Expensify test suite. Each test case is assigned a unique Test ID (`TC-xxx-xxx`), linked directly to its test implementation file, and executed against an isolated in-memory database fixture (`tests/conftest.py`).

---

## 📊 Test Execution Summary

- **Total Test Cases**: 26
- **Pass Rate**: 100% (26/26 Passed)
- **Code Coverage**: 98%
- **Execution Time**: ~0.40 seconds

---

## 📂 Test Cases Catalog

### 🌐 1. Root & Health Check (`tests/test_main.py`)

| Test ID | Test Name | Description / Boundary Condition | Target Endpoint | Expected Status | Implementation Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-ROOT-001` | Root Health Check | Verifies root endpoint returns online status message and docs URL. | `GET /` | `200 OK` | [`test_tc_root_001_root_endpoint`](file:///Users/mathews/Projects/Expensify/tests/test_main.py#L1-L8) |

---

### 🔌 2. Database Session Lifecycle (`tests/test_database.py`)

| Test ID | Test Name | Description / Boundary Condition | Target Function | Expected Behavior | Implementation Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-DB-001` | Session Lifecycle | Verifies `get_db()` generator yields clean session and closes after request. | `app.database.get_db()` | Yields SQLAlchemy Session | [`test_tc_db_001_get_db_generator`](file:///Users/mathews/Projects/Expensify/tests/test_database.py#L3-L11) |

---

### 💳 3. Accounts & Net Worth Engine (`tests/test_accounts.py`)

| Test ID | Test Name | Description / Boundary Condition | Target Endpoint | Expected Status | Implementation Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-ACC-001` | Empty Net Worth Summary | Returns 0.0 balances and counts for empty database. | `GET /api/v1/summary` | `200 OK` | [`test_tc_acc_001_empty_net_worth_summary`](file:///Users/mathews/Projects/Expensify/tests/test_accounts.py#L3-L12) |
| `TC-ACC-002` | Create Bank Account | Creates a new Bank Account and returns assigned ID. | `POST /api/v1/accounts` | `201 Created` | [`test_tc_acc_002_create_bank_account`](file:///Users/mathews/Projects/Expensify/tests/test_accounts.py#L14-L31) |
| `TC-ACC-003` | Create Credit Card | Creates a new Credit Card Account for tracking dues. | `POST /api/v1/accounts` | `201 Created` | [`test_tc_acc_003_create_credit_card_account`](file:///Users/mathews/Projects/Expensify/tests/test_accounts.py#L33-L47) |
| `TC-ACC-004` | List Accounts & Filter | Lists accounts and filters by `include_in_net_worth`. | `GET /api/v1/accounts` | `200 OK` | [`test_tc_acc_004_list_accounts_and_filters`](file:///Users/mathews/Projects/Expensify/tests/test_accounts.py#L49-L69) |
| `TC-ACC-005` | Get Account by ID & 404 | Fetches single account details; returns 404 for missing ID. | `GET /api/v1/accounts/{id}` | `200 OK` / `404 Not Found` | [`test_tc_acc_005_get_account_by_id`](file:///Users/mathews/Projects/Expensify/tests/test_accounts.py#L71-L85) |
| `TC-ACC-006` | Update Account Details | Updates name/balance/exclusion; returns 404 for missing ID. | `PATCH /api/v1/accounts/{id}` | `200 OK` / `404 Not Found` | [`test_tc_acc_006_update_account`](file:///Users/mathews/Projects/Expensify/tests/test_accounts.py#L87-L105) |
| `TC-ACC-007` | Delete Account | Deletes account; verifies subsequent requests return 404. | `DELETE /api/v1/accounts/{id}` | `204 No Content` / `404` | [`test_tc_acc_007_delete_account`](file:///Users/mathews/Projects/Expensify/tests/test_accounts.py#L107-L121) |
| `TC-ACC-008` | Net Worth Calculation Math | Verifies math: $\text{Liquid} = \text{Bank} - \text{CreditCard}$ skipping hidden accounts. | `GET /api/v1/summary` | `200 OK` | [`test_tc_acc_008_net_worth_calculation_logic`](file:///Users/mathews/Projects/Expensify/tests/test_accounts.py#L123-L147) |
| `TC-ACC-009` | Account Specific Transactions | Returns transactions history filtered specifically for target account. | `GET /api/v1/accounts/{id}/transactions` | `200 OK` / `404 Not Found` | [`test_tc_acc_009_get_account_specific_transactions`](file:///Users/mathews/Projects/Expensify/tests/test_accounts.py#L149-L162) |

---

### 💸 4. Transactions & Transfers Engine (`tests/test_transactions.py`)

| Test ID | Test Name | Description / Boundary Condition | Target Endpoint | Expected Status | Implementation Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-TX-001` | Bank Expense Balance Reduction | Logging an expense on a Bank account automatically reduces bank balance. | `POST /api/v1/transactions` | `201 Created` | [`test_tc_tx_001_expense_on_bank_account_reduces_balance`](file:///Users/mathews/Projects/Expensify/tests/test_transactions.py#L1-L24) |
| `TC-TX-002` | Bank Income Balance Addition | Logging income on a Bank account automatically increases bank balance. | `POST /api/v1/transactions` | `201 Created` | [`test_tc_tx_002_income_on_bank_account_increases_balance`](file:///Users/mathews/Projects/Expensify/tests/test_transactions.py#L26-L44) |
| `TC-TX-003` | Credit Card Dues & Payments | Expense increases credit card due; payment decreases credit card due. | `POST /api/v1/transactions` | `201 Created` | [`test_tc_tx_003_expense_and_payment_on_credit_card`](file:///Users/mathews/Projects/Expensify/tests/test_transactions.py#L46-L75) |
| `TC-TX-004` | Delete Bank Income Reversal | Deleting a bank income transaction automatically restores previous balance. | `DELETE /api/v1/transactions/{id}` | `204 No Content` | [`test_tc_tx_004_delete_bank_income_transaction`](file:///Users/mathews/Projects/Expensify/tests/test_transactions.py#L77-L90) |
| `TC-TX-005` | List Transactions Filters | Query filters by `account_id`, `category`, and `transaction_type`. | `GET /api/v1/transactions` | `200 OK` | [`test_tc_tx_005_list_transactions_filters`](file:///Users/mathews/Projects/Expensify/tests/test_transactions.py#L92-L108) |
| `TC-TX-006` | Empty Category Analytics | Returns 0.0 total expense and empty categories array. | `GET /api/v1/transactions/analytics/categories` | `200 OK` | [`test_tc_tx_006_empty_category_breakdown`](file:///Users/mathews/Projects/Expensify/tests/test_transactions.py#L110-L115) |
| `TC-TX-007` | Category Spending Breakdown | Calculates total spending per category and exact spending percentages. | `GET /api/v1/transactions/analytics/categories` | `200 OK` | [`test_tc_tx_007_category_spending_breakdown_with_account_filter`](file:///Users/mathews/Projects/Expensify/tests/test_transactions.py#L117-L131) |
| `TC-TX-008` | Inter-Account Bill Transfer | Transfer from Bank ➔ Credit Card reduces bank balance and reduces credit card due. | `POST /api/v1/transfers` | `201 Created` | [`test_tc_tx_008_transfer_bank_to_credit_card_bill_payment`](file:///Users/mathews/Projects/Expensify/tests/test_transactions.py#L133-L154) |
| `TC-TX-009` | Transfer Validation Errors | Prevents same-account transfers (422) and missing source/dest accounts (404). | `POST /api/v1/transfers` | `422` / `404 Not Found` | [`test_tc_tx_009_transfer_validation_errors`](file:///Users/mathews/Projects/Expensify/tests/test_transactions.py#L156-L173) |

---

### 🎨 5. Categories Management (`tests/test_categories.py`)

| Test ID | Test Name | Description / Boundary Condition | Target Endpoint | Expected Status | Implementation Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-CAT-001` | Category Auto-Seeding | Verifies default Paisa categories are seeded automatically on first call. | `GET /api/v1/categories` | `200 OK` | [`test_tc_cat_001_list_categories_with_auto_seeding`](file:///Users/mathews/Projects/Expensify/tests/test_categories.py#L1-L10) |
| `TC-CAT-002` | Category Income/Expense Filter | Filters categories by `category_type=income` vs `category_type=expense`. | `GET /api/v1/categories` | `200 OK` | [`test_tc_cat_002_filter_categories_by_type`](file:///Users/mathews/Projects/Expensify/tests/test_categories.py#L12-L22) |
| `TC-CAT-003` | Create Custom Category | Creates user custom category marked `is_default=false`. | `POST /api/v1/categories` | `201 Created` | [`test_tc_cat_003_create_custom_category`](file:///Users/mathews/Projects/Expensify/tests/test_categories.py#L24-L36) |
| `TC-CAT-004` | Prevent Duplicate Categories | Returns HTTP 400 when attempting to create duplicate category under same type. | `POST /api/v1/categories` | `400 Bad Request` | [`test_tc_cat_004_prevent_duplicate_category`](file:///Users/mathews/Projects/Expensify/tests/test_categories.py#L38-L43) |
| `TC-CAT-005` | Custom Category Deletion Rules | Allows deleting custom categories; blocks deleting system default categories (400). | `DELETE /api/v1/categories/{id}` | `204` / `400` / `404` | [`test_tc_cat_005_delete_custom_category_rules`](file:///Users/mathews/Projects/Expensify/tests/test_categories.py#L45-L62) |

---

### 📈 6. Monthly Analytics & Insights (`tests/test_analytics.py`)

| Test ID | Test Name | Description / Boundary Condition | Target Endpoint | Expected Status | Implementation Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `TC-ANA-001` | Monthly Analytics Empty State | Returns 0.0 income/expense/savings for month with no transactions. | `GET /api/v1/analytics/monthly` | `200 OK` | [`test_tc_ana_001_monthly_analytics_empty_state`](file:///Users/mathews/Projects/Expensify/tests/test_analytics.py#L1-L10) |
| `TC-ANA-002` | Income vs Expense Savings Rate | Calculates total income, total expense, net savings, and savings rate percentage. | `GET /api/v1/analytics/monthly` | `200 OK` | [`test_tc_ana_002_monthly_analytics_income_expense_savings`](file:///Users/mathews/Projects/Expensify/tests/test_analytics.py#L12-L34) |
