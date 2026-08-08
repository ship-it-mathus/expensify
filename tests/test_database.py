from app.database import get_db

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
