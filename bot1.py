import telebot
from telebot import types
import os, json

# 🔑 توکن ربات
TOKEN = "توکن_ربات_خودت"
bot = telebot.TeleBot(TOKEN)

# 📂 چک کردن فایل users.json
if not os.path.exists("users.json"):
    with open("users.json", "w") as f:
        json.dump({}, f)

# 📌 تابع کمکی برای خواندن/نوشتن دیتا
def load_users():
    with open("users.json", "r") as f:
        return json.load(f)

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4, ensure_ascii=False)

# 📂 متغیر صف و چت‌های فعال
queue = []
active_chats = {}

# 📌 دستور /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    users = load_users()
    user_id = str(message.chat.id)

    # اگه اولین باره وارد شده
    if user_id not in users:
        users[user_id] = {
            "name": None,
            "city": None,
            "gender": None,
            "coins": 5  # هدیه شروع 🎁
        }
        save_users(users)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📖 راهنما")
    btn2 = types.KeyboardButton("ℹ️ پروفایل من")
    btn3 = types.KeyboardButton("💰 خرید سکه")
    btn4 = types.KeyboardButton("👥 شروع چت ناشناس")
    btn5 = types.KeyboardButton("⛔ پایان چت")
    markup.add(btn1, btn2, btn3, btn4, btn5)

    text = (
        "سلام 👋\n"
        "به ربات ناشناس چت خوش اومدی 😎\n"
        "از منو پایین یکی رو انتخاب کن."
    )
    bot.reply_to(message, text, reply_markup=markup)

# 📌 راهنما
@bot.message_handler(func=lambda m: m.text == "📖 راهنما")
def send_help(message):
    bot.reply_to(message,
        "📌 امکانات ربات:\n"
        "ℹ️ پروفایل من → ساخت/ویرایش پروفایل\n"
        "💰 خرید سکه → افزایش سکه برای چت\n"
        "👥 شروع چت ناشناس → ورود به گفتگوی ناشناس\n"
        "⛔ پایان چت → خروج از گفتگو\n"
        "هر کاربر در شروع ۵ سکه هدیه داره 🎁"
    )

# 📌 پروفایل
@bot.message_handler(func=lambda m: m.text == "ℹ️ پروفایل من")
def show_profile(message):
    users = load_users()
    user_id = str(message.chat.id)
    user = users.get(user_id, {})

    reply = (
        f"👤 نام: {user.get('name')}\n"
        f"🏙 شهر: {user.get('city')}\n"
        f"⚧ جنسیت: {user.get('gender')}\n"
        f"💰 سکه‌ها: {user.get('coins')}"
    )
    bot.reply_to(message, reply)

# 📌 خرید سکه
@bot.message_handler(func=lambda m: m.text == "💰 خرید سکه")
def buy_coins(message):
    bot.reply_to(message,
        "💳 درگاه پرداخت فعلا فعال نیست.\n"
        "برای تست، فقط به ادمین پیام بده تا سکه‌هات افزایش پیدا کنه."
    )

# 📌 شروع چت ناشناس
@bot.message_handler(func=lambda m: m.text == "👥 شروع چت ناشناس")
def start_chat(message):
    users = load_users()
    user_id = str(message.chat.id)

    if users[user_id]["coins"] <= 0:
        bot.reply_to(message, "❌ سکه‌هات تموم شده. باید سکه بخری!")
        return

    # اگه کاربر در حال چت باشه
    if user_id in active_chats:
        bot.reply_to(message, "⚠️ شما هم‌اکنون در حال چت هستید.")
        return

    if len(queue) > 0:
        partner_id = queue.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id

        # کم کردن یک سکه
        users[user_id]["coins"] -= 1
        users[partner_id]["coins"] -= 1
        save_users(users)

        bot.send_message(user_id, "✅ شما به یک نفر وصل شدید. خوش و بش کنید 😎")
        bot.send_message(partner_id, "✅ شما به یک نفر وصل شدید. خوش و بش کنید 😎")
    else:
        queue.append(user_id)
        bot.reply_to(message, "⌛ منتظر بمون تا یکی بهت وصل بشه...")

# 📌 پایان چت
@bot.message_handler(func=lambda m: m.text == "⛔ پایان چت")
def end_chat(message):
    user_id = str(message.chat.id)

    if user_id in active_chats:
        partner_id = active_chats[user_id]
        del active_chats[user_id]
        del active_chats[partner_id]

        bot.send_message(user_id, "❌ چت پایان یافت.")
        bot.send_message(partner_id, "❌ طرف مقابل چت را پایان داد.")
    elif user_id in queue:
        queue.remove(user_id)
        bot.send_message(user_id, "❌ از صف انتظار خارج شدید.")
    else:
        bot.send_message(user_id, "⚠️ شما در چتی نیستید.")

# 📌 مسیج رد و بدل در چت ناشناس
@bot.message_handler(func=lambda m: True)
def relay_messages(message):
    user_id = str(message.chat.id)

    if user_id in active_chats:
        partner_id = active_chats[user_id]
        bot.send_message(partner_id, message.text)
    else:
        bot.reply_to(message, "برای شروع چت ناشناس از منو گزینه 👥 شروع چت ناشناس رو بزن.")

print("✅ ربات روشن شد و آماده پاسخگویی است.")
bot.infinity_polling()