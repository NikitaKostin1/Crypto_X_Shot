from config import logger
import threading
import asyncio

from . import thread



@logger.catch
def start_server():
	"""
	Starts the signals server in a separate thread
	"""
	def asynchronous_start(wait_for, loop):
		asyncio.set_event_loop(loop)
		loop.create_task(thread.server(wait_for))

	loop = asyncio.get_event_loop()
	server_thread = threading.Thread(
		target=asynchronous_start, args=(90, loop)
	)
	server_thread.daemon = True
	server_thread.start()

