def test_tc_cat_001_list_categories_with_auto_seeding(client):
    """TC-CAT-001: Verify default categories are auto-seeded on first call."""
    res = client.get("/api/v1/categories")
    assert res.status_code == 200
    categories = res.json()
    assert len(categories) >= 15
    # Verify both income and expense categories exist
    types = {c["category_type"] for c in categories}
    assert "income" in types
    assert "expense" in types

def test_tc_cat_002_filter_categories_by_type(client):
    """TC-CAT-002: Verify category listing filters by income vs expense."""
    res_inc = client.get("/api/v1/categories?category_type=income")
    assert res_inc.status_code == 200
    for c in res_inc.json():
        assert c["category_type"] == "income"

    res_exp = client.get("/api/v1/categories?category_type=expense")
    assert res_exp.status_code == 200
    for c in res_exp.json():
        assert c["category_type"] == "expense"

def test_tc_cat_003_create_custom_category(client):
    """TC-CAT-003: Create a custom category."""
    payload = {
        "name": "Crypto Gains",
        "category_type": "income",
        "icon": "currency_bitcoin"
    }
    res = client.post("/api/v1/categories", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "Crypto Gains"
    assert data["category_type"] == "income"
    assert data["is_default"] is False

def test_tc_cat_004_prevent_duplicate_category(client):
    """TC-CAT-004: Prevent duplicate category creation under same type."""
    client.post("/api/v1/categories", json={"name": "Freelance Test", "category_type": "income"})
    dup_res = client.post("/api/v1/categories", json={"name": "Freelance Test", "category_type": "income"})
    assert dup_res.status_code == 400
    assert "already exists" in dup_res.json()["detail"].lower()

def test_tc_cat_005_delete_custom_category_rules(client):
    """TC-CAT-005: Delete custom category & block deleting default system categories."""
    # Create custom category
    create_res = client.post("/api/v1/categories", json={"name": "Custom Hobby", "category_type": "expense"})
    cat_id = create_res.json()["id"]

    # Delete custom category ➔ 204
    del_res = client.delete(f"/api/v1/categories/{cat_id}")
    assert del_res.status_code == 204

    # Delete default category ➔ 400 Bad Request
    default_cat = client.get("/api/v1/categories?category_type=income").json()[0]
    del_def_res = client.delete(f"/api/v1/categories/{default_cat['id']}")
    assert del_def_res.status_code == 400
    assert "cannot delete system default" in del_def_res.json()["detail"].lower()

    # Delete non-existing category ➔ 404
    del_404 = client.delete("/api/v1/categories/99999")
    assert del_404.status_code == 404
