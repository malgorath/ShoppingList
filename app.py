import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash


def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn


app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/')
def index():
    conn = get_db_connection()
    ShoppingList = conn.execute('SELECT * FROM ShoppingList').fetchall()
    conn.close()
    return render_template('index.html', ShoppingList=ShoppingList)


@app.route('/add', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        if not title or not content:
            flash('Title and content are required!', 'error')
        else:
            conn = get_db_connection()
            conn.execute(
                'INSERT INTO ShoppingList (title, content, created) VALUES (?, ?, datetime("now"))',
                (title, content)
            )
            conn.commit()
            conn.close()
            flash('Item added successfully!', 'success')
            return redirect(url_for('index'))
    return render_template('add.html')


@app.route('/delete/<int:item_id>', methods=['POST'])
def delete_item(item_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM ShoppingList WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')  # Change port to 5000 and host to 
# app.py
