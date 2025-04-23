import customtkinter as ctk
from tkinter import messagebox
from config import LANG, CURRENT_LANG, THEME, set_language

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=THEME['background'])
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        settings_frame = ctk.CTkFrame(self, fg_color=THEME['card_background'], corner_radius=20)
        settings_frame.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")
        settings_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            settings_frame,
            text=LANG[CURRENT_LANG]['settings'],
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).pack(pady=20)

        # Language Selection
        ctk.CTkLabel(
            settings_frame,
            text="زبان:" if CURRENT_LANG == 'fa' else "Language:",
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            text_color=THEME['text_dark']
        ).pack(pady=5)
        self.language_menu = ctk.CTkOptionMenu(
            settings_frame,
            values=["فارسی", "English"],
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            fg_color=THEME['button_fg'],
            button_color=THEME['button_fg'],
            button_hover_color=THEME['button_hover'],
            dropdown_fg_color=THEME['card_background'],
            dropdown_text_color=THEME['text_dark'],
            command=self.change_language
        )
        self.language_menu.pack(pady=10)

        # Change Password
        ctk.CTkLabel(
            settings_frame,
            text="تغییر رمز عبور" if CURRENT_LANG == 'fa' else "Change Password",
            font=THEME['font_bold'],
            text_color=THEME['text_dark']
        ).pack(pady=20)

        self.current_password_entry = ctk.CTkEntry(
            settings_frame,
            placeholder_text="رمز عبور فعلی" if CURRENT_LANG == 'fa' else "Current Password",
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            fg_color="#FFFFFF",
            text_color=THEME['text_dark'],
            border_color=THEME['accent'],
            corner_radius=10,
            show="*"
        )
        self.current_password_entry.pack(pady=10)

        self.new_password_entry = ctk.CTkEntry(
            settings_frame,
            placeholder_text="رمز عبور جدید" if CURRENT_LANG == 'fa' else "New Password",
            width=300,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            fg_color="#FFFFFF",
            text_color=THEME['text_dark'],
            border_color=THEME['accent'],
            corner_radius=10,
            show="*"
        )
        self.new_password_entry.pack(pady=10)

        self.confirm_password_entry = ctk.CTkEntry(
            settings_frame,
            placeholder_text="تکرار رمز عبور جدید" if CURRENT_LANG == 'fa' else "Confirm New Password",
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
            settings_frame,
            text="تغییر رمز عبور" if CURRENT_LANG == 'fa' else "Change Password",
            command=self.change_password,
            font=THEME['font_bold'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            corner_radius=10,
            height=40
        ).pack(pady=20)

    def update_settings(self):
        """این تابع تنظیمات رو به‌روزرسانی می‌کنه"""
        pass  # فعلاً نیازی به به‌روزرسانی داده‌ها نیست

    def change_language(self, language):
        try:
            new_lang = 'fa' if language == "فارسی" else 'en'
            set_language(new_lang)  # ابتدا زبان را تغییر دهید
        
        # حالا از LANG با زبان جدید استفاده کنید
            messagebox.showinfo(
                LANG[new_lang]['success'], 
                LANG[new_lang]['lang_changed_msg']
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def change_password(self):
        current_password = self.current_password_entry.get().strip()
        new_password = self.new_password_entry.get().strip()
        confirm_password = self.confirm_password_entry.get().strip()

        if not all([current_password, new_password, confirm_password]):
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "همه فیلدها الزامی هستند" if CURRENT_LANG == 'fa' else "All fields are required"
            )
            return

        if new_password != confirm_password:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "رمز عبور جدید و تکرار آن مطابقت ندارند" if CURRENT_LANG == 'fa' else "New password and confirmation do not match"
            )
            return

        if len(new_password) < 8:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                "رمز عبور جدید باید حداقل 8 کاراکتر باشد" if CURRENT_LANG == 'fa' else "New password must be at least 8 characters"
            )
            return

        try:
            user = self.controller.auth_controller.login(self.controller.current_user['username'], current_password)
            if not user:
                messagebox.showerror(
                    "خطا" if CURRENT_LANG == 'fa' else "Error",
                    "رمز عبور فعلی اشتباه است" if CURRENT_LANG == 'fa' else "Current password is incorrect"
                )
                return

            self.controller.auth_controller.register(self.controller.current_user['username'], new_password, self.controller.current_user['role'])
            messagebox.showinfo(
                "موفقیت" if CURRENT_LANG == 'fa' else "Success",
                "رمز عبور با موفقیت تغییر کرد" if CURRENT_LANG == 'fa' else "Password changed successfully"
            )
            self.current_password_entry.delete(0, "end")
            self.new_password_entry.delete(0, "end")
            self.confirm_password_entry.delete(0, "end")
        except Exception as e:
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                f"خطا در تغییر رمز عبور: {e}" if CURRENT_LANG == 'fa' else f"Error changing password: {e}"
            )