import sqlite3
from datetime import datetime

# Database connection
conn = sqlite3.connect('skincare_orders.db')
cursor = conn.cursor()

# Create the orders table
cursor.execute('''
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_email TEXT NOT NULL,
    order_date TEXT NOT NULL,
    order_amount REAL NOT NULL,
    item_quantity INTEGER NOT NULL
)
''')

# Insert dummy data
dummy_orders = [
    ("alice@example.com", datetime(2024, 11, 20).strftime('%Y-%m-%d'), 50.25, 2),
    ("bob@example.com", datetime(2024, 11, 21).strftime('%Y-%m-%d'), 75.00, 3),
    ("charlie@example.com", datetime(2024, 11, 22).strftime('%Y-%m-%d'), 20.99, 1),
    ("diana@example.com", datetime(2024, 11, 23).strftime('%Y-%m-%d'), 100.50, 4),
    ("eve@example.com", datetime(2024, 11, 19).strftime('%Y-%m-%d'), 35.75, 2),
    ("frank@example.com", datetime(2024, 11, 18).strftime('%Y-%m-%d'), 60.00, 3),
    ("grace@example.com", datetime(2024, 11, 17).strftime('%Y-%m-%d'), 45.99, 2),
    ("hank@example.com", datetime(2024, 11, 16).strftime('%Y-%m-%d'), 90.25, 5),
    ("ivy@example.com", datetime(2024, 11, 15).strftime('%Y-%m-%d'), 120.00, 6),
    ("jack@example.com", datetime(2024, 11, 14).strftime('%Y-%m-%d'), 80.50, 4)
]

cursor.executemany('''
INSERT INTO orders (customer_email, order_date, order_amount, item_quantity)
VALUES (?, ?, ?, ?)
''', dummy_orders)

# Commit and close
conn.commit()
conn.close()

print("Database and table created successfully, and dummy data inserted.")
