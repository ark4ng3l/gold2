import customtkinter as ctk
from tkinter import messagebox
from config import LANG, CURRENT_LANG, THEME

class PaymentView(ctk.CTkToplevel):
    def __init__(self, parent, controller, customer_id, invoice_id, installment_id, amount, interest_amount, callback):
        super().__init__(parent)
        self.controller = controller
        self.customer_id = customer_id
        self.invoice_id = invoice_id
        self.installment_id = installment_id
        self.amount = amount + interest_amount
        self.callback = callback
        self.title(LANG[CURRENT_LANG]['pay'])
        self.geometry("600x600")
        self.configure(fg_color=THEME['background'])
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        payment_frame = ctk.CTkFrame(self, fg_color=THEME['card_background'], corner_radius=20)
        payment_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        payment_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            payment_frame,
            text=f"{LANG[CURRENT_LANG]['pay']} - {LANG[CURRENT_LANG]['amount']}: {self.amount:,.2f} {'تومان' if CURRENT_LANG == 'fa' else 'Toman'}",
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).pack(pady=20)

        # Payment Type
        ctk.CTkLabel(
            payment_frame,
            text=LANG[CURRENT_LANG]['payment_type'],
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            text_color=THEME['text_dark']
        ).pack(pady=5)

        self.payment_type = ctk.CTkOptionMenu(
            payment_frame,
            values=[
                LANG[CURRENT_LANG]['cash'],
                LANG[CURRENT_LANG]['card_to_card'],
                LANG[CURRENT_LANG]['sheba']
            ],
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            fg_color=THEME['button_fg'],
            button_color=THEME['button_fg'],
            button_hover_color=THEME['button_hover'],
            command=self.update_payment_fields
        )
        self.payment_type.pack(pady=10)

        # Payment Details Frame
        self.details_frame = ctk.CTkFrame(payment_frame, fg_color=THEME['card_background'])
        self.details_frame.pack(pady=10, fill="x", padx=20)

        self.source_entry = None
        self.destination_entry = None

        # Admin Info
        ctk.CTkLabel(
            payment_frame,
            text=f"{LANG[CURRENT_LANG]['admin']}: {self.controller.current_user['username']}",
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            text_color=THEME['text_dark']
        ).pack(pady=5)

        # Invoice Info
        invoice = self.controller.db.fetchone(
            "SELECT invoice_number FROM invoices WHERE id = ?",
            (self.invoice_id,)
        )
        ctk.CTkLabel(
            payment_frame,
            text=f"{LANG[CURRENT_LANG]['invoice_number']}: {invoice[0]}",
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            text_color=THEME['text_dark']
        ).pack(pady=5)

        ctk.CTkButton(
            payment_frame,
            text=LANG[CURRENT_LANG]['pay'],
            command=self.process_payment,
            font=THEME['font_bold'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10,
            height=40
        ).pack(pady=20)

    def update_payment_fields(self, payment_type):
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        if payment_type == LANG[CURRENT_LANG]['card_to_card']:
            ctk.CTkLabel(
                self.details_frame,
                text=LANG[CURRENT_LANG]['source_card'],
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                text_color=THEME['text_dark']
            ).pack(pady=5)
            self.source_entry = ctk.CTkEntry(
                self.details_frame,
                placeholder_text="XXXX-XXXX-XXXX-XXXX",
                width=300,
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                fg_color="#FFFFFF",
                text_color=THEME['text_dark'],
                border_color=THEME['accent'],
                corner_radius=10
            )
            self.source_entry.pack(pady=5)

            ctk.CTkLabel(
                self.details_frame,
                text=LANG[CURRENT_LANG]['destination_card'],
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                text_color=THEME['text_dark']
            ).pack(pady=5)
            self.destination_entry = ctk.CTkEntry(
                self.details_frame,
                placeholder_text="XXXX-XXXX-XXXX-XXXX",
                width=300,
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                fg_color="#FFFFFF",
                text_color=THEME['text_dark'],
                border_color=THEME['accent'],
                corner_radius=10
            )
            self.destination_entry.pack(pady=5)

        elif payment_type == LANG[CURRENT_LANG]['sheba']:
            ctk.CTkLabel(
                self.details_frame,
                text=LANG[CURRENT_LANG]['source_sheba'],
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                text_color=THEME['text_dark']
            ).pack(pady=5)
            self.source_entry = ctk.CTkEntry(
                self.details_frame,
                placeholder_text="IRXXXXXXXXXXXXXXXXXXXXXXXX",
                width=300,
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                fg_color="#FFFFFF",
                text_color=THEME['text_dark'],
                border_color=THEME['accent'],
                corner_radius=10
            )
            self.source_entry.pack(pady=5)

            ctk.CTkLabel(
                self.details_frame,
                text=LANG[CURRENT_LANG]['destination_sheba'],
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                text_color=THEME['text_dark']
            ).pack(pady=5)
            self.destination_entry = ctk.CTkEntry(
                self.details_frame,
                placeholder_text="IRXXXXXXXXXXXXXXXXXXXXXXXX",
                width=300,
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                fg_color="#FFFFFF",
                text_color=THEME['text_dark'],
                border_color=THEME['accent'],
                corner_radius=10
            )
            self.destination_entry.pack(pady=5)

    def process_payment(self):
        payment_type = self.payment_type.get()
        payment_details = ""

        if payment_type == LANG[CURRENT_LANG]['card_to_card']:
            source = self.source_entry.get().strip()
            destination = self.destination_entry.get().strip()
            if not (source and destination):
                messagebox.showerror(
                    "خطا" if CURRENT_LANG == 'fa' else "Error",
                    "لطفاً اطلاعات کارت را وارد کنید" if CURRENT_LANG == 'fa' else "Please enter card details"
                )
                return
            payment_details = f"{LANG[CURRENT_LANG]['source_card']}: {source}, {LANG[CURRENT_LANG]['destination_card']}: {destination}"
        elif payment_type == LANG[CURRENT_LANG]['sheba']:
            source = self.source_entry.get().strip()
            destination = self.destination_entry.get().strip()
            if not (source and destination):
                messagebox.showerror(
                    "خطا" if CURRENT_LANG == 'fa' else "Error",
                    "لطفاً اطلاعات شبا را وارد کنید" if CURRENT_LANG == 'fa' else "Please enter Sheba details"
                )
                return
            payment_details = f"{LANG[CURRENT_LANG]['source_sheba']}: {source}, {LANG[CURRENT_LANG]['destination_sheba']}: {destination}"

        try:
            # Register payment
            self.controller.db.execute(
                "INSERT INTO payments (invoice_id, installment_id, amount, payment_type, payment_details, admin_id) VALUES (?, ?, ?, ?, ?, ?)",
                (self.invoice_id, self.installment_id, self.amount, payment_type, payment_details, self.controller.current_user['id'])
            )
            # Update installment
            self.controller.db.execute(
                "UPDATE installments SET paid = 1, paid_at = CURRENT_TIMESTAMP WHERE id = ?",
                (self.installment_id,)
            )
            messagebox.showinfo(
                "موفقیت" if CURRENT_LANG == 'fa' else "Success",
                "پرداخت با موفقیت انجام شد" if CURRENT_LANG == 'fa' else "Payment completed successfully"
            )
            self.callback()
            self.destroy()
        except Exception as e:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                f"خطا در ثبت پرداخت: {e}" if CURRENT_LANG == 'fa' else f"Error processing payment: {e}"
            )