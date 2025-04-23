import customtkinter as ctk
from datetime import datetime, timedelta
import platform
import winsound
import os
from config import LANG, CURRENT_LANG, THEME

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=THEME['background'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Stats Cards
        stats_frame = ctk.CTkFrame(self, fg_color=THEME['background'])
        stats_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.total_paid_label = ctk.CTkLabel(
            stats_frame,
            text="",
            font=THEME['font_bold'],
            fg_color=THEME['card_background'],
            corner_radius=15,
            text_color=THEME['text_dark'],
            height=100
        )
        self.total_paid_label.grid(row=0, column=0, padx=10, pady=10)

        self.total_due_label = ctk.CTkLabel(
            stats_frame,
            text="",
            font=THEME['font_bold'],
            fg_color=THEME['card_background'],
            corner_radius=15,
            text_color=THEME['text_dark'],
            height=100
        )
        self.total_due_label.grid(row=0, column=1, padx=10, pady=10)

        self.avg_interest_label = ctk.CTkLabel(
            stats_frame,
            text="",
            font=THEME['font_bold'],
            fg_color=THEME['card_background'],
            corner_radius=15,
            text_color=THEME['text_dark'],
            height=100
        )
        self.avg_interest_label.grid(row=0, column=2, padx=10, pady=10)

        # Notifications
        notifications_frame = ctk.CTkFrame(self, fg_color=THEME['card_background'], corner_radius=15)
        notifications_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        notifications_frame.grid_columnconfigure(0, weight=1)
        notifications_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            notifications_frame,
            text=LANG[CURRENT_LANG]['notifications'],
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w" if CURRENT_LANG == "en" else "e")

        self.notifications_scroll = ctk.CTkScrollableFrame(notifications_frame, fg_color=THEME['card_background'])
        self.notifications_scroll.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    def update_dashboard(self, stats):
        self.total_paid_label.configure(text=f"{LANG[CURRENT_LANG]['total_paid']}\n{stats[0]}")
        self.total_due_label.configure(text=f"{LANG[CURRENT_LANG]['total_due']}\n{stats[1]}")
        self.avg_interest_label.configure(text=f"{LANG[CURRENT_LANG]['avg_interest']}\n{stats[2]}")

        # Load Notifications
        for widget in self.notifications_scroll.winfo_children():
            widget.destroy()

        today = datetime.today()
        notifications = self.controller.db.fetchall(
            """
            SELECT i.id, i.due_date, i.amount, i.interest_amount, inv.installment_type, inv.customer_id, c.first_name, c.last_name
            FROM installments i
            JOIN invoices inv ON i.invoice_id = inv.id
            JOIN customers c ON inv.customer_id = c.id
            WHERE i.paid = 0
            """
        )

        has_notification = False
        for notif in notifications:
            inst_id, due_date, amount, interest_amount, installment_type, customer_id, first_name, last_name = notif
            due = datetime.strptime(due_date, "%Y-%m-%d")
            delta = (due - today).days

            if installment_type == LANG[CURRENT_LANG]['monthly'] and 0 <= delta <= 5:
                ctk.CTkLabel(
                    self.notifications_scroll,
                    text=f"{LANG[CURRENT_LANG]['due_soon']}: {first_name} {last_name} - {amount + interest_amount:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'} ({due_date})",
                    font=THEME['font_small'],
                    text_color="red"
                ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=5)
                has_notification = True
            elif installment_type == LANG[CURRENT_LANG]['weekly'] and 0 <= delta <= 2:
                ctk.CTkLabel(
                    self.notifications_scroll,
                    text=f"{LANG[CURRENT_LANG]['due_soon']}: {first_name} {last_name} - {amount + interest_amount:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'} ({due_date})",
                    font=THEME['font_small'],
                    text_color="red"
                ).pack(anchor="w" if CURRENT_LANG == "en" else "e", padx=10, pady=5)
                has_notification = True

        if has_notification:
            self.play_notification_sound()

    def play_notification_sound(self):
        if platform.system() == "Windows":
            winsound.Beep(1000, 500)  # Frequency 1000Hz, duration 500ms
        else:
            # For Mac/Linux, using a system beep (requires a sound file or system command)
            os.system("afplay /System/Library/Sounds/Glass.aiff")  # For Mac