# ShoppingList

A tiny, single-file Flask + SQLite demo app for maintaining a shopping list. The app uses server-side DataTables for listing items, a SPA modal for adding items, and supports a light/dark theme with deliberate light table rows for readability.

This README documents how to set up, run, and develop the project, plus a short changelog describing the recent UI and data model changes.

## Features

- Flask 3.x application using SQLite (single-file `database.db`).
- Server-side DataTables integration (AJAX) for scalable table rendering.
- SPA-style Add Item modal (no page reload) with fields: Title, Description, Price, Purchase By (date).
- Theme support: dark and light themes. Inputs remain white with black text to ensure high-contrast editing. Labels use the theme's muted color for readability.
- Table cells are forced to light backgrounds (white) even in dark mode to ensure legibility and a consistent look.
- Fixed top menubar with drop shadow; content floats 20px below to expose the shadow.
- Database migration to add `purchase_by` column; newly-seeded items include it.
- A `scripts/seed_db.py` script to append 150 grocery items for demo/testing.

## Files of note

- `app.py` - main Flask application and API endpoints.
- `schema.sql` - SQL schema. The `ShoppingList` table includes `purchase_by DATE`.
- `init_db.py` - initial DB bootstrap helper (if present).
- `database.db` - the SQLite database (created at runtime).
- `templates/` - Jinja2 templates (`base.html`, `index.html`, `add.html` if present).
- `static/css/style.css` - main stylesheet. Contains malgorath_suite-inspired theme rules and several overrides:
	- Inputs (`.form-control`, `.themed-input`) are forced to white with black text.
	- Table cells and headers are forced to white background + black text (to keep table readable in dark theme).
	- Labels use `var(--muted)` color (so they read lighter in dark mode).
	- Navbar is fixed to the top with a drop shadow; `.app-card` is positioned 20px below the header to reveal the shadow.
	- Modal (`.modal-content`) uses `var(--panel)` and `var(--fg)` so the modal follows theme panels while inputs remain high-contrast.
- `scripts/seed_db.py` - new script that inserts 150 grocery items into `database.db` (appends by default).

## Setup

1. Create and activate a virtualenv (the project contains a `venv/` in workspace used during development).

	 python -m venv venv
	 source venv/bin/activate

2. Install dependencies:

	 pip install -r requirements.txt

3. Initialize the database (optional - if you want a fresh DB):

	 python init_db.py

4. Seed demo data (this app appends items to your DB):

	 python scripts/seed_db.py

5. Run the Flask app (development server):

	 python app.py

The app will run at http://127.0.0.1:5000 by default.

## Development notes

- Theme details:
	- CSS variables are defined in `:root` and `.theme-dark` for colors such as `--panel`, `--muted`, and `--fg`.
	- Because table rows are critical to readability, `.table tbody td` and `.table thead th` are forced to a white background with black text (via `!important` selectors). If you later change column order, update the nth-child selectors used for alignment.

- Modal behavior:
	- Modals are centered using Bootstrap's `modal-dialog-centered` and additionally have a small `padding-top` fallback for narrow screens so the modals are visible below the fixed header.
	- The modal panel background uses `var(--panel)` (dark in dark theme), while inputs remain white for editing contrast.

- Seed script:
	- `scripts/seed_db.py` appends 150 rows. It intentionally appends so you can run it repeatedly for load testing; if you'd like it to recreate the DB, edit the script to remove the file or run `init_db.py` first.

## Database

Table `ShoppingList` columns:

- id INTEGER PRIMARY KEY AUTOINCREMENT
- created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
- title TEXT
- content TEXT
- price REAL
- purchase_by DATE

Two helpful SQL commands for inspection:

SELECT COUNT(*) FROM ShoppingList;
SELECT * FROM ShoppingList ORDER BY id DESC LIMIT 10;

## UI behavior and accessibility

- Title and Description columns are left-aligned; Price, Purchase By, Date Added, and Actions are centered for visual consistency.
- Inputs are white with black text for high contrast in both themes; labels use the muted color for less visual weight.
- The table remains light in both themes to prioritize readability.

## Scripts

- `scripts/seed_db.py` - run to add 150 grocery records. The script uses random prices and purchase_by dates 0-21 days from today.

## Testing & verification

- Start the dev server and use the API endpoint to inspect rows:

	curl 'http://127.0.0.1:5000/api/items?start=0&length=5'

- Use the web UI to confirm:
	- Modal centers properly on open.
	- Modal background changes when you toggle theme.
	- Table rows are white with black text in dark mode.

## Changelog (recent notable changes)

- Added `purchase_by` column to `ShoppingList` and updated templates to include the date field in the Add Item modal and DataTable.
- Reworked theme behavior so inputs remain white with dark text and labels are muted.
- Fixed JS loading order issues and ensured jQuery/DataTables load before app script.
- Introduced `scripts/seed_db.py` to quickly populate many demo rows (150 items).
- Made menu bar fixed with shadow and positioned `.app-card` 20px below for visual depth.

## Next steps / recommendations

- Consider adding a richer datepicker (flatpickr) to `purchase_by` for better UX.
- Replace nth-child alignment CSS with explicit column classes for maintainability.
- Add tests for the API endpoints (pytest) and CI linting for styles.

---
Updated: September 22, 2025

## Getting started

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Initialize the database (creates `database.db` with sample rows):

```bash
python init_db.py
```

3. Run the app:

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Configuration

- `FLASK_SECRET_KEY`: optional environment variable to set the Flask secret key.
- `DATABASE_PATH`: optional path to the sqlite database file (defaults to `database.db`).

## Testing

Install pytest and run tests:

```bash
pip install pytest
pytest -q
```
