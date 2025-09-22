DROP TABLE IF EXISTS ShoppingList;

CREATE TABLE ShoppingList (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    price REAL NOT NULL DEFAULT 0.0,
    purchase_by DATE
);

-- Indexes to improve search performance
CREATE INDEX IF NOT EXISTS idx_shoppinglist_title ON ShoppingList(title);
CREATE INDEX IF NOT EXISTS idx_shoppinglist_content ON ShoppingList(content);
    
