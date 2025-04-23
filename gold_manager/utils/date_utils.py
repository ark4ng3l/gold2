from datetime import datetime
import jdatetime
import re  # خط بالای فایل


        # ... بقیه کد
def jalali_to_gregorian(jalali_date):
    # افزودن اعتبارسنجی
    if not re.match(r'^\d{2}/\d{2}/\d{4}$', jalali_date):
        raise ValueError("قالب تاریخ باید DD/MM/YYYY باشد (مثال: 25/09/1403)")
    
    try:
        day, month, year = map(int, jalali_date.split('/'))
        g_date = jdatetime.date(year, month, day).togregorian()
        return g_date.strftime("%Y-%m-%d")
    except Exception as e:
        raise Exception(f"خطا در تبدیل تاریخ شمسی: {e}")

def gregorian_to_jalali(gregorian_date):
    """تبدیل تاریخ میلادی به شمسی (به فرمت DD/MM/YYYY)"""
    try:
        g_date = datetime.strptime(gregorian_date, "%Y-%m-%d %H:%M:%S")
        j_date = jdatetime.date.fromgregorian(date=g_date)
        return j_date.strftime("%d/%m/%Y %H:%M:%S")
    except Exception as e:
        raise Exception(f"خطا در تبدیل تاریخ میلادی به شمسی: {e}")