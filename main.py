from aiogram import executor
from config import logger
from create_bot import dp

from handlers import (
	user, admin,
)
import timers
import signals

import sys
import asyncio
import signal



IS_WINDOWS = sys.platform == 'win32'

# Register command handlers for users and admins
user.register_commands_handlers(dp)
admin.register_commands_handlers(dp)

# Start all timers
timers.register_timers()

# Start signals server thread
signals.start_server()

async def on_startup(_):
	""" Executes immediately after the bot startup """
	logger.success("The bot is online!")


async def on_shutdown():
	"""
	Handles the bot shutdown process
	"""
	from handlers.admin.client import clear_signals
	loop = asyncio.get_event_loop()

	# Create the task and wait for it to complete
	task = loop.create_task(clear_signals())
	await asyncio.gather(task)

	# Stop the event loop
	loop.stop()

	logger.success("The bot is offline!")


if __name__ == "__main__":
	"""
	# Set up signal handlers for graceful shutdown
	signal.signal(signal.SIGTERM, on_shutdown)
	signal.signal(signal.SIGINT, on_shutdown)

	# Start the bot polling with provided configurations
	executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
	"""
	# Assuming this is part of your main code
	if IS_WINDOWS:
		try:
			# Start the bot polling with provided configurations
			executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
		finally:
			# loop = asyncio.get_event_loop()
			# asyncio.set_event_loop(loop)
			asyncio.run(on_shutdown())

	else:
		loop = asyncio.new_event_loop()
		loop.add_signal_handler(signal.SIGINT, on_shutdown)
	# loop.add_signal_handler(signal.SIGTERM, lambda s, f: loop.create_task(on_shutdown(s, f)))

		loop.run_forever()
		logger.info(1)
		executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
