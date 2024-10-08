from aiogram.types import (
	InlineKeyboardMarkup, ReplyKeyboardMarkup,
	Message
)
from aiogram.utils.exceptions import BotBlocked
from aiogram.types.input_file import InputFile
from aiogram import types
from datetime import datetime, timedelta

from typing import Union

from config import logger
from handlers import misc
from create_bot import bot
from ..admin import manager as admin_manager
from . import manager

from entities import (
	MainMessage, 
	User, Subscriptions,
	StandardParametres
)



@logger.catch
def date_to_int(date: datetime) -> int:
	"""
	Convert a datetime object to an integer representation.

	Args:
		date (datetime): The datetime object to convert.

	Returns:
		int: The integer representation of the date.
	"""
	year, month, day = date.year, date.month, date.day
	return ((year-1)*365 + (year-1)//4 - (year-1)//100 + (year-1)//400
			+ [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334][month - 1]
			+ day
			+ int(((year%4==0 and year%100!=0) or year%400==0) and month > 2))


@logger.catch
async def send_video( \
	user_id: int|str, video: str|InputFile, \
	caption: str=None, markup: InlineKeyboardMarkup=None) -> Message:
	"""
	Use this method to send video files, Telegram clients support mp4 videos 
	(other formats may be sent as Document).
	"""
	try:
		msg = await bot.send_video(
			user_id, video=video, caption=caption, reply_markup=markup
		)
		return msg
	except Exception as e:
		# TODO: check exception
		if caption:
			try:
				msg = await bot.send_message(
					user_id, caption, reply_markup=markup,
					disable_web_page_preview=True
				)
			except BotBlocked:
				return
			return msg


@logger.catch
async def send_photo( \
	user_id: int|str, photo: str|InputFile, \
	caption: str=None, markup: InlineKeyboardMarkup=None) -> Message:
	"""
	Use this method to send photo files
	"""
	try:
		msg = await bot.send_photo(
			user_id, photo=photo, caption=caption, reply_markup=markup
		)
		return msg
	except Exception as e:
		# TODO: check exception
		if caption:
			try:
				msg = await bot.send_message(
					user_id, caption, reply_markup=markup,
					disable_web_page_preview=True
				)
			except BotBlocked:
				return
			return msg


@logger.catch
async def determine_reply_markup(user_id: int) -> Union[ReplyKeyboardMarkup, None]:
	"""
	Determines the appropriate reply keyboard markup based on the user's status.
	"""
	kb = await misc.get_keyboard_module(user_id)

	if await manager.is_chat(user_id):
		return None

	if await manager.is_tester(user_id):
		return kb.reply.tester

	if await manager.is_subscription_active(user_id):
		if await manager.is_subscription_expired(user_id):
			return kb.reply.subscription_expired
		return kb.reply.active_subscription

	if await manager.is_tester_expired(user_id):
		return kb.reply.subscription_expired
	if await manager.is_subscription_expired(user_id):
			return kb.reply.subscription_expired

	return kb.reply.new_user



@logger.catch
async def activate_test_drive(callback: types.CallbackQuery):
	"""
	Activate the test drive subscription for a user.

	Args:
		callback (types.CallbackQuery): The callback query triggering the activation.
	"""
	user_id = callback["message"]["chat"]["id"]
	await callback.answer()
	await MainMessage.delete(user_id)

	txt = await misc.get_language_module(user_id)
	kb = await misc.get_keyboard_module(user_id)

	user = await manager.get_user(user_id)

	if not user:
		# TODO: error message
		await callback.message.answer(txt.error)
		return

	new_user = User(
		user_id=user_id,
		username=user.username,
		entry_date=user.entry_date,
		is_bot_on=False,
		is_subscription_active=True,
		subscription_id=Subscriptions.tester.subscription_id,
		subscription_begin_date=datetime.now(),
		is_test_active=True,
		test_begin_date=datetime.now(),
		language=user.language
	)
	markup = kb.reply.tester
	text = txt.tester_activated

	user_updated = await admin_manager.update_user(new_user)

	if not user_updated:
		await callback.message.answer(txt.error)
		return

	user_parametres_updated = await manager.update_user_parametres(
		user_id, StandardParametres()
	)

	if not user_parametres_updated:
		await callback.message.answer(txt.error)
		return

	msg = await callback.message.answer(
		text, reply_markup=markup
	)
	await MainMessage.acquire(msg)


@logger.catch
async def set_language(callback: types.CallbackQuery):
	"""
	Set the language preference for a user in response to a callback query.

	Args:
		callback (types.CallbackQuery): The callback query received.

	This function extracts the user's language preference from the callback query and
	sets it for the user. It then sends a confirmation message to the user.
	"""
	user_id = callback["message"]["chat"]["id"]

	if not await misc.access_check(callback):
		return

	language: str = callback["data"].split()[1]
	await callback.message.delete()

	language_is_set = await manager.set_language(user_id, language)

	markup = await determine_reply_markup(user_id)
	txt = await misc.get_language_module(user_id)

	await callback.message.answer(
		txt.language_is_set.format(
			language=language
		),
		reply_markup=markup
	)

