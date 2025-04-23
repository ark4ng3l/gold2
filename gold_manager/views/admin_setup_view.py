import customtkinter as ctk
from tkinter import messagebox
from config import LANG, CURRENT_LANG, THEME

class AdminSetupView(ctk.CTkFrame):
    def __init__(self, parent, callback):
        super().__init__(parent, fg_color=THEME['background'])
        self.callback = callback
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        setup_frame = ctk.CTkFrame(self, fg_color=THEME['card_background'], corner_radius=20)
        setup_frame.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")
        setup_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            setup_frame,
            text="تنظیمات اولیه ادمین" if CURRENT_LANG == 'fa' else "Initial Admin Setup",
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).pack(pady=20)

        self.username_entry = ctk.CTkEntry(
            setup_frame,
            placeholder_text="نام کاربری" if CURRENT_LANG == 'fa' else "Username",
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            fg_color="#FFFFFF",
            text_color=THEME['text_dark'],
            border_color=THEME['accent'],
            corner_radius=10
        )
        self.username_entry.pack(pady=10)

        self.password_entry = ctk.CTkEntry(
            setup_frame,
            placeholder_text="رمز عبور" if CURRENT_LANG == 'fa' else "Password",
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            fg_color="#FFFFFF",
            text_color=THEME['text_dark'],
            border_color=THEME['accent'],
            corner_radius=10,
            show="*"
        )
        self.password_entry.pack(pady=10)

        self.confirm_password_entry = ctk.CTkEntry(
            setup_frame,
            placeholder_text="تکرار رمز عبور" if CURRENT_LANG == 'fa' else "Confirm Password",
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            fg_color="#FFFFFF",
            text_color=THEME['text_dark'],
            border_color=THEME['accent'],
            corner_radius=10,
            show="*"
        )
        self.confirm_password_entry.pack(pady=10)

        ctk.CTkButton(
            setup_frame,
            text="ثبت" if CURRENT_LANG == 'fa' else "Register",
            command=self.register_admin,
            font=THEME['font_bold'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10,
            height=40
        ).pack(pady=20)

    def register_admin(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not all([username, password, confirm_password]):
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "همه فیلدها الزامی هستند" if CURRENT_LANG == 'fa' else "All fields are required"
            )
            return

        if password != confirm_password:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "رمز عبور و تکرار آن مطابقت ندارند" if CURRENT_LANG == 'fa' else "Password and confirmation do not match"
            )
            return

        if len(password) < 8:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "رمز عبور باید حداقل 8 کاراکتر باشد" if CURRENT_LANG == 'fa' else "Password must be at least 8 characters"
            )
            return

        try:
            self.callback(username, password)
        except Exception as e:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                f"خطا در ثبت ادمین: {e}" if CURRENT_LANG == 'fa' else f"Error registering admin: {e}"
            )