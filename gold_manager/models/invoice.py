import datetime
from datetime import timedelta

class Invoice:
    def __init__(self, db):
        """Initialize the invoice model with a database connection."""
        self.db = db

    def add_invoice(self, customer_id, invoice_number, amount, interest, installment_type, start_date, num_installments, products):
        """Add a new invoice and its installments."""
        created_at = datetime.datetime.now().isoformat()
        self.db.execute(
            "INSERT INTO invoices (customer_id, invoice_number, amount, interest, installment_type, start_date, num_installments, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (customer_id, invoice_number, amount, interest, installment_type, start_date, num_installments, created_at)
        )
        invoice_id = self.db.fetchone("SELECT last_insert_rowid()")[0]

        # Add products
        for product in products:
            self.db.execute(
                "INSERT INTO products (invoice_id, name, description, price) VALUES (?, ?, ?, ?)",
                (invoice_id, product['name'], product['description'], product['price'])
            )

        # Calculate and add installments
        installment_amount = amount / num_installments
        interest_amount = (amount * (interest / 100)) / num_installments
        start_date = datetime.datetime.strptime(start_date, '%Y/%m/%d')
        for i in range(1, num_installments + 1):
            if installment_type == "روزانه":
                due_date = start_date + timedelta(days=i)
            elif installment_type == "هفتگی":
                due_date = start_date + timedelta(weeks=i)
            else:  # ماهانه
                due_date = start_date + timedelta(days=30 * i)
            self.db.execute(
                "INSERT INTO installments (invoice_id, installment_number, amount, interest_amount, due_date, paid) VALUES (?, ?, ?, ?, ?, ?)",
                (invoice_id, i, installment_amount, interest_amount, due_date.strftime('%Y/%m/%d'), 0)
            )

    def add_payment(self, invoice_id, amount, payment_date, admin_username, payment_type, source_card=None, destination_card=None, source_iban=None, destination_iban=None):
        """Add a payment for an invoice."""
        timestamp = datetime.datetime.now().isoformat()
        self.db.execute(
            "INSERT INTO payments (invoice_id, amount, date, timestamp, admin_username, payment_type, source_card, destination_card, source_iban, destination_iban) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (invoice_id, amount, payment_date, timestamp, admin_username, payment_type, source_card, destination_card, source_iban, destination_iban)
        )
        # Mark installment as paid
        installment = self.db.fetchone("SELECT id, amount, interest_amount FROM installments WHERE invoice_id = ? AND paid = 0 ORDER BY installment_number LIMIT 1", (invoice_id,))
        if installment:
            total_due = installment[1] + installment[2]  # amount + interest_amount
            if amount >= total_due:
                self.db.execute("UPDATE installments SET paid = 1 WHERE id = ?", (installment[0],))

    def get_due_installments(self, customer_id=None, days_ahead=5):
        """Get installments due within the next few days."""
        today = datetime.datetime.now()
        due_date_limit = (today + timedelta(days=days_ahead)).strftime('%Y/%m/%d')
        today = today.strftime('%Y/%m/%d')
        
        query = """
            SELECT i.id, i.invoice_id, i.installment_number, i.amount, i.interest_amount, i.due_date,
                   c.first_name || ' ' || c.last_name AS customer_name, inv.invoice_number
            FROM installments i
            JOIN invoices inv ON i.invoice_id = inv.id
            JOIN customers c ON inv.customer_id = c.id
            WHERE i.paid = 0 AND i.due_date BETWEEN ? AND ?
        """
        params = (today, due_date_limit)
        if customer_id:
            query += " AND inv.customer_id = ?"
            params += (customer_id,)
        
        rows = self.db.fetchall(query, params)
        return [
            {
                'installment_id': row[0],
                'invoice_id': row[1],
                'installment_number': row[2],
                'amount': row[3] + row[4],  # Include interest
                'due_date': row[5],
                'customer_name': row[6],
                'invoice_number': row[7]
            } for row in rows
        ]