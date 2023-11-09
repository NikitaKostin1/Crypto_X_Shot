from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



new_user = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
b1 = KeyboardButton("🎈 TEST DRIVE 🎈")
b2 = KeyboardButton("🎯 Activate SHOT 🎯")
b3 = KeyboardButton("🫡 SUPPORT 🫡")
new_user.add(b1).add(b2).add(b3)

active_subscription = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
b1 = KeyboardButton("⚙️ Settings")
b2 = KeyboardButton("🔔 On/Off")
b3 = KeyboardButton("🫡 SUPPORT 🫡")
active_subscription.row(b1, b2).add(b3)

tester = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
b1 = KeyboardButton("⚙️ Settings")
b2 = KeyboardButton("🔔 On/Off")
b3 = KeyboardButton("🎯 Activate SHOT 🎯")
b4 = KeyboardButton("🫡 SUPPORT 🫡")
tester.row(b1, b2).add(b3).add(b4)

subscription_expired = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False)
b1 = KeyboardButton("🎯 Activate SHOT 🎯")
b2 = KeyboardButton("🫡 SUPPORT 🫡")
subscription_expired.add(b1).add(b2)

tester_expired = subscription_expired