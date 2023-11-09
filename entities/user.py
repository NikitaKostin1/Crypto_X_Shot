from typing import Union
from dataclasses import dataclass
from datetime import datetime



@dataclass
class User:
	"""
	Represents a user with necessary data.

	Attributes:
		user_id: The unique identifier of the user.
		username: The username of the user.
		entry_date: The entry date of the user.
		is_bot_on: Indicates whether the user's bot is active.

		is_subscription_active: Indicates whether the user has an active subscription.
		subscription_id: The ID of the user's subscription.
		subscription_begin_date: The start date of the user's subscription.

		is_test_active: Indicates whether the user has an active test.
		test_begin_date: The start date of the user's test.
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
