#!/usr/bin/env python3
"""
Simple seeding script to add grocery items to the project's SQLite database.
Run from project root (where database.db lives):

./scripts/seed_db.py

This will append 150 grocery items to the ShoppingList table.
"""
import sqlite3
import random
from datetime import datetime, timedelta

DB = 'database.db'
COUNT = 150
GROCERY_ITEMS = [
    'Milk', 'Bread', 'Eggs', 'Butter', 'Cheese', 'Yogurt', 'Chicken Breast', 'Ground Beef',
    'Pasta', 'Rice', 'Canned Tomatoes', 'Onions', 'Potatoes', 'Carrots', 'Apples', 'Bananas',
    'Oranges', 'Lettuce', 'Spinach', 'Cereal', 'Oats', 'Coffee', 'Tea', 'Sugar', 'Salt',
    'Pepper', 'Olive Oil', 'Vegetable Oil', 'Flour', 'Baking Powder', 'Yeast', 'Tomato Sauce',
    'Peanut Butter', 'Jam', 'Honey', 'Granola', 'Frozen Vegetables', 'Frozen Pizza', 'Ice Cream'
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

for i in range(COUNT):
    title = random.choice(GROCERY_ITEMS)
    # append index to make some variety
    title_full = f"{title} #{i+1}"
    content = f"Pack of {random.randint(1,5)} - {title.lower()}"
    price = round(random.uniform(0.99, 19.99), 2)
    # purchase_by random between today and 21 days
    pb = (datetime.utcnow() + timedelta(days=random.randint(0,21))).date().isoformat()
    cur.execute(
        "INSERT INTO ShoppingList (title, content, price, purchase_by) VALUES (?, ?, ?, ?)",
        (title_full, content, price, pb)
    )

conn.commit()
print(f"Inserted {COUNT} items into {DB}")
conn.close()
