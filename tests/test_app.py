import os
import sys
import tempfile
import sqlite3

import pytest

# Ensure project root is on sys.path so `import app` works when pytest runs.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app, get_db_connection


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Create a temporary database file
    db_file = tmp_path / "test_database.db"
    # Initialize schema
    with open('schema.sql') as f:
        sql = f.read()
    conn = sqlite3.connect(str(db_file))
    conn.executescript(sql)
    conn.commit()
    conn.close()

    # Monkeypatch DATABASE_PATH via environment so get_db_connection uses it
    monkeypatch.setenv('DATABASE_PATH', str(db_file))

    app.config['TESTING'] = True
    # Disable CSRF checks in tests
    app.config['DISABLE_CSRF'] = True
    with app.test_client() as client:
        yield client


def test_add_item(client):
    # POST to /add
    resp = client.post('/add', data={'title': 'Test Item', 'content': 'Test desc', 'price': '3.50'}, follow_redirects=True)
    assert resp.status_code == 200
    assert b'Item added successfully' in resp.data

    # Verify in DB
    conn = get_db_connection()
    cur = conn.execute('SELECT * FROM ShoppingList WHERE title = ?', ('Test Item',))
    row = cur.fetchone()
    conn.close()
    assert row is not None
    assert row['content'] == 'Test desc'


def test_delete_item(client):
    # Insert an item directly
    conn = get_db_connection()
    cur = conn.execute("INSERT INTO ShoppingList (title, content, price) VALUES (?, ?, ?)", ('ToDelete', 'temp', 1.0))
    conn.commit()
    item_id = cur.lastrowid
    conn.close()

    # Delete via POST (CSRF disabled in tests)
    resp = client.post(f'/delete/{item_id}', follow_redirects=True)
    assert resp.status_code == 200


def test_api_items(client):
    resp = client.get('/api/items?draw=1&start=0&length=10')
    assert resp.status_code == 200
    j = resp.get_json()
    assert 'data' in j
    assert 'recordsTotal' in j
