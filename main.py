from aiogram import executor
import asyncio
import atexit

from create_bot import dp
from config import logger

from handlers.user import main as users_registrator
from handlers.admin import main as admins_registrator
from timers import main as timers_registrator
from signals import main as signals_server_starter



# Register command handlers
users_registrator.register_commands_handlers(dp)
admins_registrator.register_commands_handlers(dp)

# Start all timers
timers_registrator.register_timers()

# Start signals server thread
signals_server_starter.start_server()


async def on_startup(_):
	""" Executes immediately after the bot startup """
	logger.success("The bot is online!")


def on_shutdown():
	from handlers.admin.client import clear_signals
	loop = asyncio.new_event_loop()
	loop.run_until_complete(clear_signals())


if __name__ == "__main__":
	atexit.register(on_shutdown)

	# try:
	executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
	# finally:
	# 	pass
