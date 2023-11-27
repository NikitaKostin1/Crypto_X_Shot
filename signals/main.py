from config import logger
import threading
import asyncio

from . import thread



@logger.catch
def start_server():
	"""	
	Starts the signals server in a separate thread
	"""
	def asynchronous_start(wait_for, bot_loop):
		loop = asyncio.new_event_loop()

		asyncio.set_event_loop(loop)
		asyncio.run_coroutine_threadsafe(
			thread.server(wait_for), bot_loop
		)


	bot_loop = asyncio.get_event_loop()
	signals_thread = threading.Thread(
		target=asynchronous_start, args=(90, bot_loop)
	)
	signals_thread.daemon = True
	signals_thread.start()
