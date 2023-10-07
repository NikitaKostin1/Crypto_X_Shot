from create_bot import Dispatcher
from aiogram import types
from config import logger

from entities.states import (
	Limits, Spread
)

from . import (
	client, parametres, util
)



@logger.catch
def register_commands_handlers(dp: Dispatcher):
	"""
	Register all user commands and handlers
	"""
	# COMMANDS
	dp.register_message_handler(client.start, commands=["start"], state="*", chat_type=types.ChatType.PRIVATE)

	# REPLY KEYBOARD
	# dp.register_message_handler(client.channel, lambda message: message.text == "🖊 Канал", state="*", chat_type=types.ChatType.PRIVATE)
	dp.register_message_handler(client.support, lambda message: message.text == "🫡 SUPPORT 🫡", state="*", chat_type=types.ChatType.PRIVATE)
	dp.register_message_handler(client.rates, lambda message: message.text == "🎯 АКТИВИРОВАТЬ SHOT 🎯", state="*", chat_type=types.ChatType.PRIVATE)
	# dp.register_message_handler(client.profile, lambda message: message.text == "👤 Профиль", state="*", chat_type=types.ChatType.PRIVATE)

	dp.register_message_handler(client.switch_bot_state, lambda message: message.text == "🔔 Вкл/Выкл", state="*", chat_type=types.ChatType.PRIVATE)
	dp.register_message_handler(client.parametres, lambda message: message.text == "⚙️ Настройки", state="*", chat_type=types.ChatType.PRIVATE)
	dp.register_message_handler(client.test_drive, lambda message: message.text == "🎈 TEST DRIVE 🎈", state="*", chat_type=types.ChatType.PRIVATE)

	# CALLBACKS
	dp.register_callback_query_handler(util.activate_test_drive, lambda query: query.data == "test_drive", chat_type=types.ChatType.PRIVATE)

	# PARAMETRES
	dp.register_callback_query_handler(parametres.util.back_to_parametres, lambda query: query.data == "back_to_parametres", state="*", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.client.menu, lambda query: query.data == "parametres_menu", state="*", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.client.limits, lambda query: query.data == "parametres limits", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.client.banks, lambda query: query.data == "parametres banks", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.client.currencies, lambda query: query.data == "parametres currencies", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.client.markets, lambda query: query.data == "parametres markets", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.client.spread, lambda query: query.data == "parametres spread", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.client.trading_type, lambda query: query.data == "parametres trading_type", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.client.fiat, lambda query: query.data == "parametres fiat", chat_type=types.ChatType.PRIVATE)

	# CALLBACK PARAMETRES
	dp.register_callback_query_handler(parametres.callbacks.handlers.banks, lambda query: query.data.split()[0] == "set_bank", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.callbacks.handlers.currencies, lambda query: query.data.split()[0] == "set_currency", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.callbacks.handlers.markets, lambda query: query.data.split()[0] == "set_market", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.callbacks.handlers.trading_type, lambda query: query.data.split()[0] == "set_trading_type", chat_type=types.ChatType.PRIVATE)
	dp.register_callback_query_handler(parametres.callbacks.handlers.fiat, lambda query: query.data.split()[0] == "set_fiat", chat_type=types.ChatType.PRIVATE)

	# STATE PARAMETRES
	dp.register_message_handler(parametres.states.handlers.limits, state=Limits.limits)
	dp.register_message_handler(parametres.states.handlers.spread, state=Spread.spread)