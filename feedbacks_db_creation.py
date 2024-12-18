import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

# Database name
DB_NAME = os.getenv("DB_NAME")

# Function to connect to the database
def get_connection():
    return sqlite3.connect(DB_NAME)

# Function to create the feedbacks table
def create_table():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS {} (
            order_id TEXT,
            feedback_summary TEXT,
            sentiment TEXT
        )
    """.format(os.getenv("FEEDBACK_TABLE")))
    connection.commit()
    connection.close()
    print("Table 'feedbacks' created successfully.")

# Function to add a new feedback entry
def add_feedback(order_id, feedback_summary, sentiment):
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO {} (order_id, feedback_summary, sentiment)
            VALUES (?, ?, ?)
        """/format(os.getenv("FEEDBACK_TABLE")), (order_id, feedback_summary, sentiment))
        connection.commit()
        print(f"Feedback added for order ID {order_id}.")
    except sqlite3.IntegrityError:
        print(f"Error: Feedback for order ID {order_id} already exists.")
    finally:
        connection.close()

# Function to fetch records by order_id
def fetch_feedback_by_order_id(order_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM {} WHERE order_id = ?
    """.format(os.getenv("FEEDBACK_TABLE")), (order_id,))
    record = cursor.fetchone()
    connection.close()
    if record:
        print("Feedback Found:")
        print(f"Order ID: {record[0]}, Feedback Summary: {record[1]}, Sentiment: {record[2]}")
        return record
    else:
        print(f"No feedback found for order ID {order_id}.")
        return None

# Main execution
if __name__ == "__main__":
    # Create the table
    create_table()
    
    # Example: Adding a new feedback
    add_feedback("2", "Product arrived in great condition, very satisfied.", "Positive")
    
    # Example: Fetching feedback by order ID
    fetch_feedback_by_order_id("2")
    
