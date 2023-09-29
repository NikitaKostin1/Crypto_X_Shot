from aiogram.dispatcher import FSMContext
from aiogram import types
from datetime import datetime

from create_bot import bot
from config import logger

from . import manager
from . import util
from assets import texts as txt
from .parametres import util as params_util

from entities import (
	MainMessage, AdditionalMessage,
	User, Parametres
)
from keyboards.user import (
	reply as rkb,
	inline as ikb
)



@logger.catch
async def start(message: types.Message, state: FSMContext):
	"""
	Handles the '/start' command. Inserts the user into the database if not already present.
	"""
	await state.finish()

	user = User(
		user_id=message["from"]["id"],
		username=str(message["from"]["username"])
	)

	user_exists = await manager.is_user_exists(user.user_id)

	if user_exists:
		await MainMessage.delete(user.user_id)
		await AdditionalMessage.delete(user.user_id)

		reply_markup = await util.determine_reply_markup(user.user_id)

		first_name = message["from"]["first_name"]
		await message.answer(
			txt.existing_user_greeting.format(first_name=first_name), 
			reply_markup=reply_markup
		)
		await bot.send_message(
			381906725, 
			txt.existing_user.format(
				user_id=user.user_id, username=user.username
			)
		)
		await bot.send_message(
			283258793, 
			txt.existing_user.format(
				user_id=user.user_id, username=user.username
			)
		)

	else:
		user.entry_date = datetime.now()
		registered = await manager.set_new_user(user)

		if not registered: 
			logger.error(f"{user.user_id}: {registered=}")
			await message.answer(txt.error)
			return

		await message.answer(
			txt.new_user_greeting, reply_markup=rkb.new_user
		)
		msg = await message.answer(
			txt.faq, reply_markup=ikb.channel_kb, 
			disable_web_page_preview=True
		)
		await MainMessage.acquire(msg)

		await bot.send_message(
			381906725, 
			txt.new_user.format(
				user_id=user.user_id, username=user.username
			)
		)
		await bot.send_message(
			283258793, 
			txt.new_user.format(
				user_id=user.user_id, username=user.username
			)
		)


@logger.catch
async def switch_bot_state(message: types.Message, state: FSMContext):
	"""
	Switches the state of the bot for a user.
	"""
	await state.finish()
	user_id = message["from"]["id"]
	await AdditionalMessage.delete(user_id)

	is_bot_on = await manager.is_bot_on(user_id)
	switched = await manager.switch_bot_state(user_id)

	if not switched:
		await message.answer(txt.error)
		return

	if is_bot_on:
		await message.answer(txt.bot_disabled)
		msg = await message.answer(txt.bot_disabling_info)
	else:
		await message.answer(txt.bot_enabled)
		msg = await message.answer(txt.bot_enabling_info)

	await MainMessage.acquire(msg)



@logger.catch
async def parametres(message: types.Message, state: FSMContext):
	"""
	Handles the 'parametres' reply keyboard button.
	Send trading type option message
	"""
	await state.finish()
	user_id = message["from"]["id"]
	await AdditionalMessage.delete(user_id)

	msg = await message.answer(
		txt.signals_type_option,
		reply_markup=ikb.signals_type_option
	)
	await MainMessage.acquire(msg)


@logger.catch
async def test_drive(message: types.Message, state: FSMContext):
	"""
	Handles the 'Test drive' reply keyboard button.
	"""
	await state.finish()
	user_id = message["from"]["id"]
	await AdditionalMessage.delete(user_id)

	if await manager.is_tester(user_id) or \
				await manager.is_subscription_active(user_id) or \
				await manager.is_tester_expired(user_id):
		return

	msg = await message.answer(
		txt.test_drive, 
		reply_markup=ikb.test_drive,
		disable_web_page_preview=True
	)
	await MainMessage.acquire(msg)


@logger.catch
async def channel(message: types.Message, state: FSMContext):
	"""
	Handles the 'channel' reply keyboard button. Sends the channel link to the user.
	"""
	await state.finish()
	user_id = message["from"]["id"]
	await AdditionalMessage.delete(user_id)

	msg = await util.send_photo(
		user_id,
		photo="AgACAgQAAxkDAAEFaMRjAAE92sIDlXKKItUBN2yiy2e78vIAAii5MRtsnwABUA-Hs0UXPXreAQADAgADeAADKQQ",
		caption=txt.channel_link
	)
	await MainMessage.acquire(msg)
	

@logger.catch
async def support(message: types.Message, state: FSMContext):
	"""
	Handles the 'support' reply keyboard button. Sends the support link to the user.
	"""
	await state.finish()
	user_id = message["from"]["id"]
	await AdditionalMessage.delete(user_id)

	msg = await util.send_photo(
		user_id, 
		photo="AgACAgQAAxkDAAEFaMhjAAE95GLbtIzfRI5N_OHTQDGDGl4AAim5MRtsnwABUGE6F6MLZ-usAQADAgADeAADKQQ",
		caption=txt.support_link
	)
	await MainMessage.acquire(msg)


@logger.catch
async def rates(message: types.Message, state: FSMContext):
	"""
	Handles the 'rates' reply keyboard button. Displays the subscription rates to the user.
	"""
	await state.finish()
	user_id = message["from"]["id"]
	await AdditionalMessage.delete(user_id)

	msg = await message.answer(
		txt.rates,
		reply_markup=ikb.payment_option,
		disable_web_page_preview=True
	)
	await MainMessage.acquire(msg)


@logger.catch
async def profile(message: types.Message, state: FSMContext):
	"""
	Handles the 'rates' reply keyboard button.
	Displays the profile data to the user.
	"""
	await state.finish()
	user_id = message["from"]["id"]

	expiration_date = await manager.subscription_expiration_date(user_id)
	if not expiration_date:
		await message.answer(txt.error)
		return

	if isinstance(expiration_date, datetime): 
		date_string = expiration_date.strftime("%d/%m/%Y")
		days_left = str(
			util.date_to_int(expiration_date) - \
			util.date_to_int(datetime.now())
		)
	else:
		date_string = expiration_date
		days_left = date_string

	msg = await message.answer(
		txt.profile.format(
			expiration_date=date_string,
			days_left=days_left
		),
		disable_web_page_preview=True
	)
	await MainMessage.acquire(msg)