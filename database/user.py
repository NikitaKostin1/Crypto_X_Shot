from asyncpg.connection import Connection
from datetime import datetime, timedelta
from typing import Union, Tuple
from config import logger

from entities import (
	User, StandardParametres,
	Parametres, Parameter
)



@logger.catch
async def is_user_exists(connection: Connection, user_id: int) -> bool:
	"""
	Checks if a user exists in the database by user_id
	"""
	record = await connection.fetchrow(
		f"SELECT user_id FROM users WHERE user_id = {user_id};"
	)
	return bool(record)


@logger.catch
async def get_user(connection: Connection, user_id: int) -> User|None:
	"""
	Returns a User object from the users table.
	Returns None in case of an error.
	"""
	try:
		record = await connection.fetchrow(f"""
			SELECT * FROM users WHERE user_id = {user_id};
		""")
		if not record: return None

		user = User(
			user_id=record.get("user_id"),
			username=record.get("username"),
			entry_date=record.get("entry_date"),
			is_bot_on=record.get("is_bot_on"),
			is_subscription_active=record.get("is_subscription_active"),
			subscription_id=record.get("subscription_id"),
			subscription_begin_date=record.get("subscription_begin_date"),
			is_test_active=record.get("is_test_active"),
			test_begin_date=record.get("test_begin_date"),
			language=record.get("language"),
		)

		return user
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return None


@logger.catch
async def get_users(connection: Connection) -> Tuple[User]|None:
	"""
	Retrieve the tuple of User objects from the users table.
	Returns:
		Tuple[User]
	"""
	try:
		users = list()
		records = await connection.fetch(f"""
			SELECT * FROM users;
		""")
		if not records: return tuple()

		for record in records:
			user = User(
				user_id=record.get("user_id"),
				username=record.get("username"),
				entry_date=record.get("entry_date"),
				is_bot_on=record.get("is_bot_on"),
				is_subscription_active=record.get("is_subscription_active"),
				subscription_id=record.get("subscription_id"),
				subscription_begin_date=record.get("subscription_begin_date"),
				is_test_active=record.get("is_test_active"),
				test_begin_date=record.get("test_begin_date"),
				language=record.get("language"),
			)
			users.append(user)

		return tuple(users)
	except Exception as e:
		logger.error(f"{e}")
		return None


@logger.catch
async def get_user_parametres(connection: Connection, user_id: int) -> Parametres|None:
	"""
	Returns a Parametres object from the users_parametres table.
	Returns None in case of an error.
	"""
	try:
		record = await connection.fetchrow(f"""
			SELECT * FROM users_parametres WHERE user_id = {user_id};
		""")
		if not record: return None

		parametres = Parametres(
			limits=record.get("limits"),
			banks=record.get("banks"),
			markets=record.get("markets"),
			spread=record.get("spread"),
			bid_type=record.get("bid_type"),
			ask_type=record.get("ask_type"),
			currencies=record.get("currencies"),
			fiat=record.get("fiat"),
			signals_type=record.get("signals_type")
		)

		return parametres
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return None


@logger.catch
async def get_parameter(connection: Connection, user_id: int, ParameterType: Parameter) -> Parameter|None:
	"""
	Retrieves a specific parameter value for a user from the database.

	Args:
		connection (Connection): The database connection.
		user_id (int): The ID of the user.
		ParameterType (Parameter): The type of parameter to retrieve.

	Returns:
		Parameter: The value of the parameter for the user, or None if it doesn't exist.
	"""
	try:
		value = await connection.fetchval(f"""
			SELECT {ParameterType.title} FROM users_parametres WHERE user_id = {user_id};
		""")
		param = ParameterType(value)

		return param
	except Exception as e:
		logger.error(f"{user_id}, {ParameterType}: {e}")
		return None	



@logger.catch
async def set_new_user(connection: Connection, user: User) -> bool:
	"""
	Inserts a new user into the database.
	"""
	try:
		# username column has VARCHAR(50) type
		if len(user.username) > 50:
			user.username = user.username[:50]

		params = StandardParametres()
		await connection.execute(f"""
			BEGIN TRANSACTION ISOLATION LEVEL repeatable read;
			INSERT INTO users (
				user_id, username, entry_date, is_bot_on, 
				is_subscription_active, is_test_active, language
			) VALUES(
				{user.user_id}, '{user.username}',
				'{user.entry_date}', false, false, 
				false, '{user.language}'
			);
			INSERT INTO users_parametres VALUES(
				{user.user_id}, 
				{"NULL" if not params.limits.value else params.limits.value},
				'{" ".join(params.banks.value)}',
				'{" ".join(params.markets.value)}',
				{params.spread.value},
				'{params.bid_type.value}',
				'{params.ask_type.value}',
				'{" ".join(params.currencies.value)}',
				'{params.fiat.value}',
				'{params.signals_type.value}'
			);
			COMMIT;
		""")
		
		return True
	except Exception as e:
		logger.error(f"{user.user_id}: {e}")
		return False


@logger.catch
async def update_user_parametres(connection: Connection, user_id: int, params: Parametres) -> bool:
	"""
	Updates a user's parameters in the database.
	Returns a boolean value indicating the success of the operation
	"""
	try:
		await connection.execute(f"""
			BEGIN TRANSACTION ISOLATION LEVEL repeatable read;
			UPDATE users_parametres
			SET 
				limits={"NULL" if not params.limits.value else params.limits.value},
				banks='{" ".join(params.banks.value)}',
				markets='{" ".join(params.markets.value)}',
				spread={params.spread.value},
				bid_type='{params.bid_type.value}',
				ask_type='{params.ask_type.value}',
				currencies='{" ".join(params.currencies.value)}',
				fiat='{params.fiat.value}',
				signals_type='{params.signals_type.value}'
			WHERE user_id = {user_id};
			COMMIT;
		""")

		return True
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def update_user_parameter(connection: Connection, user_id: int, column: str, data: Union[str, int]) -> bool:
	"""
	Updates a user's parameter in the database.
	Returns a boolean value indicating the success of the operation
	"""
	try:
		await connection.execute(f"""
			BEGIN TRANSACTION ISOLATION LEVEL repeatable read;
			UPDATE users_parametres
			SET 
				{column} = {data}
			WHERE user_id = {user_id};
			COMMIT;
		""")

		return True
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def is_bot_on(connection: Connection, user_id: int) -> bool:
	"""
	Checks if the bot is enabled for a user.
	Returns True if the bot is enabled for the user, False otherwise.
	"""
	try:
		is_bot_on = await connection.fetchval(f"""
			SELECT is_bot_on
			FROM users
			WHERE user_id = {user_id};
		""")

		return bool(is_bot_on)
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def enable_bot(connection: Connection, user_id: int) -> bool:
	"""
	Enables the bot for a user.
	Returns True if the bot is successfully enabled, False otherwise.
	"""
	try:
		await connection.execute(f"""
			BEGIN TRANSACTION ISOLATION LEVEL repeatable read;
			UPDATE users
			SET 
				is_bot_on = true
			WHERE user_id = {user_id};
			COMMIT;
		""")

		return True
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def disable_bot(connection: Connection, user_id: int) -> bool:
	"""
	Disables the bot for a user.
	Returns True if the bot is successfully disabled, False otherwise.
	"""
	try:
		await connection.execute(f"""
			BEGIN TRANSACTION ISOLATION LEVEL repeatable read;
			UPDATE users
			SET 
				is_bot_on = false
			WHERE user_id = {user_id};
			COMMIT;
		""")

		return True
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def get_active_users(connection: Connection) -> Tuple[User]:
	"""
	Return tuple of Users where is_bot_on = True
	"""
	try:
		active_users = list()
		records = await connection.fetch("""
			SELECT 
				DISTINCT users.*
			FROM 
				users_parametres AS params
				JOIN users AS users 
					ON params.user_id = users.user_id
			WHERE 
				users.is_bot_on = true
			AND 
				params.signals_type IN ('p2p');
		""")

		for record in records:
			user = User(
				user_id=record.get("user_id"),
				username=record.get("username"),
				entry_date=record.get("entry_date"),
				is_bot_on=record.get("is_bot_on"),
				is_subscription_active=record.get("is_subscription_active"),
				subscription_id=record.get("subscription_id"),
				subscription_begin_date=record.get("subscription_begin_date"),
				is_test_active=record.get("is_test_active"),
				test_begin_date=record.get("test_begin_date"),
				language=record.get("language")
			)
			active_users.append(user)


		return tuple(active_users)
	except Exception as e:
		logger.error(e)
		return tuple()


@logger.catch
async def get_language(connection: Connection, user_id: int) -> str|None:
	"""

	"""
	try:
		language = await connection.fetchval(f"""
			SELECT language FROM users
			WHERE user_id = {user_id};
		""")

		return language
	except Exception as e:
		logger.error(e)
		return None



@logger.catch
async def set_language(
	connection: Connection, user_id: int, 
	language: str) -> bool:
	"""

	"""
	try:
		await connection.execute(f"""
			BEGIN TRANSACTION ISOLATION LEVEL repeatable read;
			UPDATE users
			SET 
				language = '{language}'
			WHERE user_id = {user_id};
			COMMIT;
		""")

		return True
	except Exception as e:
		logger.error(e)
		return False