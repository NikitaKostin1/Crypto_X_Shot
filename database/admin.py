from asyncpg.connection import Connection
from typing import List, Union

from config import logger

from entities import (
	User, Supergroup, Group, Channel
)



@logger.catch
async def get_admins(connection: Connection) -> list:
	"""
	Retrieves a list of admin IDs from the database.
	"""
	admins = []
	try:
		records = await connection.fetch(f"""
			SELECT admin_id FROM admins;
		""")
		if not records:
			return []

		for record in records:
			admins.append(record.get("user_id"))

		return admins
	except Exception as e:
		logger.error(e)
		return []


@logger.catch
async def add_admin_chat(connection: Connection, admin_id: int, chat_id: int) -> bool:
	"""
	Adds an admin to a chat in the database.

	Returns:
		bool: True if the admin was added successfully, False otherwise.
	"""
	try:
		await connection.execute(f"""
			BEGIN TRANSACTION ISOLATION LEVEL repeatable read;

			INSERT INTO chats VALUES(
				{chat_id}, {admin_id}
			);

			COMMIT;
		""")

		return True
	except Exception as e:
		logger.error(e)
		return False


@logger.catch
async def get_admin_chats(connection: Connection, admin_id: int) -> List[Union[Supergroup, Group, Channel]]:
	"""
	Fetches chats (Supergroups, Channels, and Groups) for a specific admin.
	"""
	chats = list()
	try:
		# Fetch all chats (Supergroups, Channels, and Groups) for the specified admin
		records = await connection.fetch(f"""
			SELECT users.*
			FROM users
			JOIN chats ON users.user_id = chats.chat_id
			WHERE 
				chats.admin_id = {admin_id} AND
				users.chat_type IN ('supergroup', 'channel', 'group');
		""")

		# Iterate through the fetched records and create corresponding instances
		for record in records:
			chat_type = record.get("chat_type")

			if chat_type == "supergroup":
				chat_instance = Supergroup
			elif chat_type == "channel":
				chat_instance = Channel
			elif chat_type == "group":
				chat_instance = Group
			else:
				logger.warning(f"Unsupported chat_type: {chat_type}")
				continue

			chat = chat_instance(
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
			chats.append(chat)

		return chats
	except Exception as e:
		logger.error(e)
		return []


@logger.catch
async def update_user(connection: Connection, user: User) -> bool:
	"""
	Updates a user's row in the user table.
	"""
	try:
		await connection.execute(f"""
			BEGIN TRANSACTION ISOLATION LEVEL repeatable read;

			UPDATE users 
			SET 
				user_id = {user.user_id},
				username = '{user.username}',
				entry_date = '{user.entry_date}',
				is_subscription_active = {user.is_subscription_active},
				subscription_id = {
					f'{user.subscription_id}' 
					if user.subscription_id or user.subscription_id == 0
					else 'NULL'
				},
				subscription_begin_date = {
					f"'{user.subscription_begin_date}'"
					if user.subscription_begin_date 
					else 'NULL'
				},
				is_test_active = {user.is_test_active},
				test_begin_date = {
					f"'{user.test_begin_date}'"
					if user.test_begin_date 
					else 'NULL'
				},
				language = '{user.language}'
			WHERE user_id = {user.user_id};

			COMMIT;
		""")

		return True
	except Exception as e:
		logger.error(f"{user.user_id}: {e}")
		return False


@logger.catch
async def reset_access(connection: Connection, user_id: int) -> bool:
	"""
	Updates a user's row in the user table.
	"""
	try:
		await connection.execute(f"""
			BEGIN TRANSACTION ISOLATION LEVEL repeatable read;

			UPDATE users 
			SET 
				is_subscription_active = false,
				subscription_id = NULL,
				subscription_begin_date = NULL,
				is_test_active = False,
				test_begin_date = NULL
			WHERE user_id = {user_id};

			COMMIT;
		""")

		return True
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def set_tester_as_expired(connection: Connection, user_id: int) -> bool:
	"""
	Sets the tester subscription as expired for a user in the database.
	"""
	try:
		await connection.execute(f"""
			BEGIN TRANSACTION ISOLATION LEVEL repeatable read;
			UPDATE users
			SET 
				is_bot_on = false,
				is_subscription_active = false,
				subscription_id = NULL,
				is_test_active = false
			WHERE user_id = {user_id};
			COMMIT;
		""")

		return True
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def set_subscription_as_expired(connection: Connection, user_id: int) -> bool:
	"""
	Sets the subscription as expired for a user in the database
	"""
	try:
		await connection.execute(f"""
			BEGIN TRANSACTION ISOLATION LEVEL repeatable read;
			UPDATE users
			SET 
				is_bot_on = false,
				is_subscription_active = false
			WHERE user_id = {user_id};
			COMMIT;
		""")

		return True
	except Exception as e:
		logger.error(f"{user_id}: {e}")
		return False


@logger.catch
async def get_tester_users(connection: Connection) -> List[User]:
	"""
	Retrieves a list of users with active tester subscriptions from the database.
	"""
	users = list()
	try:
		records = await connection.fetch("""
			SELECT * FROM users WHERE is_test_active = true;
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
				language=record.get("language"),
			)
			users.append(user)

		return users
	except Exception as e:
		logger.error(e)
		return list()


@logger.catch
async def get_users_with_non_tester_subscription(connection: Connection) -> List[User]:
	"""
	Retrieve a list of users with non-tester subscription from the database
	"""
	users = list()
	try:
		records = await connection.fetch("""
			SELECT * FROM users 
			WHERE 
				is_test_active = false AND
				is_subscription_active = true;
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
				language=record.get("language"),
			)
			users.append(user)

		return users
	except Exception as e:
		logger.error(e)
		return list()
