from aiogram import types
from create_bot import Dispatcher
from config import logger

from . import client



@logger.catch
def register_commands_handlers(dp: Dispatcher):
	"""
	Register all admins commands
	"""
	dp.register_message_handler(client.give_access, lambda message: message.text.split()[0] == "Доступ1899", state="*", chat_type=types.ChatType.PRIVATE)
	dp.register_message_handler(client.reset_access, lambda message: message.text.split()[0] == "Обнулить105", state="*", chat_type=types.ChatType.PRIVATE)
	dp.register_message_handler(client.mailing, lambda message: message.text.split()[0] == "Рассылка1100", state="*", chat_type=types.ChatType.PRIVATE)
	dp.register_message_handler(client.clear_signals, lambda message: message.text == "Очистка1944", state="*", chat_type=types.ChatType.PRIVATE)
