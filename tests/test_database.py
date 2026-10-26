from unittest.mock import patch
import sys
from app.database import get_db, get_engine_url

def test_tc_db_001_get_db_generator():
    """TC-DB-001: Database session generator yields clean session and closes."""
    db_gen = get_db()
    session = next(db_gen)
    assert session is not None
    try:
        next(db_gen)
    except StopIteration:
        pass

def test_tc_db_002_ulid_format():
    """TC-DB-002: Verify generate_ulid returns a valid 26-character Base32 string."""
    from app.models import generate_ulid
    ulid_str = generate_ulid()
    assert isinstance(ulid_str, str)
    assert len(ulid_str) == 26

def test_tc_db_003_get_engine_url_postgres_legacy():
    """TC-DB-003: Converts legacy postgres:// prefix to postgresql://."""
    url = "postgres://user:pass@aws.pooler.supabase.com:6543/postgres"
    assert get_engine_url(url).startswith("postgresql://")

def test_tc_db_004_get_engine_url_psycopg_fallback_to_psycopg2():
    """TC-DB-004: Falls back to postgresql+psycopg2:// if psycopg (v3) is missing."""
    with patch.dict(sys.modules, {"psycopg": None}):
        url = "postgresql+psycopg://user:pass@host:5432/db"
        assert get_engine_url(url) == "postgresql+psycopg2://user:pass@host:5432/db"

def test_tc_db_005_get_engine_url_psycopg2_fallback_to_psycopg():
    """TC-DB-005: Falls back to postgresql+psycopg:// if psycopg2 is missing."""
    with patch.dict(sys.modules, {"psycopg2": None}):
        url = "postgresql+psycopg2://user:pass@host:5432/db"
        assert get_engine_url(url) == "postgresql+psycopg://user:pass@host:5432/db"

def test_tc_db_006_safe_account_type_case_resilience():
    """TC-DB-006: SafeAccountType handles upper and lower case DB enum strings."""
    from app.models import SafeAccountType, AccountType
    col = SafeAccountType()
    assert col.process_result_value("investment", None) == AccountType.INVESTMENT
    assert col.process_result_value("INVESTMENT", None) == AccountType.INVESTMENT
    assert col.process_result_value("bank", None) == AccountType.BANK
    assert col.process_result_value("BANK", None) == AccountType.BANK
    assert col.process_result_value("credit_card", None) == AccountType.CREDIT_CARD
    assert col.process_result_value("CREDIT_CARD", None) == AccountType.CREDIT_CARD
    assert col.process_bind_param(AccountType.BANK, None) == "BANK"
    assert col.process_bind_param("investment", None) == "INVESTMENT"

def test_tc_db_007_account_response_null_timestamps():
    """TC-DB-007: AccountResponse serializes records with null timestamps without error."""
    from app.schemas import AccountResponse
    from app.models import AccountType
    resp = AccountResponse(
        id="01TEST1234567890ABCDEF1234",
        name="Null Date Account",
        account_type=AccountType.BANK,
        balance=1500.0,
        include_in_net_worth=True,
        created_at=None,
        updated_at=None
    )
    assert resp.created_at is None
    assert resp.updated_at is None
    assert resp.name == "Null Date Account"


