from aiogram import types
from config import logger
import asyncio

from . import subscriptions



loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@logger.catch
def register_timers():
	"""
	Register all timers
	"""
	loop.create_task(subscriptions.tester(wait_for=600))
	loop.create_task(subscriptions.premium_subscriptions(wait_for=3600))
