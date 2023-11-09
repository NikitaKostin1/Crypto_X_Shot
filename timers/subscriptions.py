from aiogram.utils.exceptions import BotBlocked
from datetime import timedelta
from typing import List
import asyncio

from config import logger
from create_bot import bot
from handlers import misc
from handlers.admin import (
	manager as admin_manager
)
from handlers.user import (
	manager as user_manager
)
from entities import (
	Subscriptions, User
)



@logger.catch
async def tester(wait_for: int):
	"""
	Check all users with active Tester subscription.
	If a user's Tester term has expired according to the Tester.term timedelta,
	it sets the user as expired and sends a notification message.
	"""
	while True:
		users: List[User] = await admin_manager.get_tester_users()

		for user in users:
			is_expired = await user_manager.is_tester_expired(user.user_id)

			if is_expired:
				access_closed = await admin_manager.set_tester_as_expired(user.user_id)

				if not access_closed:
					# TODO: Error message
					await bot.send_message(
						381906725, f"ТЕСТЕР НЕ ОТКЛЮЧИЛСЯ <code>{user.user_id}</code>"
					)

				try:
					txt = await misc.get_language_module(user_id)
					await bot.send_message(
						user.user_id, txt.tester_expired, 
						reply_markup=rkb.subscription_expired
					)
				except BotBlocked:
					pass

		await asyncio.sleep(wait_for)



@logger.catch
async def premium_subscriptions(wait_for: int):
	"""
	Check all users with active Non-Tester subscription.
	If a user's Subscription term has expired according to the Subscription.term timedelta,
	it sets the user as expired and sends a notification message.
	"""
	while True:
		users: List[User] = await admin_manager.get_users_with_non_tester_subscription()
		logger.info(f"Subscription timer ping. Users amount: {len(users)}")

		for user in users:
			is_expired = await user_manager.is_subscription_expired(user.user_id)

			if is_expired:
				txt = await misc.get_language_module(user_id)
				access_closed = await admin_manager.set_subscription_as_expired(user.user_id)

				if not access_closed:
					# TODO: Error message
					await bot.send_message(
						381906725, f"ПОДПИСКА НЕ ОТКЛЮЧИЛАСЬ <code>{user.user_id}</code>"
					)

				subscription = Subscriptions.by_id(user.subscription_id)
				text = txt.subscription_expired.format(
					user_id=user.user_id,
					username=user.username,
					subscription_title=subscription.title
				)
				try:	
					await bot.send_message(
						user.user_id, txt.subscription_expired_, 
						reply_markup=rkb.subscription_expired
					)
					await bot.send_message(
						381906725, text,
						reply_markup=rkb.subscription_expired
					)
				except BotBlocked:
					pass

		await asyncio.sleep(wait_for)

