from config import logger, get_conn

from datetime import datetime, timedelta
from typing import Union, Tuple

from entities import (
	User, Subscriptions,
	Parametres, Parameter
)
from database import user as db



@logger.catch
async def is_user_exists(user_id: int) -> bool:
	"""
	Check if the user exists in the users table.
	"""
	try:
		connection = await get_conn()
		exists = await db.is_user_exists(connection, user_id)

		return exists
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def get_user(user_id: int) -> User:
	"""
	Retrieve the User object from the users table based on the user ID.
	Returns:
		The User object if found, None otherwise.
	"""
	try:
		connection = await get_conn()
		user: User = await db.get_user(connection, user_id)

		return user
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return None


@logger.catch
async def get_users() -> Tuple[User]:
	"""
	Retrieve the tuple of User objects from the users table.
	Returns:
		Tuple[User]
	"""
	try:
		connection = await get_conn()
		users: Tuple[User] = await db.get_users(connection)

		return users
	except Exception as e:
		logger.error(f"{e}")
		return None


@logger.catch
async def set_new_user(user: User) -> bool:
	"""
	Insert the user's data into the database.
	"""
	if not user.username or not user.entry_date:
		logger.error(""" \
			'username' or 'entry_date' parametres are not provided for the User instance!
		""")
		return False

	try:
		user.entry_date = datetime.now()
		connection = await get_conn()
		registered = await db.set_new_user(connection, user)

		return registered
	except Exception as e:
		logger.error(f"{user}: {e}")
		return False


@logger.catch
async def get_user_parametres(user_id: int) -> Parametres:
	"""
	Retrieve the Parametres object from the users_parametres table based on the user ID.
	Returns:
		The Parametres object if found, None otherwise.
	"""
	try:
		connection = await get_conn()
		parametres: Parametres = await db.get_user_parametres(connection, user_id)

		return parametres
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return None


@logger.catch
async def get_parameter(user_id: int, ParameterType: Parameter) -> Parameter:
	"""
	Retrieve the Parameter object from the users_parametres table 
	based on the user ID and Parameter type
	Returns:
		The Parameter object if found, None otherwise.
	"""
	try:
		connection = await get_conn()
		param = await db.get_parameter(connection, user_id, ParameterType)

		return param
	except Exception as e:
		logger.error(f"{user_id}, {ParameterType}: {e}")
		return None


@logger.catch
async def update_user_parametres(user_id: int, params: Parametres) -> bool:
	"""
	Update the user's parameters in the database.
	Args:
		user_id: The ID of the user.
		params: The Parametres object containing the updated parameters.
	"""
	try:
		connection = await get_conn()
		updated = await db.update_user_parametres(connection, user_id, params)

		return updated
	except Exception as e:
		logger.error(f"{user}: {e}")
		return False


@logger.catch
async def update_user_parameter(user_id: int, param: Parameter) -> bool:
	"""
	Update a specific parameter of the user in the database.
	Args:
		user_id: The ID of the user.
		param: The Parameter object representing the parameter to update.
	Returns:
		True if the update is successful, False otherwise.
	"""
	try:
		connection = await get_conn()

		if param.value is None:
			data = "NULL"
		elif isinstance(param.value, list):
			data = "'{}'".format(" ".join(param.value))
		elif isinstance(param.value, str):
			data = f"\'{param.value}\'"
		else:
			data = param.value

		updated = await db.update_user_parameter(connection, user_id, param.title, data)

		return updated
	except Exception as e:
		logger.error(f"{user}: {e}")
		return False


@logger.catch
async def is_subscription_active(user_id: int) -> bool:
	"""
	Check if the user's subscription is active.
	"""
	try:
		user = await get_user(user_id)

		return user.is_subscription_active
	except Exception as e:
		logger.error(f"{user}: {e}")
		return False


@logger.catch
async def subscription_expiration_date(user_id: int) -> Union[datetime, str, None]:
	"""
	Return datetime obj when subscruption expires.
	In Unlimited subscription case return `∞` symbol
	Otherwise return None
	"""
	try:
		user = await get_user(user_id)
		if not user:
			return None

		subscription_id = user.subscription_id
		if not subscription_id:
			return None

		subscription = Subscriptions.by_id(subscription_id)
		if subscription is Subscriptions.unlimited:
			return "∞"

		subscription_term = subscription.term
		subscription_begin_date = user.subscription_begin_date

		expiration_date: datetime = subscription_begin_date + subscription_term

		return expiration_date
	except Exception as e:
		logger.error(f"{user}: {e}")
		return None


@logger.catch
async def is_subscription_expired(user_id: int) -> bool:
	current_time = datetime.now()
	try:
		user = await get_user(user_id)
		if not user: return False

		subscription_id = user.subscription_id
		if not subscription_id: return False

		if not user.subscription_begin_date: return False

		subscription = Subscriptions.by_id(subscription_id)
		if subscription is Subscriptions.unlimited: return False

		return current_time > user.subscription_begin_date + subscription.term
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def is_tester(user_id: int) -> bool:
	"""
 	Check if the user is a tester.
 	"""
	try:
		user = await get_user(user_id)

		return user.is_test_active
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def is_tester_expired(user_id: int) -> bool:
	"""
	Check if the user's tester status has expired.
	"""
	current_time = datetime.now()
	try:
		user = await get_user(user_id)

		if user.test_begin_date is None:
			return False

		return current_time > user.test_begin_date + Subscriptions.tester.term
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def is_bot_on(user_id: int) -> bool:
	"""
	Checks if the bot is enabled for a user.
	Returns True if the bot is enabled, False otherwise.
	"""
	try:
		connection = await get_conn()
		is_bot_on = await db.is_bot_on(connection, user_id)

		return is_bot_on
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def enable_bot(user_id: int) -> bool:
	"""
	Enables the bot for a user.
	Returns True if the bot is successfully enabled, False otherwise.
	"""
	try:
		connection = await get_conn()
		enabled = await db.enable_bot(connection, user_id)

		return enabled
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def disable_bot(user_id: int) -> bool:
	"""
	Disables the bot for a user.
	Returns True if the bot is successfully disabled, False otherwise.
	"""
	try:
		connection = await get_conn()
		disabled = await db.disable_bot(connection, user_id)

		return disabled
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def switch_bot_state(user_id: int) -> bool:
	"""
	Switches the state of the bot for a user.
	Returns True if the bot state is successfully switched, False otherwise.
	"""
	try:
		_is_bot_on = await is_bot_on(user_id)

		if _is_bot_on:
			switched = await disable_bot(user_id)
		else:
			switched = await enable_bot(user_id)

		return switched
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def get_active_users() -> Tuple[User]:
	"""
	Retrieves a tuple of users where the bot is enabled.
	Returns:
		Tuple[User]: A tuple of User objects representing the active users.
	"""
	try:
		connection = await get_conn()
		active_users = await db.get_active_users(connection)

		return active_users
	except Exception as e:
		logger.error(e)
		return tuple()