import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from controllers.auth_controller import AuthController
from controllers.payment_controller import PaymentController
from controllers.customer_controller import CustomerController
from views.login_view import LoginView
from views.admin_setup_view import AdminSetupView
from views.settings_view import SettingsView
from views.invoices_view import InvoicesView
from views.customers_view import CustomersView
from views.dashboard_view import DashboardView
from views.reports_view import ReportsView
from utils.database import Database
from config import LANG, CURRENT_LANG, THEME
from tkinter import messagebox

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(1.2)

class GoldManagementApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(LANG[CURRENT_LANG]['welcome'])
        self.geometry("1440x900")
        self.configure(fg_color=THEME['background'])
        
        self.db = Database()
        self.auth_controller = AuthController(self.db)
        self.payment_controller = PaymentController(self.db)
        self.customer_controller = CustomerController(self.db)
        self.setup_ui()

    def setup_ui(self):
        user_count = self.db.fetchone("SELECT COUNT(*) FROM users")[0]
        if user_count == 0:
            self.admin_setup_view = AdminSetupView(self, self.handle_admin_setup)
            self.admin_setup_view.pack(fill="both", expand=True)
        else:
            self.login_view = LoginView(self, self.handle_login)
            self.login_view.pack(fill="both", expand=True)

    def handle_admin_setup(self, username, password):
        self.auth_controller.register(username, password, "admin")
        self.admin_setup_view.pack_forget()
        self.login_view = LoginView(self, self.handle_login)
        self.login_view.pack(fill="both", expand=True)

    def handle_login(self, username, password):
        user = self.auth_controller.login(username, password)
        if user:
            self.current_user = user
            self.login_view.pack_forget()
            self.show_main_app()
        else:
            self.login_view.show_error(LANG[CURRENT_LANG]['login_failed'])

    def show_main_app(self):
        # Main Container
        self.main_container = ctk.CTkFrame(self, fg_color=THEME['background'])
        self.main_container.pack(fill="both", expand=True)

        # Sidebar with Animation
        self.sidebar = ctk.CTkFrame(self.main_container, width=250, fg_color="#2A3435", corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.configure(width=0)
        self.animate_sidebar()

        # Sidebar Header
        ctk.CTkLabel(
            self.sidebar,
            text="✨ طلایار ✨" if CURRENT_LANG == 'fa' else "✨ GoldManager ✨",
            font=THEME['font_bold'],
            text_color=THEME['accent']
        ).pack(pady=(20, 10))

        # Sidebar Buttons
        buttons = [
            ("🏠 " + LANG[CURRENT_LANG]['dashboard'], "DashboardView"),
            ("👥 " + LANG[CURRENT_LANG]['customers'], "CustomersView"),
            ("📜 " + LANG[CURRENT_LANG]['invoices'], "InvoicesView"),
            ("📊 " + LANG[CURRENT_LANG]['reports'], "ReportsView"),
            ("⚙️ " + LANG[CURRENT_LANG]['settings'], "SettingsView"),
        ]
        for text, frame_name in buttons:
            button = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=lambda name=frame_name: self.show_frame(name),
                font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
                fg_color="transparent",
                text_color=THEME['text_light'],
                hover_color=THEME['button_hover'],
                anchor="w" if CURRENT_LANG == "en" else "e",
                height=40
            )
            button.pack(fill="x", padx=10, pady=5)

        # Logout Button
        logout_button = ctk.CTkButton(
            self.sidebar,
            text="🚪 " + LANG[CURRENT_LANG]['logout'],
            command=self.logout,
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            fg_color=THEME['button_fg'],
            hover_color=THEME['button_hover'],
            height=40
        )
        logout_button.pack(side="bottom", fill="x", padx=10, pady=20)

        # Main Content Area
        content_container = ctk.CTkFrame(self.main_container, fg_color=THEME['background'])
        content_container.pack(side="left", fill="both", expand=True)

        # Header
        header = ctk.CTkFrame(content_container, fg_color="#2A3435", height=60, corner_radius=0)
        header.pack(fill="x")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header,
            text=LANG[CURRENT_LANG]['welcome'],
            font=THEME['font_bold'],
            text_color=THEME['text_light']
        ).grid(row=0, column=0, padx=20, pady=10, sticky="w" if CURRENT_LANG == "en" else "e")

        ctk.CTkLabel(
            header,
            text=f"👤 {self.current_user['username']}",
            font=THEME['font_fa'] if CURRENT_LANG == 'fa' else THEME['font_en'],
            text_color=THEME['accent']
        ).grid(row=0, column=1, padx=20, pady=10, sticky="e" if CURRENT_LANG == "en" else "w")

        # Frames
        self.frames_container = ctk.CTkFrame(content_container, fg_color=THEME['background'])
        self.frames_container.pack(fill="both", expand=True, padx=20, pady=20)
        self.frames_container.grid_rowconfigure(0, weight=1)
        self.frames_container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (DashboardView, CustomersView, InvoicesView, ReportsView, SettingsView):
            page_name = F.__name__
            frame = F(parent=self.frames_container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("DashboardView")

    def animate_sidebar(self):
        width = 0
        target_width = 250
        while width < target_width:
            width += 10
            self.sidebar.configure(width=width)
            self.update()
            self.after(20)

    def show_frame(self, page_name):
        try:
            frame = self.frames[page_name]
            frame.tkraise()
            if page_name == "DashboardView":
                stats = self.get_dashboard_stats()
                frame.update_dashboard(stats)
            elif page_name == "ReportsView":
                frame.update_reports()  # فراخوانی تابع به‌روزرسانی گزارش‌ها
            elif page_name == "SettingsView":
                frame.update_settings()  # فراخوانی تابع به‌روزرسانی تنظیمات
        except Exception as e:
            print(f"Error showing frame {page_name}: {e}")
            messagebox.showerror(
                "خطا" if CURRENT_LANG == 'fa' else "Error",
                f"خطا در نمایش صفحه: {e}" if CURRENT_LANG == 'fa' else f"Error showing page: {e}"
            )

    def get_dashboard_stats(self):
        query = """
            SELECT (SELECT SUM(amount) FROM payments),
                   (SELECT SUM(amount + interest_amount) FROM installments WHERE paid = 0),
                   (SELECT AVG(interest) FROM invoices)
        """
        stats = self.db.fetchone(query)
        return [
            f"{stats[0] or 0:,.2f} تومان",
            f"{stats[1] or 0:,.2f} تومان",
            f"{stats[2] or 0:.2f} %"
        ]

    def logout(self):
        if messagebox.askyesno(
            "خروج" if CURRENT_LANG == 'fa' else "Logout",
            "آیا مطمئن هستید که می‌خواهید خارج شوید؟" if CURRENT_LANG == 'fa' else "Are you sure you want to logout?"
        ):
            self.main_container.pack_forget()
            self.setup_ui()

if __name__ == "__main__":
    app = GoldManagementApp()
    app.mainloop()