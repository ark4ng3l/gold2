import customtkinter as ctk
from tkinter import messagebox
from config import LANG, CURRENT_LANG, THEME

class LoginView(ctk.CTkFrame):
    def __init__(self, parent, callback):
        super().__init__(parent, fg_color=THEME['background'])
        self.callback = callback
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.login_frame = ctk.CTkFrame(self, fg_color=THEME['card_background'], corner_radius=20)
        self.login_frame.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")
        self.login_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.login_frame,
            text="ورود به سیستم" if CURRENT_LANG == 'fa' else "Login to System",
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).pack(pady=20)

        self.username_entry = ctk.CTkEntry(
            self.login_frame,
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
            self.login_frame,
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

        ctk.CTkButton(
            self.login_frame,
            text="ورود" if CURRENT_LANG == 'fa' else "Login",
            command=self.login,
            font=THEME['font_bold'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10,
            height=40
        ).pack(pady=20)

        self.error_label = ctk.CTkLabel(
            self.login_frame,
            text="",
            font=THEME['font_small'],
            text_color="red"
        )
        self.error_label.pack(pady=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            self.show_error("نام کاربری و رمز عبور الزامی هستند" if CURRENT_LANG == 'fa' else "Username and password are required")
            return

        try:
            self.callback(username, password)
        except Exception as e:
            self.show_error(f"خطا: {e}" if CURRENT_LANG == 'fa' else f"Error: {e}")

    def show_error(self, message):
        self.error_label.configure(text=message)