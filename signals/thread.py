from create_bot import bot
from config import logger
import asyncio
import time

from handlers.user import manager as user_manager
from . import manager

from typing import List, Tuple, Dict
from entities.parsing.types import (
	ParserResponse, Advertisement
)
from entities import (
	User, Parametres, Signal
)


# Dict with the tuple of signals sent to a user
signals: Dict[int, Tuple[Signal]] = {}


@logger.catch
async def server(wait_for: int):
	"""
	Server function that runs periodically to process signals for active users

	Args:
		wait_for (int): The time interval to wait between server pings
	"""
	# List of user IDs that have been notified about inefficient parameters
	notified_users: List[int] = list()
	min_acceptable_signals_amount = 5

	await manager.set_fiats_symbols()

	while True:
		logger.success("Server ping")
		await asyncio.sleep(wait_for)

		try:
			active_users: List[User] = await user_manager.get_active_users()
			logger.info(f"Active users amount: {len(active_users)}")

			# Check if notified users turned off the bot
			for user_id in notified_users:
				if not user_id in [user.user_id for user in active_users]:
					notified_users.remove(user_id)


			for user in active_users:
				user_id = user.user_id

				parametres: Parametres = await user_manager.get_user_parametres(user_id)

				if not parametres:
					logger.error(f"No parametres: {user_id}")
					continue

				sent_signals_per_cycle = tuple()
				former_signals = signals.get(user_id, tuple())

				for currency in parametres.currencies.value:
					parsers_responses = await manager.gather_parsers_responses(
						currency, parametres
					)

					sent_signals_per_cycle: Tuple[Signal] = await manager.iterate_advertisments(
						user_id, parametres, parsers_responses, former_signals, list(sent_signals_per_cycle)
					)

				await manager.delete_expired_signals(
					user_id, len(sent_signals_per_cycle), former_signals
				)


				# Notification about inefficient parametres
				if len(sent_signals_per_cycle) < min_acceptable_signals_amount and \
									not user_id in notified_users and \
									not await user_manager.is_chat(user_id):
					await manager.notificate_user(user_id)
					notified_users.append(user_id)

				if sent_signals_per_cycle:
					signals[user_id] = sent_signals_per_cycle

				logger.info(f"{user_id} | {user.username} Sent signals: {len(sent_signals_per_cycle)}")

		except Exception as e:
			logger.error(f"Signals thread crashed: {e}")
			continue
