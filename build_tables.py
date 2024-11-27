import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
connection = sqlite3.connect("instance/lab-project.db")
cursor = connection.cursor()


create_admin_table = """
CREATE TABLE IF NOT EXISTS Admin (
    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL
);
"""

create_customer_table = """
CREATE TABLE IF NOT EXISTS Customer (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    balance REAL NOT NULL DEFAULT 0,
    age INTEGER NOT NULL,
    address TEXT NOT NULL,
    gender TEXT NOT NULL,
    marital_status TEXT NOT NULL
);
"""

create_inventory_table = """
CREATE TABLE IF NOT EXISTS Inventory (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    price REAL NOT NULL,
    description TEXT NOT NULL,
    count INTEGER NOT NULL
);
"""

create_log_table = """
CREATE TABLE IF NOT EXISTS Log (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT NOT NULL UNIQUE,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

create_favorite_table = """
CREATE TABLE IF NOT EXISTS Favorite (
    favorite_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    inventory_id INTEGER NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(user_id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id)
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
    flag BOOLEAN,
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
    FOREIGN KEY (customer_id) REFERENCES customer(user_id)
);
"""

create_sale_table = """
CREATE TABLE IF NOT EXISTS Sale (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    inventory_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id),
    FOREIGN KEY (customer_id) REFERENCES customer(user_id)
);
"""

create_wishlist_table = """
CREATE TABLE IF NOT EXISTS Wishlist (
    wishlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    inventory_id INTEGER NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (inventory_id) REFERENCES inventory(inventory_id)
);
"""

# Execute SQL commands
cursor.execute(create_admin_table)
cursor.execute(create_customer_table)
cursor.execute(create_inventory_table)
cursor.execute(create_log_table)
cursor.execute(create_favorite_table)
cursor.execute(create_review_table)
cursor.execute(create_sale_table)
cursor.execute(create_wishlist_table)

# Commit changes and close the connection
connection.commit()
connection.close()

print("Tables created successfully.")
