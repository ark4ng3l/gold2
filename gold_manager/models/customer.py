from utils.database import Database
import datetime

class Customer:
    def __init__(self, db: Database):
        self.db = db

    def add_customer(self, first_name, last_name, phone):
        created_at = datetime.datetime.now().isoformat()
        self.db.execute(
            "INSERT INTO customers (first_name, last_name, phone, created_at) VALUES (?, ?, ?, ?)",
            (first_name, last_name, phone, created_at)
        )
        return self.db.cursor.lastrowid

    def get_customers(self):
        return self.db.fetchall("SELECT * FROM customers")

    def update_customer(self, customer_id, first_name, last_name, phone):
        self.db.execute(
            "UPDATE customers SET first_name = ?, last_name = ?, phone = ? WHERE id = ?",
            (first_name, last_name, phone, customer_id)
        )

    def delete_customer(self, customer_id):
        self.db.execute("DELETE FROM customers WHERE id = ?", (customer_id,))