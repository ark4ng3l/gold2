class CustomerController:
    def __init__(self, db):
        """Initialize the customer controller with a database connection."""
        self.db = db

    def add_customer(self, first_name, last_name, phone):
        """Add a new customer."""
        if not first_name or not last_name:
            raise ValueError("نام و نام خانوادگی الزامی است")
        if phone and (not phone.isdigit() or len(phone) < 10):
            raise ValueError("شماره تماس باید حداقل 10 رقم و فقط شامل اعداد باشد")
        self.db.execute(
            "INSERT INTO customers (first_name, last_name, phone) VALUES (?, ?, ?)",
            (first_name, last_name, phone)
        )

    def update_customer(self, customer_id, first_name, last_name, phone):
        """Update an existing customer."""
        if not first_name or not last_name:
            raise ValueError("نام و نام خانوادگی الزامی است")
        if phone and (not phone.isdigit() or len(phone) < 10):
            raise ValueError("شماره تماس باید حداقل 10 رقم و فقط شامل اعداد باشد")
        self.db.execute(
            "UPDATE customers SET first_name = ?, last_name = ?, phone = ? WHERE id = ?",
            (first_name, last_name, phone, customer_id)
        )

    def delete_customer(self, customer_id):
        """Delete a customer."""
        self.db.execute("DELETE FROM customers WHERE id = ?", (customer_id,))

    def get_customers(self, search_query=None):
        """Get all customers with optional search."""
        query = "SELECT * FROM customers"
        params = ()
        if search_query:
            query += " WHERE first_name LIKE ? OR last_name LIKE ? OR phone LIKE ?"
            search_term = f"%{search_query}%"
            params = (search_term, search_term, search_term)
        query += " ORDER BY first_name, last_name"
        rows = self.db.fetchall(query, params)
        return [
            {
                'id': row[0],
                'first_name': row[1],
                'last_name': row[2],
                'phone': row[3]
            } for row in rows
        ]