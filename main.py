from aiogram import executor

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


# Start the bot using long-polling
if __name__ == "__main__":
	executor.start_polling(dp, skip_updates=True, on_startup=on_startup)

