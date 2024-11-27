import sqlite3

# Define database file name
db_name = "skincare_complaints.db"

def create_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create table for customer complaints
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customer_complaints (
            complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            email TEXT NOT NULL,
            product_name TEXT NOT NULL,
            complaint_details TEXT NOT NULL,
            complaint_date TEXT NOT NULL,
            status TEXT DEFAULT 'Open'
        )
    ''')
    
    # Commit changes and close the connection
    conn.commit()

    # Dummy complaints data
    dummy_complaints = [
        ("Alice Johnson", "alice.johnson@example.com", "Anti-Aging Cream", "Caused skin irritation.", "2024-11-01", "Open"),
        ("Bob Smith", "bob.smith@example.com", "Sunscreen SPF 50", "Leaves a white residue.", "2024-11-02", "In Progress"),
        ("Charlie Brown", "charlie.brown@example.com", "Moisturizing Lotion", "Bottle was half empty.", "2024-11-03", "Resolved"),
        ("Daisy Parker", "daisy.parker@example.com", "Acne Treatment Gel", "No visible results after 3 weeks.", "2024-11-04", "Open"),
        ("Evan Taylor", "evan.taylor@example.com", "Facial Cleanser", "Strong chemical smell.", "2024-11-05", "In Progress"),
        ("Fiona Lewis", "fiona.lewis@example.com", "Vitamin C Serum", "Caused redness and swelling.", "2024-11-06", "Resolved"),
        ("George Martin", "george.martin@example.com", "Night Repair Cream", "Too greasy for my skin.", "2024-11-07", "Open"),
        ("Hannah Davis", "hannah.davis@example.com", "Eye Cream", "No improvement in dark circles.", "2024-11-08", "In Progress"),
        ("Ian Wright", "ian.wright@example.com", "Exfoliating Scrub", "Scrub particles are too harsh.", "2024-11-09", "Resolved"),
        ("Jane Doe", "jane.doe@example.com", "Hydrating Toner", "Product leaked during shipping.", "2024-11-10", "Open")
    ]

    # Insert dummy data into the table
    cursor.executemany('''
        INSERT INTO customer_complaints (customer_name, email, product_name, complaint_details, complaint_date, status)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', dummy_complaints)

    conn.commit()
    conn.close()
    print(f"Database '{db_name}' and table 'customer_complaints' created successfully.")




