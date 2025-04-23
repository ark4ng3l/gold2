import customtkinter as ctk
from datetime import datetime
import jdatetime
from tkcalendar import Calendar
from config import LANG, CURRENT_LANG, THEME
from utils.date_utils import jalali_to_gregorian, gregorian_to_jalali

class ReportsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=THEME['background'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Filters
        filters_frame = ctk.CTkFrame(self, fg_color=THEME['background'])
        filters_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        filters_frame.grid_columnconfigure(4, weight=1)

        ctk.CTkLabel(
            filters_frame,
            text=LANG[CURRENT_LANG]['reports'],
            font=THEME['font_bold'],
            text_color=THEME['text_light']
        ).grid(row=0, column=0, padx=10, sticky="w" if CURRENT_LANG == "en" else "e")

        # Start Date Filter with Calendar
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

        # End Date Filter with Calendar
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

        # Customer Filter
        customers = self.controller.db.fetchall("SELECT id, first_name, last_name FROM customers")
        self.customer_names = ["همه" if CURRENT_LANG == 'fa' else "All"] + [f"{c[1]} {c[2]}" for c in customers]
        self.customer_ids = [-1] + [c[0] for c in customers]

        ctk.CTkLabel(
            filters_frame,
            text="مشتری:" if CURRENT_LANG == 'fa' else "Customer:",
            font=THEME['font_small'],
            text_color=THEME['text_light']
        ).grid(row=0, column=7, padx=5)
        self.customer_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=self.customer_names,
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            button_color=THEME['button_fg'],
            button_hover_color=THEME['button_hover']
        )
        self.customer_filter.grid(row=0, column=8, padx=5)

        # Payment Type Filter
        self.payment_types = [
            "همه" if CURRENT_LANG == 'fa' else "All",
            LANG[CURRENT_LANG]['cash'],
            LANG[CURRENT_LANG]['card_to_card'],
            LANG[CURRENT_LANG]['sheba']
        ]
        ctk.CTkLabel(
            filters_frame,
            text="نوع پرداخت:" if CURRENT_LANG == 'fa' else "Payment Type:",
            font=THEME['font_small'],
            text_color=THEME['text_light']
        ).grid(row=0, column=9, padx=5)
        self.payment_type_filter = ctk.CTkOptionMenu(
            filters_frame,
            values=self.payment_types,
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            button_color=THEME['button_fg'],
            button_hover_color=THEME['button_hover']
        )
        self.payment_type_filter.grid(row=0, column=10, padx=5)

        ctk.CTkButton(
            filters_frame,
            text="فیلتر" if CURRENT_LANG == 'fa' else "Filter",
            command=self.load_reports,
            font=THEME['font_small'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10,
            width=100
        ).grid(row=0, column=11, padx=10)

        # Reports List
        reports_frame = ctk.CTkFrame(self, fg_color=THEME['card_background'], corner_radius=15)
        reports_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        reports_frame.grid_columnconfigure(0, weight=1)
        reports_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            reports_frame,
            text=LANG[CURRENT_LANG]['report_details'],
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w" if CURRENT_LANG == "en" else "e")

        self.reports_scroll = ctk.CTkScrollableFrame(reports_frame, fg_color=THEME['card_background'])
        self.reports_scroll.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

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

    def update_reports(self):
        """این تابع گزارش‌ها رو به‌روزرسانی می‌کنه"""
        self.load_reports()

    def load_reports(self):
        for widget in self.reports_scroll.winfo_children():
            widget.destroy()
            payment_date_jalali = gregorian_to_jalali(payment_date)
            payment_date_jalali = payment_date_jalali.split()[0]  # فقط تاریخ بدون ساعت

        query = """
            SELECT p.id, p.amount, p.payment_type, p.payment_details, p.payment_date, p.admin_id, 
                   i.invoice_number, c.first_name, c.last_name, u.username
            FROM payments p
            JOIN invoices i ON p.invoice_id = i.id
            JOIN customers c ON i.customer_id = c.id
            JOIN users u ON p.admin_id = u.id
            WHERE 1=1
        """
        params = []

        # Apply Date Filter (تبدیل تاریخ شمسی به میلادی)
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        if start_date:
            start_date_gregorian = jalali_to_gregorian(start_date)
            query += " AND p.payment_date >= ?"
            params.append(start_date_gregorian + " 00:00:00")
        if end_date:
            end_date_gregorian = jalali_to_gregorian(end_date)
            query += " AND p.payment_date <= ?"
            params.append(end_date_gregorian + " 23:59:59")

        # Apply Customer Filter
        selected_customer = self.customer_filter.get()
        customer_idx = self.customer_ids[self.customer_names.index(selected_customer)]
        if customer_idx != -1:
            query += " AND c.id = ?"
            params.append(customer_idx)

        # Apply Payment Type Filter
        payment_type = self.payment_type_filter.get()
        if payment_type != ("همه" if CURRENT_LANG == 'fa' else "All"):
            query += " AND p.payment_type = ?"
            params.append(payment_type)

        reports = self.controller.db.fetchall(query, params)
        if not reports:
            ctk.CTkLabel(
                self.reports_scroll,
                text="هیچ گزارشی یافت نشد" if CURRENT_LANG == 'fa' else "No reports found",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=5)
            return

        for report in reports:
            rep_id, amount, payment_type, payment_details, payment_date, admin_id, invoice_number, first_name, last_name, admin_username = report
            # تبدیل تاریخ پرداخت به شمسی
            payment_date_jalali = gregorian_to_jalali(payment_date)

            rep_frame = ctk.CTkFrame(self.reports_scroll, fg_color="#E0E0E0", corner_radius=10)
            rep_frame.pack(fill="x", padx=5, pady=5)

            ctk.CTkLabel(
                rep_frame,
                text=f"{LANG[CURRENT_LANG]['invoice_number']}: {invoice_number}",
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                rep_frame,
                text=f"{first_name} {last_name}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                rep_frame,
                text=f"{LANG[CURRENT_LANG]['amount']}: {amount:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                rep_frame,
                text=f"{LANG[CURRENT_LANG]['payment_type']}: {payment_type}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            if payment_details:
                ctk.CTkLabel(
                    rep_frame,
                    text=payment_details,
                    font=THEME['font_small'],
                    text_color=THEME['text_dark']
                ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                rep_frame,
                text=f"{LANG[CURRENT_LANG]['admin']}: {admin_username}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)

            ctk.CTkLabel(
                rep_frame,
                text=f"{LANG[CURRENT_LANG]['payment_date']}: {payment_date_jalali}",
                font=THEME['font_small'],
                text_color=THEME['text_dark']
            ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=2)