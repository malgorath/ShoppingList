import os
import sqlite3
import secrets
from urllib.parse import quote_plus
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify


def get_db_connection(db_path=None):
    db = db_path or os.getenv('DATABASE_PATH', 'database.db')
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
# Load secret key from environment when available. Fallback to a dev key.
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# Simple session-based CSRF protection (lightweight alternative to Flask-WTF).
# Can be disabled in tests or environments via app.config['DISABLE_CSRF'] = True


@app.before_request
def ensure_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)


@app.context_processor
def inject_csrf_token():
    return {'csrf_token': session.get('csrf_token', '')}


def ensure_migrations():
    """Ensure database has the purchase_by column. This is a lightweight runtime migration."""
    conn = get_db_connection()
    cur = conn.cursor()
    # Check existing columns
    cur.execute("PRAGMA table_info(ShoppingList)")
    cols = [r[1] for r in cur.fetchall()]
    if 'purchase_by' not in cols:
        cur.execute('ALTER TABLE ShoppingList ADD COLUMN purchase_by DATE')
        conn.commit()
    conn.close()


# Run migrations at import time (avoid removed before_first_request in newer Flask)
ensure_migrations()


@app.route('/')
def index():
    conn = get_db_connection()
    ShoppingList = conn.execute('SELECT * FROM ShoppingList').fetchall()
    conn.close()
    return render_template('index.html', ShoppingList=ShoppingList)


@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        # CSRF check unless explicitly disabled (useful for tests)
        if not app.config.get('DISABLE_CSRF'):
            # support token in form, JSON body, or X-CSRF-Token header
            form_token = request.form.get('csrf_token') or (request.get_json(silent=True) or {}).get('csrf_token') or request.headers.get('X-CSRF-Token')
            if not form_token or form_token != session.get('csrf_token'):
                flash('Invalid CSRF token', 'error')
                return redirect(url_for('index'))
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        price_raw = request.form.get('price', '0').strip()
        purchase_by_raw = request.form.get('purchase_by')
        if not title or not content:
            flash('Title and description are required!', 'error')
        else:
            # Validate price
            try:
                price = float(price_raw)
            except Exception:
                flash('Price must be a number (e.g. 2.99)', 'error')
                return redirect(url_for('index'))

            # default purchase_by to 7 days from now if not provided
            import datetime
            if not purchase_by_raw:
                purchase_by_val = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
            else:
                purchase_by_val = purchase_by_raw

            conn = get_db_connection()
            cur = conn.execute(
                'INSERT INTO ShoppingList (title, content, price, created, purchase_by) VALUES (?, ?, ?, datetime("now"), ?)',
                (title, content, price, purchase_by_val)
            )
            conn.commit()
            item_id = cur.lastrowid
            # fetch inserted row to return when called via AJAX
            row = conn.execute('SELECT * FROM ShoppingList WHERE id = ?', (item_id,)).fetchone()
            conn.close()
            flash('Item added successfully!', 'success')
            # If request is AJAX/JSON return JSON
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                row_dict = dict(row)
                row_dict['purchase_by'] = row['purchase_by'] if 'purchase_by' in row.keys() else None
                # build server-side Amazon search URL (safe encoding)
                row_dict['amazon_url'] = 'https://www.amazon.com/s?k=' + quote_plus(f"{row['title']} {row['content']}")
                return jsonify(row_dict), 201
            return redirect(url_for('index'))

    # Form is now part of the main page (SPA modal). On GET redirect to index.
    return redirect(url_for('index'))


@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    # CSRF check (delete comes via POST or AJAX)
    if not app.config.get('DISABLE_CSRF'):
        token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token') or (request.get_json(silent=True) or {}).get('csrf_token')
        if not token or token != session.get('csrf_token'):
            flash('Invalid CSRF token', 'error')
            # if AJAX, return JSON error
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': 'Invalid CSRF token'}), 400
            return redirect(url_for('index'))

    conn = get_db_connection()
    conn.execute('DELETE FROM ShoppingList WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    flash('Item deleted successfully!', 'success')
    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'status': 'ok'})
    return redirect(url_for('index'))


@app.route('/api/items', methods=['GET'])
def api_items():
    # Server-side processing for DataTables
    # Params: draw, start, length, search[value], order[0][column], order[0][dir]
    params = request.args
    draw = int(params.get('draw', 1))
    start = int(params.get('start', 0))
    length = int(params.get('length', 25))
    search_value = params.get('search[value]', '')


    # columns mapping: 0=title,1=content,2=price,3=purchase_by,4=created
    order_col_index = int(params.get('order[0][column]', 0))
    order_dir = params.get('order[0][dir]', 'asc').lower()
    # allowlist for columns
    col_map = {0: 'title', 1: 'content', 2: 'price', 3: 'purchase_by', 4: 'created'}
    order_col = col_map.get(order_col_index, 'created')
    # sanitize direction
    if order_dir not in ('asc', 'desc'):
        order_dir = 'asc'

    conn = get_db_connection()
    # total records
    total = conn.execute('SELECT COUNT(*) FROM ShoppingList').fetchone()[0]

    # filtering
    if search_value:
        like = f"%{search_value}%"
        # If search_value looks like a number, also allow filtering by price equality
        try:
            num = float(search_value)
        except Exception:
            num = None

        if num is not None:
            filtered = conn.execute(
                'SELECT COUNT(*) FROM ShoppingList WHERE title LIKE ? OR content LIKE ? OR price = ?',
                (like, like, num)
            ).fetchone()[0]
            rows = conn.execute(
                f'SELECT * FROM ShoppingList WHERE (title LIKE ? OR content LIKE ? OR price = ?) ORDER BY {order_col} {order_dir} LIMIT ? OFFSET ?',
                (like, like, num, length, start)
            ).fetchall()
        else:
            filtered = conn.execute(
                'SELECT COUNT(*) FROM ShoppingList WHERE title LIKE ? OR content LIKE ?',
                (like, like)
            ).fetchone()[0]
            rows = conn.execute(
                f'SELECT * FROM ShoppingList WHERE title LIKE ? OR content LIKE ? ORDER BY {order_col} {order_dir} LIMIT ? OFFSET ?',
                (like, like, length, start)
            ).fetchall()
    else:
        filtered = total
        rows = conn.execute(
            f'SELECT * FROM ShoppingList ORDER BY {order_col} {order_dir} LIMIT ? OFFSET ?',
            (length, start)
        ).fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append({
            'id': r['id'],
            'title': r['title'],
            'content': r['content'],
            'price': r['price'],
            'created': r['created'],
            'purchase_by': r['purchase_by'],
            'amazon_url': 'https://www.amazon.com/s?k=' + quote_plus(f"{r['title']} {r['content']}")
        })

    return jsonify({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': filtered,
        'data': data
    })


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')  # Change port to 5000 and host to 
# app.py
