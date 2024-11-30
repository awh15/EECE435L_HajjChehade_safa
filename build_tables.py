import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
connection = sqlite3.connect("instance/lab-project.db")
cursor = connection.cursor()


create_favorite_table = """
CREATE TABLE IF NOT EXISTS Favorite (
    favorite_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    inventory_id INTEGER NOT NULL
);
"""

create_review_table = """
CREATE TABLE IF NOT EXISTS Review (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    rating INTEGER NOT NULL,
    comment TEXT,
    flag BOOLEAN
);
"""

create_sale_table = """
CREATE TABLE IF NOT EXISTS Sale (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL
);
"""

create_wishlist_table = """
CREATE TABLE IF NOT EXISTS Wishlist (
    wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    inventory_id INTEGER NOT NULL
);
"""

# Execute SQL commands
cursor.execute(create_favorite_table)
cursor.execute(create_review_table)
cursor.execute(create_sale_table)
cursor.execute(create_wishlist_table)

# Commit changes and close the connection
connection.commit()
connection.close()

print("Tables created successfully.")
