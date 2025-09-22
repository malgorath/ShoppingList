import sqlite3

connection = sqlite3.connect('database.db')

with open('./schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

import datetime

def days_from_now(days=7):
    return (datetime.date.today() + datetime.timedelta(days=days)).isoformat()

cur.execute("INSERT INTO ShoppingList (title, content, price, purchase_by) VALUES (?, ?, ?, ?)",
            ('Gatorade', 'zero orange', 2.49, days_from_now())
            )

cur.execute("INSERT INTO ShoppingList (title, content, price, purchase_by) VALUES (?, ?, ?, ?)",
            ('Gatorade', 'zero grape', 2.49, days_from_now())
            )

connection.commit()
connection.close()
