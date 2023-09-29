from aiogram.utils.exceptions import BotBlocked
from aiogram import types
from datetime import datetime

from create_bot import bot, dp
from config import logger

from ..user import manager as user_manager
from . import manager

from entities import (
	MainMessage, AdditionalMessage,
	User, Subscriptions,
	StandardParametres
)
from assets import texts as txt
from keyboards.user import (
	reply as rkb
)



@logger.catch
async def give_access(message: types.Message):
	"""
	Function to give access to a subscription for a user.
	"""
	try:
		if len(message["text"].split()) == 2:
			# Access requested for caller
			user_id = message["from"]["id"]
			subscription_id = int(message["text"].split()[1])
		else:
			# Access requested for another user
			user_id = int(message["text"].split()[1])
			subscription_id = int(message["text"].split()[2])
	except:
		# TODO: error message
		await message.answer("Неверная команда.")
		return

	user = await user_manager.get_user(user_id)

	if not user:
		# TODO: error message
		await message.answer("Этот пользователь ещё не зашёл в бота. Возможно, неверно указан id")
		return

	subscription = Subscriptions.by_id(subscription_id)

	if not subscription:
		# TODO: error message
		await message.answer("""
			Неверно указан id подписки. Варианты: 
			0 - Тестер
			1 - 1 месяц
			2 - 3 месяца
			3 - 12 месяцев
			4 - бессрочно
		""")
		return

	if subscription is Subscriptions.tester:
		new_user = User(
			user_id=user_id,
			username=user.username,
			entry_date=user.entry_date,
			is_bot_on=False,
			is_subscription_active=True,
			subscription_id=subscription_id,
			subscription_begin_date=datetime.now(),
			is_test_active=True,
			test_begin_date=datetime.now()
		)
		markup = rkb.tester
		text = txt.tester_activated

		user_parametres_updated = await user_manager.update_user_parametres(
			user_id, StandardParametres()
		)
		if not user_parametres_updated:
			# TODO: error message
			await message.answer("Ошибка!")
			return
	else:
		new_user = User(
			user_id=user_id,
			username=user.username,
			entry_date=user.entry_date,
			is_bot_on=False,
			is_subscription_active=True,
			subscription_id=subscription_id,
			subscription_begin_date=datetime.now(),
			is_test_active=False,
			test_begin_date=user.test_begin_date
		)
		markup = rkb.active_subscription
		text = txt.payment_success


	user_updated = await manager.update_user(new_user)

	if not user_updated:
		# TODO: error message
		await message.answer("Ошибка!")
		return

		
	try:	
		await message.answer(
			txt.access_given.format(
				username=user.username,
				user_id=user_id,
				title=subscription.title
			)
		)
		await bot.send_message(
			381906725, 
			txt.access_given.format(
				username=user.username,
				user_id=user_id,
				title=subscription.title
			)
		)
	except BotBlocked:
		pass

	try:
		await bot.send_message(user_id, text, reply_markup=markup)
	except BotBlocked:
		pass


@logger.catch
async def reset_access(message: types.Message):
	"""
	Function to reset the access for a user.
	"""
	try:
		if len(message["text"].split()) == 1:
			# Access reset requested for caller
			user_id = message["from"]["id"]
		else:
			# Access reset requested for another user
			user_id = int(message["text"].split()[1])
	except:
		# TODO: error message
		await message.answer("Неверная команда.")
		return

	user = await user_manager.get_user(user_id)

	if not user:
		# TODO: error message
		await message.answer("Этот пользователь ещё не зашёл в бота. Возможно, неверно указан id")
		return

	is_subscription_active = await user_manager.is_subscription_active(user_id)
	is_tester_expired = await user_manager.is_tester_expired(user_id)

	if not is_subscription_active and not is_tester_expired:
		# TODO: error message
		await message.answer("""
			У пользователя нет подписки или истёкшего тест-драйва
		""")
		return

	zeroed = await manager.reset_access(user_id)

	if not zeroed:
		# TODO: error message
		await message.answer("Ошибка!")
		return


	await message.answer(
		txt.access_zeroed.format(
			username=user.username,
			user_id=user_id
		)
	)
	await bot.send_message(
		381906725, 
		txt.access_zeroed.format(
			username=user.username,
			user_id=user_id
		)
	)
	await bot.send_message(
		user_id,
		txt.access_zeroed_,
		reply_markup=rkb.new_user
	)


@logger.catch
async def mailing(message: types.Message):
	try:
		users_type = int(message["text"].split()[1])
		mailing_text = "\n".join(message["text"].split("\n")[1:])
	except:
		# TODO: error message
		await message.answer("Неверная команда")
		return

	if users_type not in (1, 2, 3):
		# TODO: error message
		await message.answer("""
			Неверно указан тип людей. 
			1 - тестеры и окончавшие тест,
			2 - с активной подпиской,
			3 - все
		""")
		return

	all_users = await user_manager.get_users()
	mailing_users = list()

	for user in all_users:
		match users_type:
			case 1:
				if user.is_test_active or \
					await user_manager.is_tester_expired(user.user_id):
					mailing_users.append(user)

			case 2:
				logger.info(2)
				if user.is_subscription_active:
					logger.info(user)
					mailing_users.append(user)

			case 3:
				mailing_users.append(user)

	await message.answer(
		f"Идёт рыссылка со следующим текстом: \n{mailing_text}"
	)

	sent = 0
	for user in mailing_users:
		try:
			await bot.send_message(user.user_id, mailing_text)
			sent += 1
		except:
			continue

	await message.answer(
		f"Отправлено {sent} людям, {len(mailing_users) - sent} заблокировали бота."
	)


@logger.catch
async def clear_signals(message: types.Message):
	"""
	Deletes all signal messages at every user
	and cleans signals storage
	"""
	from signals.thread import signals as storage

	for user_id in storage:
		signals = storage[user_id]
		deleted_amount = 0

		for signal in signals:
			try:
				await bot.delete_message(
					chat_id=user_id, 
					message_id=signal.message_id
				)
				deleted_amount += 1
			except:
				pass

		logger.success(f"{user_id}: Deleted {deleted_amount}/{len(signals)}")
		storage[user_id] = tuple()


