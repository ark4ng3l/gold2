import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tkcalendar import Calendar
import jdatetime
from config import LANG, CURRENT_LANG, THEME
from utils.date_utils import jalali_to_gregorian, gregorian_to_jalali

class InvoicesView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=THEME['background'])
        self.controller = controller
        self.create_widgets()  # این متد باید وجود داشته باشد

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Filters
        filters_frame = ctk.CTkFrame(self, fg_color=THEME['background'])
        filters_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        filters_frame.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(
            filters_frame,
            text=LANG[CURRENT_LANG]['invoices'],
            font=THEME['font_bold'],
            text_color=THEME['text_light']
        ).grid(row=0, column=0, padx=10, sticky="w" if CURRENT_LANG == "en" else "e")

        ctk.CTkLabel(
            filters_frame,
            text="از تاریخ (شمسی):" if CURRENT_LANG == 'fa' else "From Date (Jalali):",
            font=THEME['font_small'],
            text_color=THEME['text_light']
        ).grid(row=0, column=1, padx=5)
        self.start_date_entry = ctk.CTkEntry(
            filters_frame,
            placeholder_text="DD/MM/YYYY",
            width=120,
            font=THEME['font_small']
        )
        self.start_date_entry.grid(row=0, column=2, padx=5)

        ctk.CTkButton(
            filters_frame,
            text="📅",
            width=30,
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            command=lambda: self.show_calendar(self.start_date_entry)
        ).grid(row=0, column=3, padx=5)

        ctk.CTkLabel(
            filters_frame,
            text="تا تاریخ (شمسی):" if CURRENT_LANG == 'fa' else "To Date (Jalali):",
            font=THEME['font_small'],
            text_color=THEME['text_light']
        ).grid(row=0, column=4, padx=5)
        self.end_date_entry = ctk.CTkEntry(
            filters_frame,
            placeholder_text="DD/MM/YYYY",
            width=120,
            font=THEME['font_small']
        )
        self.end_date_entry.grid(row=0, column=5, padx=5)

        ctk.CTkButton(
            filters_frame,
            text="📅",
            width=30,
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            command=lambda: self.show_calendar(self.end_date_entry)
        ).grid(row=0, column=6, padx=5)

        ctk.CTkButton(
            filters_frame,
            text="فیلتر" if CURRENT_LANG == 'fa' else "Filter",
            command=self.load_invoices,
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10,
            width=100
        ).grid(row=0, column=7, padx=10)

        ctk.CTkButton(
            filters_frame,
            text="فاکتور جدید" if CURRENT_LANG == 'fa' else "New Invoice",
            command=self.open_new_invoice_window,
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10,
            width=100
        ).grid(row=0, column=8, padx=10)

        # Invoices List
        invoices_frame = ctk.CTkFrame(self, fg_color=THEME['card_background'], corner_radius=15)
        invoices_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        invoices_frame.grid_columnconfigure(0, weight=1)
        invoices_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            invoices_frame,
            text=LANG[CURRENT_LANG]['invoice_list'],
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w" if CURRENT_LANG == "en" else "e")

        self.invoices_scroll = ctk.CTkScrollableFrame(invoices_frame, fg_color=THEME['card_background'])
        self.invoices_scroll.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.load_invoices()

    def show_calendar(self, entry):
        """نمایش تقویم گرافیکی و تبدیل تاریخ انتخاب‌شده به شمسی"""
        calendar_window = ctk.CTkToplevel(self)
        calendar_window.title("انتخاب تاریخ" if CURRENT_LANG == 'fa' else "Select Date")
        calendar_window.geometry("300x300")

        # تقویم میلادی
        cal = Calendar(calendar_window, selectmode="day", date_pattern="y-mm-dd")
        cal.pack(pady=10)

        def set_date():
            selected_date = cal.get_date()  # تاریخ به فرمت YYYY-MM-DD
            # تبدیل تاریخ میلادی به شمسی
            g_date = datetime.strptime(selected_date, "%Y-%m-%d")
            j_date = jdatetime.date.fromgregorian(date=g_date)
            jalali_date = j_date.strftime("%d/%m/%Y")  # فرمت DD/MM/YYYY
            entry.delete(0, "end")
            entry.insert(0, jalali_date)
            calendar_window.destroy()

        ctk.CTkButton(
            calendar_window,
            text="تأیید" if CURRENT_LANG == 'fa' else "Confirm",
            command=set_date,
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover']
        ).pack(pady=10)

    def load_invoices(self):
        for widget in self.invoices_scroll.winfo_children():
            widget.destroy()

        query = """
            SELECT i.id, i.invoice_number, i.amount, i.interest, i.installment_type, 
                   i.start_date, i.num_installments, c.first_name, c.last_name
            FROM invoices i
            JOIN customers c ON i.customer_id = c.id
            WHERE 1=1
        """
        params = []

        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        if start_date:
            start_date_gregorian = jalali_to_gregorian(start_date)
            query += " AND i.start_date >= ?"
            params.append(start_date_gregorian)
        if end_date:
            end_date_gregorian = jalali_to_gregorian(end_date)
            query += " AND i.start_date <= ?"
            params.append(end_date_gregorian)

        invoices = self.controller.db.fetchall(query, params)
        if not invoices:
            ctk.CTkLabel(
                self.invoices_scroll,
                text="هیچ فاکتوری یافت نشد" if CURRENT_LANG == 'fa' else "No invoices found",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=5)
            return

        for invoice in invoices:
            inv_id, inv_number, amount, interest, installment_type, start_date, num_installments, first_name, last_name = invoice
            start_date_jalali = gregorian_to_jalali(start_date)

            inv_frame = ctk.CTkFrame(self.invoices_scroll, fg_color="#E0E0E0", corner_radius=10)
            inv_frame.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(
                inv_frame,
                text=f"{LANG[CURRENT_LANG]['invoice_number']}: {inv_number}",
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                inv_frame,
                text=f"{first_name} {last_name}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                inv_frame,
                text=f"{LANG[CURRENT_LANG]['amount']}: {amount:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                inv_frame,
                text=f"{LANG[CURRENT_LANG]['interest']}: {interest}%",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            if installment_type:
                ctk.CTkLabel(
                    inv_frame,
                    text=f"{LANG[CURRENT_LANG]['installment_type']}: {installment_type} ({num_installments} قسط)",
                    font=THEME['font_small'],
                    text_color=THEME['text_dark']
                ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                inv_frame,
                text=f"{LANG[CURRENT_LANG]['start_date']}: {start_date_jalali}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkButton(
                inv_frame,
                text="جزئیات" if CURRENT_LANG == 'fa' else "Details",
                command=lambda inv_id=inv_id: self.show_invoice_details(inv_id),
                font=THEME['font_small'],
                fg_color=THEME['button_fg'],
                hover_color=THEME['button_hover'],
                corner_radius=10,
                width=100
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=5)

    def open_new_invoice_window(self):
        self.new_invoice_window = ctk.CTkToplevel(self)
        self.new_invoice_window.title("فاکتور جدید" if CURRENT_LANG == 'fa' else "New Invoice")
        self.new_invoice_window.geometry("600x700")

        ctk.CTkLabel(
            self.new_invoice_window,
            text="فاکتور جدید" if CURRENT_LANG == 'fa' else "New Invoice",
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).pack(pady=20)

        # Customer Selection
        customers = self.controller.db.fetchall("SELECT id, first_name, last_name FROM customers")
        customer_names = [f"{c[1]} {c[2]}" for c in customers]
        self.customer_ids = [c[0] for c in customers]

        ctk.CTkLabel(
            self.new_invoice_window,
            text="مشتری:" if CURRENT_LANG == 'fa' else "Customer:",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)
        self.customer_menu = ctk.CTkOptionMenu(
            self.new_invoice_window,
            values=customer_names if customer_names else ["هیچ مشتری وجود ندارد"],
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            button_color=THEME['button_fg'],
            button_hover_color=THEME['button_hover']
        )
        self.customer_menu.pack(pady=5)

        # Invoice Details
        ctk.CTkLabel(
            self.new_invoice_window,
            text="شماره فاکتور:" if CURRENT_LANG == 'fa' else "Invoice Number:",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)
        self.invoice_number_entry = ctk.CTkEntry(
            self.new_invoice_window,
            placeholder_text="شماره فاکتور" if CURRENT_LANG == 'fa' else "Invoice Number",
            width=300,
            font=THEME['font_small']
        )
        self.invoice_number_entry.pack(pady=5)

        ctk.CTkLabel(
            self.new_invoice_window,
            text="مبلغ (تومان):" if CURRENT_LANG == 'fa' else "Amount (Toman):",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)
        self.amount_entry = ctk.CTkEntry(
            self.new_invoice_window,
            placeholder_text="مبلغ" if CURRENT_LANG == 'fa' else "Amount",
            width=300,
            font=THEME['font_small']
        )
        self.amount_entry.pack(pady=5)

        ctk.CTkLabel(
            self.new_invoice_window,
            text="نرخ سود (درصد):" if CURRENT_LANG == 'fa' else "Interest Rate (%):",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)
        self.interest_entry = ctk.CTkEntry(
            self.new_invoice_window,
            placeholder_text="نرخ سود" if CURRENT_LANG == 'fa' else "Interest Rate",
            width=300,
            font=THEME['font_small']
        )
        self.interest_entry.pack(pady=5)

        # Installment Options
        ctk.CTkLabel(
            self.new_invoice_window,
            text="نوع قسط:" if CURRENT_LANG == 'fa' else "Installment Type:",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)
        self.installment_type_menu = ctk.CTkOptionMenu(
            self.new_invoice_window,
            values=["بدون قسط", "ماهانه", "دو ماهه", "سه ماهه"] if CURRENT_LANG == 'fa' else ["No Installments", "Monthly", "Bimonthly", "Quarterly"],
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            button_color=THEME['button_fg'],
            button_hover_color=THEME['button_hover']
        )
        self.installment_type_menu.pack(pady=5)

        ctk.CTkLabel(
            self.new_invoice_window,
            text="تعداد اقساط:" if CURRENT_LANG == 'fa' else "Number of Installments:",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)
        self.num_installments_entry = ctk.CTkEntry(
            self.new_invoice_window,
            placeholder_text="تعداد اقساط" if CURRENT_LANG == 'fa' else "Number of Installments",
            width=300,
            font=THEME['font_small']
        )
        self.num_installments_entry.pack(pady=5)

        ctk.CTkLabel(
            self.new_invoice_window,
            text="تاریخ شروع (شمسی):" if CURRENT_LANG == 'fa' else "Start Date (Jalali):",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)
        self.start_date_entry_new = ctk.CTkEntry(
            self.new_invoice_window,
            placeholder_text="DD/MM/YYYY",
            width=300,
            font=THEME['font_small']
        )
        self.start_date_entry_new.pack(pady=5)

        ctk.CTkButton(
            self.new_invoice_window,
            text="📅",
            width=30,
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            command=lambda: self.show_calendar(self.start_date_entry_new)
        ).pack(pady=5)

        # Products
        ctk.CTkLabel(
            self.new_invoice_window,
            text="محصولات:" if CURRENT_LANG == 'fa' else "Products:",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)
        self.products_frame = ctk.CTkFrame(self.new_invoice_window, fg_color=THEME['card_background'])
        self.products_frame.pack(fill="x", padx=20, pady=5)

        self.products = []
        self.add_product_entry()

        ctk.CTkButton(
            self.new_invoice_window,
            text="اضافه کردن محصول" if CURRENT_LANG == 'fa' else "Add Product",
            command=self.add_product_entry,
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10,
            width=150
        ).pack(pady=5)

        ctk.CTkButton(
            self.new_invoice_window,
            text="ثبت فاکتور" if CURRENT_LANG == 'fa' else "Create Invoice",
            command=self.create_invoice,
            font=THEME['font_bold'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10,
            height=40
        ).pack(pady=20)

    def add_product_entry(self):
        product_frame = ctk.CTkFrame(self.products_frame, fg_color=THEME['card_background'])
        product_frame.pack(fill="x", pady=5)

        name_entry = ctk.CTkEntry(
            product_frame,
            placeholder_text="نام محصول" if CURRENT_LANG == 'fa' else "Product Name",
            width=200,
            font=THEME['font_small']
        )
        name_entry.pack(side="left", padx=5)

        price_entry = ctk.CTkEntry(
            product_frame,
            placeholder_text="قیمت (تومان)" if CURRENT_LANG == 'fa' else "Price (Toman)",
            width=150,
            font=THEME['font_small']
        )
        price_entry.pack(side="left", padx=5)

        self.products.append((name_entry, price_entry))

    def create_invoice(self):
        customer_idx = self.customer_ids[self.customer_menu.get_values().index(self.customer_menu.get())] if self.customer_ids else None
        if not customer_idx:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "لطفاً یک مشتری انتخاب کنید" if CURRENT_LANG == 'fa' else "Please select a customer"
            )
            return

        invoice_number = self.invoice_number_entry.get().strip()
        amount = self.amount_entry.get().strip()
        interest = self.interest_entry.get().strip()
        installment_type = self.installment_type_menu.get()
        num_installments = self.num_installments_entry.get().strip()
        start_date = self.start_date_entry_new.get().strip()

        if not all([invoice_number, amount, start_date]):
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "شماره فاکتور، مبلغ و تاریخ شروع الزامی هستند" if CURRENT_LANG == 'fa' else "Invoice number, amount, and start date are required"
            )
            return

        try:
            amount = float(amount)
            interest = float(interest) if interest else 0
            num_installments = int(num_installments) if num_installments else 0
        except ValueError:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "مبلغ، نرخ سود و تعداد اقساط باید عددی باشند" if CURRENT_LANG == 'fa' else "Amount, interest rate, and number of installments must be numeric"
            )
            return

        if installment_type != ("بدون قسط" if CURRENT_LANG == 'fa' else "No Installments") and num_installments <= 0:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "تعداد اقساط باید بیشتر از صفر باشد" if CURRENT_LANG == 'fa' else "Number of installments must be greater than zero"
            )
            return

        # تبدیل تاریخ شمسی به میلادی
        start_date_gregorian = jalali_to_gregorian(start_date)

        try:
            self.controller.db.execute(
                """
                INSERT INTO invoices (customer_id, invoice_number, amount, interest, installment_type, start_date, num_installments)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (customer_idx, invoice_number, amount, interest, installment_type, start_date_gregorian, num_installments if installment_type != ("بدون قسط" if CURRENT_LANG == 'fa' else "No Installments") else 0)
            )

            invoice_id = self.controller.db.fetchone("SELECT last_insert_rowid()")[0]

            for name_entry, price_entry in self.products:
                name = name_entry.get().strip()
                price = price_entry.get().strip()
                if name and price:
                    try:
                        price = float(price)
                        self.controller.db.execute(
                            "INSERT INTO products (invoice_id, name, price) VALUES (?, ?, ?)",
                            (invoice_id, name, price)
                        )
                    except ValueError:
                        messagebox.showerror(
                            "خطا" if CURRENT_LANG == 'fa' else "Error",
                            "قیمت محصول باید عددی باشد" if CURRENT_LANG == 'fa' else "Product price must be numeric"
                        )
                        return

            if installment_type != ("بدون قسط" if CURRENT_LANG == 'fa' else "No Installments"):
                interval = {"ماهانه": 1, "دو ماهه": 2, "سه ماهه": 3, "Monthly": 1, "Bimonthly": 2, "Quarterly": 3}[installment_type]
                installment_amount = amount / num_installments
                interest_amount = (amount * (interest / 100)) / num_installments
                start_date = datetime.strptime(start_date_gregorian, "%Y-%m-%d")
                for i in range(num_installments):
                    due_date = start_date + relativedelta(months=i * interval)
                    self.controller.db.execute(
                        "INSERT INTO installments (invoice_id, amount, interest_amount, due_date) VALUES (?, ?, ?, ?)",
                        (invoice_id, installment_amount, interest_amount, due_date.strftime("%Y-%m-%d"))
                    )

            self.new_invoice_window.destroy()
            self.load_invoices()
            messagebox.showinfo(
                "موفقیت" if CURRENT_LANG == 'fa' else "Success",
                "فاکتور با موفقیت ثبت شد" if CURRENT_LANG == 'fa' else "Invoice created successfully"
            )
        except Exception as e:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                f"خطا در ثبت فاکتور: {e}" if CURRENT_LANG == 'fa' else f"Error creating invoice: {e}"
            )

    def show_invoice_details(self, invoice_id):
        details_window = ctk.CTkToplevel(self)
        details_window.title("جزئیات فاکتور" if CURRENT_LANG == 'fa' else "Invoice Details")
        details_window.geometry("600x700")

        invoice = self.controller.db.fetchone(
            """
            SELECT i.invoice_number, i.amount, i.interest, i.installment_type, i.start_date, i.num_installments,
                   c.first_name, c.last_name
            FROM invoices i
            JOIN customers c ON i.customer_id = c.id
            WHERE i.id = ?
            """,
            (invoice_id,)
        )

        if not invoice:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "فاکتور یافت نشد" if CURRENT_LANG == 'fa' else "Invoice not found"
            )
            details_window.destroy()
            return

        invoice_number, amount, interest, installment_type, start_date, num_installments, first_name, last_name = invoice
        start_date_jalali = gregorian_to_jalali(start_date)

        ctk.CTkLabel(
            details_window,
            text=f"{LANG[CURRENT_LANG]['invoice_number']}: {invoice_number}",
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).pack(pady=10)

        ctk.CTkLabel(
            details_window,
            text=f"{LANG[CURRENT_LANG]['customer']}: {first_name} {last_name}",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)

        ctk.CTkLabel(
            details_window,
            text=f"{LANG[CURRENT_LANG]['amount']}: {amount:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)

        ctk.CTkLabel(
            details_window,
            text=f"{LANG[CURRENT_LANG]['interest']}: {interest}%",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)

        ctk.CTkLabel(
            details_window,
            text=f"{LANG[CURRENT_LANG]['start_date']}: {start_date_jalali}",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)

        if installment_type != ("بدون قسط" if CURRENT_LANG == 'fa' else "No Installments"):
            ctk.CTkLabel(
                details_window,
                text=f"{LANG[CURRENT_LANG]['installment_type']}: {installment_type} ({num_installments} قسط)",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(pady=5)

        # Products
        ctk.CTkLabel(
            details_window,
            text="محصولات:" if CURRENT_LANG == 'fa' else "Products:",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=10)
        products = self.controller.db.fetchall("SELECT name, price FROM products WHERE invoice_id = ?", (invoice_id,))
        for product in products:
            name, price = product
            ctk.CTkLabel(
                details_window,
                text=f"{name}: {price:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=20, pady=2)

        # Installments
        if installment_type != ("بدون قسط" if CURRENT_LANG == 'fa' else "No Installments"):
            ctk.CTkLabel(
                details_window,
                text="اقساط:" if CURRENT_LANG == 'fa' else "Installments:",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(pady=10)
            installments = self.controller.db.fetchall(
                "SELECT id, amount, interest_amount, due_date, paid FROM installments WHERE invoice_id = ?",
                (invoice_id,)
            )
            for inst in installments:
                inst_id, inst_amount, inst_interest, due_date, paid = inst
                due_date_jalali = gregorian_to_jalali(due_date + " 00:00:00").split()[0]  # فقط تاریخ رو می‌خوایم

                inst_frame = ctk.CTkFrame(details_window, fg_color="#E0E0E0", corner_radius=10)
                inst_frame.pack(fill="x", padx=20, pady=5)

                ctk.CTkLabel(
                    inst_frame,
                    text=f"{LANG[CURRENT_LANG]['amount']}: {inst_amount:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
                    font=THEME['font_small'],
                    text_color=THEME['text_dark']
                ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

                ctk.CTkLabel(
                    inst_frame,
                    text=f"{LANG[CURRENT_LANG]['interest']}: {inst_interest:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
                    font=THEME['font_small'],
                    text_color=THEME['text_dark']
                ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

                ctk.CTkLabel(
                    inst_frame,
                    text=f"{LANG[CURRENT_LANG]['due_date']}: {due_date_jalali}",
                    font=THEME['font_small'],
                    text_color=THEME['text_dark']
                ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

                status = "پرداخت‌شده" if paid else "پرداخت‌نشده"
                if CURRENT_LANG == "en":
                    status = "Paid" if paid else "Unpaid"
                ctk.CTkLabel(
                    inst_frame,
                    text=f"{LANG[CURRENT_LANG]['status']}: {status}",
                    font=THEME['font_small'],
                    text_color="green" if paid else "red"
                ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

                if not paid:
                    ctk.CTkButton(
                        inst_frame,
                        text="پرداخت" if CURRENT_LANG == 'fa' else "Pay",
                        command=lambda inst_id=inst_id: self.pay_installment(inst_id, details_window),
                        font=THEME['font_small'],
                        fg_color=THEME['button_fg'],
                        hover_color=THEME['button_hover'],
                        corner_radius=10,
                        width=100
                    ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=5)

        # Payments
        ctk.CTkLabel(
            details_window,
            text="پرداخت‌ها:" if CURRENT_LANG == 'fa' else "Payments:",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=10)
        payments = self.controller.db.fetchall(
            """
            SELECT p.id, p.amount, p.payment_type, p.payment_details, p.payment_date, u.username
            FROM payments p
            JOIN users u ON p.admin_id = u.id
            WHERE p.invoice_id = ?
            """,
            (invoice_id,)
        )
        for payment in payments:
            pay_id, pay_amount, pay_type, pay_details, pay_date, admin_username = payment
            pay_date_jalali = gregorian_to_jalali(pay_date)

            pay_frame = ctk.CTkFrame(details_window, fg_color="#E0E0E0", corner_radius=10)
            pay_frame.pack(fill="x", padx=20, pady=5)

            ctk.CTkLabel(
                pay_frame,
                text=f"{LANG[CURRENT_LANG]['amount']}: {pay_amount:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                pay_frame,
                text=f"{LANG[CURRENT_LANG]['payment_type']}: {pay_type}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            if pay_details:
                ctk.CTkLabel(
                    pay_frame,
                    text=pay_details,
                    font=THEME['font_small'],
                    text_color=THEME['text_dark']
                ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                pay_frame,
                text=f"{LANG[CURRENT_LANG]['admin']}: {admin_username}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                pay_frame,
                text=f"{LANG[CURRENT_LANG]['payment_date']}: {pay_date_jalali}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

    def pay_installment(self, installment_id, details_window):
        payment_window = ctk.CTkToplevel(self)
        payment_window.title("پرداخت قسط" if CURRENT_LANG == 'fa' else "Pay Installment")
        payment_window.geometry("400x500")

        ctk.CTkLabel(
            payment_window,
            text="پرداخت قسط" if CURRENT_LANG == 'fa' else "Pay Installment",
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).pack(pady=20)

        installment = self.controller.db.fetchone(
            "SELECT amount, interest_amount FROM installments WHERE id = ?",
            (installment_id,)
        )
        amount, interest_amount = installment
        total_amount = amount + interest_amount

        ctk.CTkLabel(
            payment_window,
            text=f"{LANG[CURRENT_LANG]['total_amount']}: {total_amount:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=10)

        ctk.CTkLabel(
            payment_window,
            text="نوع پرداخت:" if CURRENT_LANG == 'fa' else "Payment Type:",
            font=THEME['font_small'],
            text_color=THEME['text_dark']
        ).pack(pady=5)
        payment_type_menu = ctk.CTkOptionMenu(
            payment_window,
            values=[LANG[CURRENT_LANG]['cash'], LANG[CURRENT_LANG]['card_to_card'], LANG[CURRENT_LANG]['sheba']],
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            button_color=THEME['button_fg'],
            button_hover_color=THEME['button_hover']
        )
        payment_type_menu.pack(pady=5)

        payment_details_entry = ctk.CTkEntry(
            payment_window,
            placeholder_text="جزئیات پرداخت (اختیاری)" if CURRENT_LANG == 'fa' else "Payment Details (Optional)",
            width=300,
            font=THEME['font_small']
        )
        payment_details_entry.pack(pady=10)

        def confirm_payment():
            payment_type = payment_type_menu.get()
            payment_details = payment_details_entry.get().strip() or None
            invoice_id = self.controller.db.fetchone("SELECT invoice_id FROM installments WHERE id = ?", (installment_id,))[0]

            try:
                self.controller.db.execute(
                    "INSERT INTO payments (invoice_id, amount, payment_type, payment_details, admin_id) VALUES (?, ?, ?, ?, ?)",
                    (invoice_id, total_amount, payment_type, payment_details, self.controller.current_user['id'])
                )
                self.controller.db.execute(
                    "UPDATE installments SET paid = 1 WHERE id = ?",
                    (installment_id,)
                )
                payment_window.destroy()
                details_window.destroy()
                self.load_invoices()
                messagebox.showinfo(
                    "موفقیت" if CURRENT_LANG == 'fa' else "Success",
                    "پرداخت با موفقیت ثبت شد" if CURRENT_LANG == 'fa' else "Payment recorded successfully"
                )
            except Exception as e:
                messagebox.showerror(
                    "خطا" if CURRENT_LANG == 'fa' else "Error",
                    f"خطا در ثبت پرداخت: {e}" if CURRENT_LANG == 'fa' else f"Error recording payment: {e}"
                )

        ctk.CTkButton(
            payment_window,
            text="تأیید پرداخت" if CURRENT_LANG == 'fa' else "Confirm Payment",
            command=confirm_payment,
            font=THEME['font_bold'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10,
            height=40
        ).pack(pady=20)