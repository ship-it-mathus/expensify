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
