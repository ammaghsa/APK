import requests
import pandas as pd
from datetime import datetime
import os

EXCEL_FILE = "data.xlsx"
ROCKET_CHAT_URL = "https://chat.apk-group.net"
USER_ID = "NruyHBvv2XrEE3Fdw"
AUTH_TOKEN = "nuMCA5va05srZ4YlbWEPyLEMKIfCpjjzJRA8zMHLQei"

HEADERS = {
    "X-Auth-Token": AUTH_TOKEN,
    "X-User-Id": USER_ID,
    "Content-Type": "application/json"
}

APPROVAL_LINK = "https://erp.apk-group.net/odoo/apk-new-approval?default_category_id=139"

persian_months = {
    1: "فروردین", 2: "اردیبهشت", 3: "خرداد", 4: "تیر",
    5: "مرداد", 6: "شهریور", 7: "مهر", 8: "آبان",
    9: "آذر", 10: "دی", 11: "بهمن", 12: "اسفند"
}

def to_persian_number(value):
    english_digits = "0123456789"
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    return str(value).translate(str.maketrans(english_digits, persian_digits))

# Get month from user
while True:
    try:
        month_num = int(input("Which month? (Enter number 1-12): "))
        if 1 <= month_num <= 12:
            current_month = persian_months[month_num]
            deadline = f"۳ {current_month}"
            break
        else:
            print("❌ Please enter a number between 1 and 12.")
    except ValueError:
        print("❌ Please enter only numbers.")

log_buffer = []

def write_log(text):
    print(text)
    log_buffer.append(text)

LOG_FOLDER = "log"
os.makedirs(LOG_FOLDER, exist_ok=True)

now = datetime.now()
log_filename = now.strftime("log_%Y-%m-%d_%H-%M-%S.txt")
log_full_path = os.path.join(LOG_FOLDER, log_filename)

df = pd.read_excel(EXCEL_FILE)

write_log("===== START SENDING =====")
write_log(f"Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
write_log(f"Month: {current_month}")
write_log(f"Total records: {len(df)}")
write_log("")

for idx, row in df.iterrows():
    try:
        username_raw = row.get('username')
        if pd.isna(username_raw) or str(username_raw).strip() == "":
            continue

        username = str(username_raw).strip()
        if not username.startswith("@"):
            username = "@" + username

        fullname = str(row.get('fullname', '')).strip()
        noe_hamkari_raw = str(row.get('نوع همکاری', '')).strip()
        noe_hamkari = " ".join(noe_hamkari_raw.split())

        hozor = row.get('حضور موثر', 0)
        kasr = row.get('کسرکار', 0)

        if "تمام وقت" in noe_hamkari:
            message = f"""**گزارش کارکرد {current_month}**

**نام همکار:** {fullname}
**نوع همکاری:** تمام وقت
**حضور موثر:** {to_persian_number(hozor)} ساعت
**کسر حضور:** {to_persian_number(kasr)} ساعت
**مهلت اصلاح کارکرد:** {deadline}
**روش اصلاح تردد:** تا ۳ مورد در سامانه‌ی کسرا، بیش از ۳ مورد، فقط با ثبت تیکت [اصلاح کارکرد]({APPROVAL_LINK})

در صورت نیاز، با رابط منابع انسانی یا مدیر مستقیم خود گفت‌و‌گو کنید.
ارسال پاسخ شما در این چت بررسی نمی‌شود.
"""

        elif "ساعتی" in noe_hamkari:
            message = f"""**گزارش کارکرد {current_month}**

**نام همکار:** {fullname}
**نوع همکاری:** ساعتی
**کارکرد ثبت‌شده:** {to_persian_number(hozor)} ساعت
**مهلت اصلاح کارکرد:** {deadline}
**روش اصلاح تردد:** تا ۳ مورد در سامانه‌ی کسرا، بیش از ۳ مورد، فقط با ثبت تیکت [اصلاح کارکرد]({APPROVAL_LINK})

در صورت نیاز، با رابط منابع انسانی یا مدیر مستقیم خود گفت‌و‌گو کنید.
ارسال پاسخ شما در این چت بررسی نمی‌شود.
"""

        elif "مسئولیتی" in noe_hamkari:
            message = f"""**گزارش کارکرد {current_month}**

**نام همکار:** {fullname}
**نوع همکاری:** مسئولیتی
کارکرد شما توافقی است و حضور و غیاب شما بررسی نمی‌شود.

در صورت نیاز، با رابط منابع انسانی یا مدیر مستقیم خود گفت‌و‌گو کنید.
ارسال پاسخ شما در این چت بررسی نمی‌شود.
"""

        else:
            continue

        body = {
            "channel": username,
            "text": message
        }

        response = requests.post(
            f"{ROCKET_CHAT_URL}/api/v1/chat.postMessage",
            json=body,
            headers=HEADERS,
            timeout=30
        )

        if response.status_code == 200:
            write_log(f"✅ {username} | {fullname} | {noe_hamkari}")
        else:
            write_log(f"❌ {username} | Status: {response.status_code}")

    except Exception:
        pass

write_log("")
write_log("===== FINISHED =====")

with open(log_full_path, "w", encoding="utf-8") as f:
    f.write("\n".join(log_buffer))

print(f"\nDone! Log saved: {log_full_path}")