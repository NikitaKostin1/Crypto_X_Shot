from aiogram import executor
from threading import Event
import asyncio
import sys
import signal

from create_bot import dp
from config import logger

from handlers.user import main as users_registrator
from handlers.admin import main as admins_registrator
from timers import main as timers_registrator
import signals



IS_WINDOWS = sys.platform == 'win32'

# Register command handlers
users_registrator.register_commands_handlers(dp)
admins_registrator.register_commands_handlers(dp)

# Start all timers
timers_registrator.register_timers()

# Start signals server thread
signals.start_server()


async def on_startup(_):
	""" Executes immediately after the bot startup """
	logger.success("The bot is online!")
	done_event.wait()


def on_shutdown(signum, frame):
	from handlers.admin.client import clear_signals
	loop = asyncio.get_event_loop()
	loop.create_task(clear_signals())

	if IS_WINDOWS:
		loop.stop()
	else:
		done_event.set()

	logger.success("The bot is offline!")


if __name__ == "__main__":
	signal.signal(signal.SIGTERM, on_shutdown)
	signal.signal(signal.SIGINT, on_shutdown)

	if IS_WINDOWS:
		loop = asyncio.new_event_loop()

		executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
	else:
		done_event = Event()

		executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
