import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()
# Define database file name
db_name = os.getenv("DB_NAME")

def create_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create table for customer complaints
    cursor.execute('''DROP TABLE IF EXISTS {}'''.format(os.getenv("COMPLAINT_TABLE")))
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS {} (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            product_name TEXT NOT NULL,
            complaint_details TEXT NOT NULL,
            complaint_date TEXT NOT NULL,
            status TEXT DEFAULT 'Open'
        )
    '''.format(os.getenv("COMPLAINT_TABLE")))
    
    # Commit changes and close the connection
    conn.commit()

    # Dummy complaints data
    dummy_complaints = [
        (1, "alice.johnson@example.com", "Anti-Aging Cream", "Caused skin irritation.", "2024-11-01", "Open"),
        (2, "bob.smith@example.com", "Sunscreen SPF 50", "Leaves a white residue.", "2024-11-02", "In Progress"),
        (3, "charlie.brown@example.com", "Moisturizing Lotion", "Bottle was half empty.", "2024-11-03", "Resolved"),
        (4, "daisy.parker@example.com", "Acne Treatment Gel", "No visible results after 3 weeks.", "2024-11-04", "Open"),
        (5, "evan.taylor@example.com", "Facial Cleanser", "Strong chemical smell.", "2024-11-05", "In Progress"),
        (6, "fiona.lewis@example.com", "Vitamin C Serum", "Caused redness and swelling.", "2024-11-06", "Resolved"),

    ]

    # Insert dummy data into the table
    cursor.executemany('''INSERT INTO {} (order_id, email, product_name, complaint_details, complaint_date, status) VALUES (?, ?, ?, ?, ?, ?)'''.format(os.getenv('COMPLAINT_TABLE')),
                       dummy_complaints)

    conn.commit()
    conn.close()
    print(f"Database '{db_name}' and table 'customer_complaints' created successfully.")


create_database()
