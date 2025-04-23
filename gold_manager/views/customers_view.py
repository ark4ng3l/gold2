import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta
from config import LANG, CURRENT_LANG, THEME
from .payments_view import PaymentView

class CustomersView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=THEME['background'])
        self.controller = controller
        self.selected_customer_id = None
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color=THEME['background'])
        header.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text=LANG[CURRENT_LANG]['customers'],
            font=THEME['font_bold'],
            text_color=THEME['text_light']
        ).grid(row=0, column=0, padx=10, sticky="w" if CURRENT_LANG == "en" else "e")

        ctk.CTkButton(
            header,
            text="+" + (" افزودن مشتری" if CURRENT_LANG == 'fa' else " Add Customer"),
            command=self.add_customer_popup,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10
        ).grid(row=0, column=1, padx=10, sticky="e" if CURRENT_LANG == "en" else "w")

        # Main Content
        self.content_frame = ctk.CTkFrame(self, fg_color=THEME['background'])
        self.content_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content_frame.grid_columnconfigure((0, 1), weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Customers List
        self.customers_list_frame = ctk.CTkFrame(self.content_frame, fg_color=THEME['card_background'], corner_radius=15)
        self.customers_list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.customers_list_frame.grid_columnconfigure(0, weight=1)
        self.customers_list_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            self.customers_list_frame,
            text=LANG[CURRENT_LANG]['customers'],
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w" if CURRENT_LANG == "en" else "e")

        self.customers_scroll = ctk.CTkScrollableFrame(self.customers_list_frame, fg_color=THEME['card_background'])
        self.customers_scroll.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.load_customers()

        # Customer Profile
        self.profile_frame = ctk.CTkFrame(self.content_frame, fg_color=THEME['card_background'], corner_radius=15)
        self.profile_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.profile_frame.grid_columnconfigure(0, weight=1)
        self.profile_frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            self.profile_frame,
            text=LANG[CURRENT_LANG]['profile'],
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).pack(pady=10)

        self.profile_info = ctk.CTkFrame(self.profile_frame, fg_color=THEME['card_background'])
        self.profile_info.pack(fill="x", padx=20, pady=10)

        self.stats_frame = ctk.CTkFrame(self.profile_frame, fg_color=THEME['card_background'])
        self.stats_frame.pack(fill="x", padx=20, pady=10)

        self.installments_frame = ctk.CTkFrame(self.profile_frame, fg_color=THEME['card_background'])
        self.installments_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def load_customers(self, page=1):
        page_size = 20
        offset = (page - 1) * page_size
    
        customers = self.controller.db.fetchall(
        "SELECT id, first_name, last_name FROM customers LIMIT ? OFFSET ?",
        (page_size, offset)
    )
        for widget in self.customers_scroll.winfo_children():
            widget.destroy()

        customers = self.controller.db.fetchall("SELECT id, first_name, last_name FROM customers")
        for customer in customers:
            customer_id, first_name, last_name = customer
            customer_button = ctk.CTkButton(
                self.customers_scroll,
                text=f"{first_name} {last_name}",
                command=lambda cid=customer_id: self.show_customer_profile(cid),
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                fg_color=THEME['button_fg'],
                hover_color=THEME['button_hover'],
                corner_radius=10,
                height=40
            )
            customer_button.pack(fill="x", padx=10, pady=5)

    def show_customer_profile(self, customer_id):
        self.selected_customer_id = customer_id
        for widget in self.profile_info.winfo_children():
            widget.destroy()
        for widget in self.stats_frame.winfo_children():
            widget.destroy()
        for widget in self.installments_frame.winfo_children():
            widget.destroy()

        # Customer Info
        customer = self.controller.db.fetchone(
            "SELECT first_name, last_name, phone FROM customers WHERE id = ?",
            (customer_id,)
        )
        first_name, last_name, phone = customer

        ctk.CTkLabel(
            self.profile_info,
            text=f"{LANG[CURRENT_LANG]['name']}: {first_name}",
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            text_color=THEME['text_dark']
        ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=5)

        ctk.CTkLabel(
            self.profile_info,
            text=f"{LANG[CURRENT_LANG]['family_name']}: {last_name}",
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            text_color=THEME['text_dark']
        ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=5)

        ctk.CTkLabel(
            self.profile_info,
            text=f"{LANG[CURRENT_LANG]['phone']}: {phone or '-'}",
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            text_color=THEME['text_dark']
        ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=5)

        # Products Purchased
        products_label = ctk.CTkLabel(
            self.profile_info,
            text=LANG[CURRENT_LANG]['products'],
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        )
        products_label.pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=5)

        invoices = self.controller.db.fetchall(
            "SELECT id, invoice_number FROM invoices WHERE customer_id = ?",
            (customer_id,)
        )
        for invoice in invoices:
            invoice_id, invoice_number = invoice
            products = self.controller.db.fetchall(
                "SELECT name, price FROM products WHERE invoice_id = ?",
                (invoice_id,)
            )
            for product in products:
                name, price = product
                ctk.CTkLabel(
                    self.profile_info,
                    text=f"{name} - {price:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'} ({LANG[CURRENT_LANG]['invoice_number']}: {invoice_number})",
                    font=THEME['font_small'],
                    text_color=THEME['text_dark']
                ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=20, pady=2)

        # Statistics
        total_debt = self.controller.db.fetchone(
            "SELECT SUM(amount + interest_amount) FROM installments WHERE invoice_id IN (SELECT id FROM invoices WHERE customer_id = ?) AND paid = 0",
            (customer_id,)
        )[0] or 0
        total_paid = self.controller.db.fetchone(
            "SELECT SUM(amount) FROM payments WHERE invoice_id IN (SELECT id FROM invoices WHERE customer_id = ?)",
            (customer_id,)
        )[0] or 0
        remaining_balance = total_debt
        paid_installments = self.controller.db.fetchone(
            "SELECT COUNT(*) FROM installments WHERE invoice_id IN (SELECT id FROM invoices WHERE customer_id = ?) AND paid = 1",
            (customer_id,)
        )[0]
        unpaid_installments = self.controller.db.fetchone(
            "SELECT COUNT(*) FROM installments WHERE invoice_id IN (SELECT id FROM invoices WHERE customer_id = ?) AND paid = 0",
            (customer_id,)
        )[0]

        self.stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(
            self.stats_frame,
            text=f"{LANG[CURRENT_LANG]['total_debt']}: {total_debt:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(
            self.stats_frame,
            text=f"{LANG[CURRENT_LANG]['total_paid_amount']}: {total_paid:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkLabel(
            self.stats_frame,
            text=f"{LANG[CURRENT_LANG]['remaining_balance']}: {remaining_balance:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).grid(row=0, column=2, padx=5, pady=5)

        ctk.CTkLabel(
            self.stats_frame,
            text=f"{LANG[CURRENT_LANG]['paid_installments']}: {paid_installments}",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).grid(row=1, column=0, padx=5, pady=5)
        ctk.CTkLabel(
            self.stats_frame,
            text=f"{LANG[CURRENT_LANG]['unpaid_installments']}: {unpaid_installments}",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).grid(row=1, column=1, padx=5, pady=5)

        # Installments
        installments_header = ctk.CTkFrame(self.installments_frame, fg_color=THEME['card_background'])
        installments_header.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(
            installments_header,
            text=LANG[CURRENT_LANG]['installments'],
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).pack(side="left" if CURRENT_LANG == "en" else "right", padx=10)

        ctk.CTkButton(
            installments_header,
            text=LANG[CURRENT_LANG]['create_installments'],
            command=self.create_installments_popup,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10,
            height=30
        ).pack(side="right" if CURRENT_LANG == "en" else "left", padx=10)

        installments_scroll = ctk.CTkScrollableFrame(self.installments_frame, fg_color=THEME['card_background'])
        installments_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        installments = self.controller.db.fetchall(
            """
            SELECT i.id, i.amount, i.interest_amount, i.due_date, i.paid, i.paid_at, inv.invoice_number
            FROM installments i
            JOIN invoices inv ON i.invoice_id = inv.id
            WHERE inv.customer_id = ?
            """,
            (customer_id,)
        )
        for installment in installments:
            inst_id, amount, interest_amount, due_date, paid, paid_at, invoice_number = installment
            inst_frame = ctk.CTkFrame(installments_scroll, fg_color="#E0E0E0", corner_radius=10)
            inst_frame.pack(fill="x", padx=5, pady=5)
            inst_frame.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                inst_frame,
                text=f"{LANG[CURRENT_LANG]['invoice_number']}: {invoice_number}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).grid(row=0, column=0, padx=10, pady=2, sticky="w" if CURRENT_LANG == "en" else "e")

            ctk.CTkLabel(
                inst_frame,
                text=f"{amount + interest_amount:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).grid(row=0, column=1, padx=10, pady=2)

            ctk.CTkLabel(
                inst_frame,
                text=f"{LANG[CURRENT_LANG]['due_date']}: {due_date}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).grid(row=1, column=0, padx=10, pady=2, sticky="w" if CURRENT_LANG == "en" else "e")

            if paid:
                ctk.CTkLabel(
                    inst_frame,
                    text=f"{LANG[CURRENT_LANG]['paid']} ({paid_at})",
                    font=THEME['font_small'],
                    text_color="green"
                ).grid(row=1, column=1, padx=10, pady=2)
            else:
                ctk.CTkButton(
                    inst_frame,
                    text=LANG[CURRENT_LANG]['pay'],
                    command=lambda iid=inst_id, inv_id=inst_frame.winfo_parent(): self.open_payment(iid, inv_id, amount, interest_amount),
                    font=THEME['font_small'],
                    fg_color=THEME['button_fg'],
                    hover_color=THEME['button_hover'],
                    corner_radius=10,
                    width=100
                ).grid(row=1, column=1, padx=10, pady=2)

    def open_payment(self, installment_id, invoice_id, amount, interest_amount):
        PaymentView(
            self,
            self.controller,
            self.selected_customer_id,
            invoice_id,
            installment_id,
            amount,
            interest_amount,
            self.show_customer_profile(self.selected_customer_id)
        )

    def add_customer_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("افزودن مشتری" if CURRENT_LANG == 'fa' else "Add Customer")
        popup.geometry("400x400")
        popup.configure(fg_color=THEME['background'])

        popup.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            popup,
            text="افزودن مشتری جدید" if CURRENT_LANG == 'fa' else "Add New Customer",
            font=THEME['font_bold'],
            text_color=THEME['text_light']
        ).pack(pady=20)

        first_name_entry = ctk.CTkEntry(
            popup,
            placeholder_text="نام" if CURRENT_LANG == 'fa' else "First Name",
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en']
        )
        first_name_entry.pack(pady=10)

        last_name_entry = ctk.CTkEntry(
            popup,
            placeholder_text="نام خانوادگی" if CURRENT_LANG == 'fa' else "Last Name",
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en']
        )
        last_name_entry.pack(pady=10)

        phone_entry = ctk.CTkEntry(
            popup,
            placeholder_text="شماره تماس" if CURRENT_LANG == 'fa' else "Phone Number",
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en']
        )
        phone_entry.pack(pady=10)

        def save_customer(self):
            first_name = first_name_entry.get().strip()
            last_name = last_name_entry.get().strip()
            phone = phone_entry.get().strip()

            if phone and (not phone.isdigit() or len(phone) != 11):
                messagebox.showerror(
                    "خطا" if CURRENT_LANG == 'fa' else "Error",
                    "شماره تماس باید 11 رقمی و عددی باشد" if CURRENT_LANG == 'fa' else "Phone must be 11 digits"
                )
                return

            try:
                self.controller.db.execute(
                    "INSERT INTO customers (first_name, last_name, phone) VALUES (?, ?, ?)",
                    (first_name, last_name, phone)
                )
                self.load_customers()
                popup.destroy()
            except Exception as e:
                messagebox.showerror(
                    "خطا" if CURRENT_LANG == 'fa' else "Error",
                    f"خطا در افزودن مشتری: {e}" if CURRENT_LANG == 'fa' else f"Error adding customer: {e}"
                )

        ctk.CTkButton(
            popup,
            text="ذخیره" if CURRENT_LANG == 'fa' else "Save",
            command=save_customer,
            font=THEME['font_bold'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10
        ).pack(pady=20)

    def create_installments_popup(self):
        if not self.selected_customer_id:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "لطفاً یک مشتری انتخاب کنید" if CURRENT_LANG == 'fa' else "Please select a customer"
            )
            return

        popup = ctk.CTkToplevel(self)
        popup.title(LANG[CURRENT_LANG]['create_installments'])
        popup.geometry("500x600")
        popup.configure(fg_color=THEME['background'])

        popup.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            popup,
            text=LANG[CURRENT_LANG]['create_installments'],
            font=THEME['font_bold'],
            text_color=THEME['text_light']
        ).pack(pady=20)

        # Invoice Number
        invoice_number_entry = ctk.CTkEntry(
            popup,
            placeholder_text=LANG[CURRENT_LANG]['invoice_number'],
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en']
        )
        invoice_number_entry.pack(pady=10)

        # Amount
        amount_entry = ctk.CTkEntry(
            popup,
            placeholder_text=LANG[CURRENT_LANG]['amount_per_installment'],
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en']
        )
        amount_entry.pack(pady=10)

        # Start Date
        start_date_entry = ctk.CTkEntry(
            popup,
            placeholder_text=LANG[CURRENT_LANG]['start_date'] + " (YYYY-MM-DD)",
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en']
        )
        start_date_entry.pack(pady=10)

        # Installment Type
        installment_type = ctk.CTkOptionMenu(
            popup,
            values=[
                LANG[CURRENT_LANG]['monthly'],
                LANG[CURRENT_LANG]['weekly']
            ],
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            fg_color=THEME['button_fg'],
            button_color=THEME['button_fg'],
            button_hover_color=THEME['button_hover']
        )
        installment_type.pack(pady=10)

        # Number of Installments
        num_installments_entry = ctk.CTkEntry(
            popup,
            placeholder_text=LANG[CURRENT_LANG]['num_installments'],
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en']
        )
        num_installments_entry.pack(pady=10)

        # Interest Rate
        interest_rate_entry = ctk.CTkEntry(
            popup,
            placeholder_text=LANG[CURRENT_LANG]['interest_rate'],
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en']
        )
        interest_rate_entry.pack(pady=10)

        def create_installments():
            invoice_number = invoice_number_entry.get().strip()
            try:
                amount = float(amount_entry.get().strip())
                num_installments = int(num_installments_entry.get().strip())
                interest_rate = float(interest_rate_entry.get().strip())
                start_date = start_date_entry.get().strip()
                type_ = installment_type.get()
            except ValueError:
                messagebox.showerror(
                    "خطا" if CURRENT_LANG == 'fa' else "Error",
                    "لطفاً مقادیر معتبر وارد کنید" if CURRENT_LANG == 'fa' else "Please enter valid values"
                )
                return

            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror(
                    "خطا" if CURRENT_LANG == 'fa' else "Error",
                    "فرمت تاریخ اشتباه است (YYYY-MM-DD)" if CURRENT_LANG == 'fa' else "Invalid date format (YYYY-MM-DD)"
                )
                return

            # Insert Invoice
            self.controller.db.execute(
                "INSERT INTO invoices (customer_id, invoice_number, amount, interest, installment_type, start_date, num_installments) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.selected_customer_id, invoice_number, amount * num_installments, interest_rate, type_, start_date, num_installments)
            )
            invoice_id = self.controller.db.fetchone("SELECT last_insert_rowid()")[0]

            # Calculate Installments
            if type_ == LANG[CURRENT_LANG]['monthly']:
                interest_per_installment = (interest_rate / 100) * amount
                for i in range(num_installments):
                    due_date = (start + timedelta(days=30 * (i + 1))).strftime("%Y-%m-%d")
                    self.controller.db.execute(
                        "INSERT INTO installments (invoice_id, amount, interest_amount, due_date) VALUES (?, ?, ?, ?)",
                        (invoice_id, amount, interest_per_installment, due_date)
                    )
            else:  # Weekly
                interest_per_installment = ((interest_rate / 100) * amount) / 4  # Divide monthly interest by 4 weeks
                for i in range(num_installments):
                    due_date = (start + timedelta(days=7 * (i + 1))).strftime("%Y-%m-%d")
                    self.controller.db.execute(
                        "INSERT INTO installments (invoice_id, amount, interest_amount, due_date) VALUES (?, ?, ?, ?)",
                        (invoice_id, amount, interest_per_installment, due_date)
                    )

            self.show_customer_profile(self.selected_customer_id)
            popup.destroy()

        ctk.CTkButton(
            popup,
            text=LANG[CURRENT_LANG]['create'],
            command=create_installments,
            font=THEME['font_bold'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10
        ).pack(pady=20)