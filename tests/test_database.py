from app.database import get_db

def test_get_db_generator():
    db_gen = get_db()
    session = next(db_gen)
    assert session is not None
    # Clean up generator
    try:
        next(db_gen)
    except StopIteration:
        pass
