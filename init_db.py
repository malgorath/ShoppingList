import sqlite3

connection = sqlite3.connect('database.db')

with open('./schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

cur.execute("INSERT INTO ShoppingList (title, content) VALUES (?, ?)",
            ('Gatorade', 'zero orange')
            )

cur.execute("INSERT INTO ShoppingList (title, content) VALUES (?, ?)",
            ('Gatorade', 'zero grape')
            )

connection.commit()
connection.close()
