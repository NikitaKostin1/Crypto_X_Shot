from datetime import datetime, timedelta
from dataclasses import dataclass, astuple
from typing import Union
from config import logger



@dataclass(frozen=True, order=True)
class Subscription:
	"""
	Represents a subscription with its properties.

	Attributes:
		subscription_id: The unique identifier of the subscription.
		term: The duration of the subscription (timedelta) or None if it's not applicable.
		title: The title of the subscription.
		description: The description of the subscription.
		price: The price of the subscription.
		is_full_access: Indicates whether the subscription provides full access.
		is_multiple_activations: Indicates whether multiple activations are allowed for the subscription.
	"""
	subscription_id: int
	term: Union[timedelta, None]

	title: str
	description: str
	price: float

	is_full_access: bool
	is_multiple_activations: bool



@dataclass(frozen=True, order=True)
class Tester(Subscription):
	"""
	Represents a tester subscription with restrictions and limited activation.
	"""
	subscription_id: int = 0
	term: Union[timedelta, None] = timedelta(hours=1)

	title: str = "Тестер"
	description: str = ""  # TODO: write and import description
	price: float = 0.00

	is_full_access: bool = False
	is_multiple_activations: bool = False



@dataclass(frozen=True, order=True)
class OneMonth(Subscription):
	"""
	Represents a one-month subscription with full access and multiple activations.
	Inherits from the base `Subscription` class.
	"""
	subscription_id: int = 1
	term: Union[timedelta, None] = timedelta(days=30)

	title: str = "1 месяц"
	description: str = ""  # TODO: write and import description
	price: float = 2499.00

	is_full_access: bool = True
	is_multiple_activations: bool = True



@dataclass(frozen=True, order=True)
class ThreeMonths(Subscription):
	"""
	Represents a three-months subscription with full access and multiple activations.
	Inherits from the base `Subscription` class.
	"""
	subscription_id: int = 2
	term: Union[timedelta, None] = timedelta(days=90)

	title: str = "3 месяца"
	description: str = ""  # TODO: write and import description
	price: float = 4999.00
	
	is_full_access: bool = True
	is_multiple_activations: bool = True


@dataclass(frozen=True, order=True)
class TwelveMonths(Subscription):
	"""
	Represents an twelve-months subscription with full access and multiple activations.
	Inherits from the base `Subscription` class.
	"""
	subscription_id: int = 3
	term: Union[timedelta, None] = timedelta(days=365)

	title: str = "12 месяцев"
	description: str = ""  # TODO: write and import description
	price: float = 9999.00
	
	is_full_access: bool = True
	is_multiple_activations: bool = True



@dataclass(frozen=True, order=True)
class Unlimited(Subscription):
	"""
	Represents an unlimited subscription with full access and one activation.
	Inherits from the base `Subscription` class.
	"""
	subscription_id: int = 4
	term: Union[timedelta, None] = None

	title: str = "Бессрочно"
	description: str = ""  # TODO: write and import description
	price: float = 19999.00
	
	is_full_access: bool = True
	is_multiple_activations: bool = False



@dataclass(frozen=True, order=True)
class Subscriptions:
	"""
	Contains available subscriptions.
	This class represents a collection of available subscriptions. It provides access to different subscription types.

	Attributes:
		tester: The tester subscription.
		one_month: The one-month subscription.
		three_months: The three-months subscription.
		unlimited: The unlimited subscription.

	Methods:
		by_id: Retrieves a subscription by its ID.

	Note:
		- The `Subscriptions` class is a convenience container for accessing different subscription types.
	"""
	tester: Subscription = Tester
	one_month: Subscription = OneMonth
	three_months: Subscription = ThreeMonths
	twelve_months: Subscription = TwelveMonths
	unlimited: Subscription = Unlimited


	@logger.catch
	def by_id(self, subscription_id: int) -> Subscription:
		"""
		Retrieves a subscription by its ID.

		Args:
			subscription_id: The ID of the subscription to retrieve.
		Returns:
			The corresponding subscription if found, or None if no matching subscription is found.
		"""
		for subscription in astuple(self):
			if int(subscription_id) == subscription.subscription_id:
				return subscription



Subscriptions = Subscriptions()
