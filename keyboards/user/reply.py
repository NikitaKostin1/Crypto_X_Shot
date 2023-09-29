from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



new_user = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
b1 = KeyboardButton("🕊 Тест-драйв")
b2 = KeyboardButton("🟢 АКТИВИРОВАТЬ PREMIUM 🟢")
b3 = KeyboardButton("🖊 Канал")
b4 = KeyboardButton("👨‍💻 Поддержка")
new_user.add(b1).add(b2).row(b3, b4)

active_subscription = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
b1 = KeyboardButton("⚙️ Настройки")
b2 = KeyboardButton("👤 Профиль")
b3 = KeyboardButton("🔔 Вкл/Выкл")
active_subscription.row(b1, b2).add(b3)

tester = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
b1 = KeyboardButton("⚙️ Настройки")
b2 = KeyboardButton("🔔 Вкл/Выкл")
b3 = KeyboardButton("🟢 АКТИВИРОВАТЬ PREMIUM 🟢")
b4 = KeyboardButton("🖊 Канал")
b5 = KeyboardButton("👨‍💻 Поддержка")
tester.row(b1, b2).add(b3).row(b4, b5)

subscription_expired = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
b1 = KeyboardButton("🟢 АКТИВИРОВАТЬ PREMIUM 🟢")
b2 = KeyboardButton("🖊 Канал")
b3 = KeyboardButton("👨‍💻 Поддержка")
subscription_expired.add(b1).row(b2, b3)
