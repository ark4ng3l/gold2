from tkcalendar import Calendar
import jdatetime
from datetime import datetime
from tkinter import Toplevel, Button, messagebox

class JalaliCalendar:
    def __init__(self, parent, callback):
        self.parent = parent  # ذخیره parent برای استفاده بعدی
        self.callback = callback
        self.top = Toplevel(parent)
        self.top.title("تقویم شمسی" if parent.lang == 'fa' else "Jalali Calendar")
        self.top.geometry("300x300")

        # امروز به تاریخ شمسی
        today = jdatetime.date.today()
        self.cal = Calendar(
            self.top,
            selectmode="day",
            year=today.year,
            month=today.month,
            day=today.day,
            date_pattern="y-mm-dd",
            locale='fa_IR' if parent.lang == 'fa' else 'en_US'
        )
        self.cal.pack(pady=10)

        # دکمه تأیید
        Button(
            self.top,
            text="تأیید" if parent.lang == 'fa' else "Confirm",
            command=self.on_date_select
        ).pack(pady=5)

    def on_date_select(self):
        jalali_date = self.cal.get_date()  # تاریخ به‌صورت YYYY-MM-DD
        # تبدیل تاریخ شمسی به میلادی
        try:
            year, month, day = map(int, jalali_date.split('-'))
            g_date = jdatetime.date(year, month, day).togregorian()
            gregorian_date = g_date.strftime("%Y-%m-%d")
            # فرمت شمسی به صورت روز/ماه/سال
            jalali_formatted = f"{day:02d}/{month:02d}/{year}"
            self.callback(gregorian_date, jalali_formatted)
            self.top.destroy()
        except Exception as e:
            messagebox.showerror(
                "خطا" if self.parent.lang == 'fa' else "Error",
                str(e)
            )