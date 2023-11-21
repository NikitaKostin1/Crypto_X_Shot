from typing import Union, Final
from dataclasses import dataclass
from datetime import datetime
from loguru import logger

from aiogram.types.chat import ChatType



@dataclass
class User:
	"""
	Represents a user with necessary data.
	"""
	user_id: int
	username: str = "None"
	entry_date: datetime = None
	is_bot_on: bool = False
	is_subscription_active: bool = False
	subscription_id: Union[int, None] = None
	subscription_begin_date: Union[datetime, None] = None
	is_test_active: bool = False
	test_begin_date: Union[datetime, None] = None
	language: str = "ru"
	chat_type: Final = ChatType.PRIVATE

	@classmethod
	@logger.catch
	def create_from_chat_type(cls, chat_type: str, **kwargs) -> Union["User", "Group", "Supergroup", "Channel"]:
		"""
		Factory method to create instances of the appropriate subclass based on chat_type.

		Args:
			chat_type (str): Type of chat ('private', 'group', 'supergroup', 'channel').
			**kwargs: Additional keyword arguments.

		Returns:
			User: Instance of the appropriate subclass.
		"""
		if chat_type == "private":
			return cls(**kwargs)
		elif chat_type == "group":
			return Group(**kwargs)
		elif chat_type == "supergroup":
			return Supergroup(**kwargs)
		elif chat_type == "channel":
			return Channel(**kwargs)
		else:
			raise ValueError(f"Unsupported chat_type: {chat_type}")



@dataclass
class Chat(User):
	"""
	Base class for grouping related subclasses (Group, Supergroup, Channel) for logical purposes.
	"""
	pass


@dataclass
class Group(Chat):
	"""
	Represents a group chat.
	"""
	def __post_init__(self):
		self.chat_type = ChatType.GROUP  # "group"


@dataclass
class Supergroup(Chat):
	"""
	Represents a supergroup chat.
	"""
	def __post_init__(self):
		self.chat_type = ChatType.SUPERGROUP  # "supergroup"


@dataclass
class Channel(Chat):
	"""
	Represents a channel chat.
	"""
	def __post_init__(self):
		self.chat_type = ChatType.CHANNEL  # "channel"
