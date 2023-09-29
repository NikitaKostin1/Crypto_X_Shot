import asyncpg
import os
from loguru import logger



TOKEN = os.getenv("TOKEN") # bot token

logger.add(
	"debug.log",		# logs writes into debug.log file
	format="{level} {message}",
	level="WARNING",	# warning logs and its parents writes only
	rotation="1 MB",	# if file exceed 1MB size new file creates
	compression="zip"	# old logs files has .zip compression
)

@logger.catch
async def get_conn() -> asyncpg.connection.Connection:
	"""
	Establish a connection to the database.

	Returns:
		asyncpg.connection.Connection: A connection object to interact with the database.
	"""
	DATABASE_URL = os.getenv("DATABASE_URL")
	connection = await asyncpg.connect(dsn=DATABASE_URL, ssl="require")

	return connection
