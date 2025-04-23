import sqlite3
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect("gold_management.db")
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Users Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Customers Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Invoices Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                invoice_number TEXT NOT NULL,
                amount REAL NOT NULL,
                interest REAL DEFAULT 0,
                installment_type TEXT,
                start_date TEXT,
                num_installments INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers(id)
            )
        ''')

        # Installments Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS installments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                amount REAL NOT NULL,
                interest_amount REAL DEFAULT 0,
                due_date TEXT NOT NULL,
                paid INTEGER DEFAULT 0,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id)
            )
        ''')

        # Products Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id)
            )
        ''')

        # Payments Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER,
                amount REAL NOT NULL,
                payment_type TEXT NOT NULL,
                payment_details TEXT,
                payment_date TEXT DEFAULT CURRENT_TIMESTAMP,
                admin_id INTEGER,
                FOREIGN KEY (invoice_id) REFERENCES invoices(id),
                FOREIGN KEY (admin_id) REFERENCES users(id)
            )
        ''')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_customers_name ON customers(first_name, last_name)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(start_date)')
        self.conn.commit()

    def execute(self, query, params=()):
        try:
            with self.conn:  # تغییر این خط
                self.cursor.execute(query, params)
        except sqlite3.Error as e:
            raise Exception(f"Database error: {e}")

    def fetchone(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            raise Exception(f"Database error: {e}")

    def fetchall(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            raise Exception(f"Database error: {e}")

    def __del__(self):
        self.conn.close()