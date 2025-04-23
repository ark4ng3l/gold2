from models.invoice import Invoice

class PaymentController:
    def __init__(self, db):
        """Initialize the payment controller with a database connection."""
        self.db = db
        self.invoice_model = Invoice(db)

    def add_invoice(self, customer_id, invoice_number, amount, interest, installment_type, start_date, num_installments, products):
        """Add a new invoice."""
        return self.invoice_model.add_invoice(customer_id, invoice_number, amount, interest, installment_type, start_date, num_installments, products)

    def add_payment(self, invoice_id, amount, payment_date, admin_username, payment_type, source_card=None, destination_card=None, source_iban=None, destination_iban=None):
        """Add a payment for an invoice."""
        return self.invoice_model.add_payment(invoice_id, amount, payment_date, admin_username, payment_type, source_card, destination_card, source_iban, destination_iban)

    def get_due_installments(self, customer_id=None, days_ahead=5):
        """Get due installments."""
        return self.invoice_model.get_due_installments(customer_id, days_ahead)

    def get_payment_history(self, invoice_id=None):
        """Get payment history for an invoice or all invoices."""
        query = """
            SELECT p.id, p.invoice_id, p.amount, p.date, p.admin_username, p.payment_type,
                   c.first_name || ' ' || c.last_name AS customer_name, inv.invoice_number
            FROM payments p
            JOIN invoices inv ON p.invoice_id = inv.id
            JOIN customers c ON inv.customer_id = c.id
        """
        params = ()
        if invoice_id:
            query += " WHERE p.invoice_id = ?"
            params = (invoice_id,)
        query += " ORDER BY p.timestamp DESC"
        rows = self.db.fetchall(query, params)
        return [
            {
                'payment_id': row[0],
                'invoice_id': row[1],
                'amount': row[2],
                'date': row[3],
                'admin_username': row[4],
                'payment_type': row[5],
                'customer_name': row[6],
                'invoice_number': row[7]
            } for row in rows
        ]