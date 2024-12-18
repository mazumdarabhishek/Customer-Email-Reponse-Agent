import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
from pydantic_classes import AgentState


def get_connection():
    return sqlite3.connect(database= os.getenv("DB_NAME"))

def fetch_one_as_dict(res, cursor):
    """
    Converts cursor.fetchone() result into a dictionary.
    """
    row = res.fetchone()
    if row is None:
        return None
    # Extract column names from cursor.description
    column_names = [desc[0] for desc in cursor.description]
    # Return a dictionary mapping column names to values
    return dict(zip(column_names, row))




class DatabaseManager:

    @staticmethod
    def fetch_order(order_id: str):
        conn = get_connection()
        cursor = conn.cursor()
        # print(order_id)
        # print(cursor.execute(f"SELECT * FROM orders WHERE order_id={order_id}").fetchall())
        res = cursor.execute(f"""SELECT * FROM {os.getenv("ORDER_TABLE")} WHERE order_id={order_id}""")
        record = fetch_one_as_dict(res, cursor)
        conn.close()

        return record


    @staticmethod
    def insert_feedback(state: AgentState):
        conn = get_connection()
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO {} (order_id, feedback_summary, sentiment)
                VALUES (?, ?, ?)
            """.format(os.getenv("FEEDBACK_TABLE")), (state.order_id, state.input_email, state.sentiment))
            conn.commit()
            print(f"Feedback added for order ID {state.order_id}.")

        except sqlite3.IntegrityError:
            print(f"Feedback for order ID {state.order_id} already exists.")
        finally:
            conn.close()


    @staticmethod
    def fetch_complaint(order_id):

        conn= get_connection()
        cursor= conn.cursor()

        res = cursor.execute("""
        SELECT * FROM {} WHERE order_id = ? and status = 'Open'
        """.format(os.getenv("COMPLAINT_TABLE")), str(order_id))
        record = fetch_one_as_dict(res, cursor)
        conn.close()
        return record

    @staticmethod
    def insert_complaint(state :AgentState):
        conn= get_connection()
        cursor= conn.cursor()

        cursor.execute("""INSERT INTO {} (order_id, email, product_name, complaint_details, complaint_date)
                VALUES (?, ?, ?, ?, ?)""".format(os.getenv("COMPLAINT_TABLE")),
                       (state.order_id, state.customer_email, state.product_name, state.complaint_summary,
                       datetime(2024, 11, 20).strftime('%Y-%m-%d')))

        complaint_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return complaint_id