from dataclasses import dataclass, field
from typing import Union, List, Tuple
from config import logger

from .input_error import InputError

import asyncio



@dataclass
class Parameter:
	"""
	Base class for individual parameters
	"""
	value: Union[int, str, List[str]]
	title: str

	def __post_init__(self):
		self.value = self._validate_value(self.value)


	@logger.catch
	def _validate_value(self, value):
		"""
		Validates the assigned value for the parameter.
		Note:
			This method applies specific validation rules based on the parameter type.

		Validation Rules:
			- For 'Banks', 'Markets', and 'Currencies' parameters, the value is expected to be a string.
				If the value is a string, it is split into a list and returned.

			- For the 'Spread' parameter, the value is expected to be a float.
				If the value is a float, it is rounded to 2 decimal places and returned.
		"""
		if isinstance(self, (Banks, Markets, Currencies)):
			if isinstance(value, str):
				value = value.split()
		elif isinstance(self, Spread):
			value = round(value, 2)

		available_values = getattr(self, "available_values", None)
		if available_values and isinstance(value, list):
			for val in value:
				if val not in available_values:
					error_message = f"Invalid value '{val}' for attribute '{self.title}'"
					raise ValueError(error_message)

		return value



@dataclass
class Limits(Parameter):
	value: Union[int, None]
	title: str = "limits"

@dataclass
class Banks(Parameter):
	value: List[str]
	title: str = "banks"
	available_values: List[str] = field(default_factory=lambda: [
		"QIWI", "Tinkoff", "YandexMoney",
		"Payeer", "AdvCash", "Sberbank",
		"SBP", "Alfa-bank", "RaiffeisenBank",
		"RosBank", "Belarusbank", "Bank_Transfer",
		"Technobank", "MTBank", "Wise", "Skrill",
		"AirTM", "PerfectMoney", "PayPal", 
		"Revolut", "Ziraat", "Garanti",
		"KuveytTurk", "Papara", "DenizBank",
		"QNB", "VakifBank", "ISBank", 
		"Akbank", "Uzcard", "Humo", 
		"UzbekNational", "PayMe", "KapitalBank",
		"PrivatBank", "Monobank", "RaiffeisenBankAval",
		"A-Bank", "Izibank", "Sepa_Transfer", 
		"Sepa_Instant", "Halyk", "HomeCreditKz",
		"Eurasian", "Jysan", "Kaspi", "CenterCredit",
		"Forte"
	])  # TODO: move to databse

@dataclass
class Markets(Parameter):
	value: List[str]
	title: str = "markets"
	available_values: List[str] = field(default_factory=lambda: [
		"Binance", "Huobi", "Bybit", "OKX", "bitpapa",
		"Commex", 'CoinBase', 'Crypto', 'Kuna.io', 'KuCoin',
		'Gate.io', 'WhiteBit', 'Kraken', 'Bitfinex',
		'mexc', 'Cryptology', 'Exmo', 'bitHumb',
		'Liquid', 'Bittrex', 'Poloniex', 'BitMart',
		'Bitrue', 'Bitstamp', 'XT.com', 'OKcoin',
		'Phemex', 'Hotcoin', 'BTCEX', 'bigONE',
		'coinW', 'ascendEX', 'BKEX', 'FMFW'
	])  # TODO: move to databse

@dataclass
class Spread(Parameter):
	value: float
	title: str = "spread"

@dataclass
class BidType(Parameter):
	value: str
	title: str = "bid_type"
	available_values: List[str] = field(default_factory=lambda: [
		"Taker", "Maker"
	])  # TODO: move to databse

@dataclass
class AskType(Parameter):
	value: str
	title: str = "ask_type"
	available_values: List[str] = field(default_factory=lambda: [
		"Maker", "Taker"
	])  # TODO: move to databse

@dataclass
class Currencies(Parameter):
	value: List[str]
	title: str = "currencies"
	available_values: List[str] = field(default_factory=lambda: [
		"USDT", "BTC", "ETH", "BNB",
		"XRP", "USDC", "ADA", "SOL",
		"MATIC", "LTC"
	])  # TODO: move to databse

@dataclass
class Fiat(Parameter):
	_available_symbols = {
		"RUB": "₽", "EUR": "€", "USD": "$", "GBP": "£",
		"UAH": "₴", "BYN": "Br", "KZT": "₸", "TRY": "₺" 
	}

	value: str
	title: str = "fiat"
	available_values: List[str] = field(default_factory=lambda: [
		"RUB", "EUR", "USD", "GBP",
		"UAH", "BYN", "KZT", "TRY"
	])  # TODO: move to databse
	symbol: str = ""

	def __post_init__(self):
		self.symbol = self._available_symbols.get(self.value, "")


@dataclass
class SignalsType(Parameter):
	value: str
	title: str = "signals_type"
	available_values: list = field(default_factory=lambda: [
		"p2p", "spot", "p2p_spot"
	])  # TODO: move to databse



@dataclass(order=True)
class Parametres:
	"""
	Represents a set of parameters for configuration.
	"""
	limits: Limits = field(default_factory=Limits)
	banks: Banks = field(default_factory=Banks)
	markets: Markets = field(default_factory=Markets)
	spread: Spread = field(default_factory=Spread)
	bid_type: BidType = field(default_factory=BidType)
	ask_type: AskType = field(default_factory=AskType)
	currencies: Currencies = field(default_factory=Currencies)
	fiat: Fiat = field(default_factory=Fiat)
	signals_type: SignalsType = field(default_factory=SignalsType)


	def __setattr__(self, name, value):
		"""
		Overrides the default setattr behavior to validate and assign values to parameter fields.
		Args:
			name (str): The name of the attribute.
			value: The value to be assigned.
		"""
		if isinstance(value, Parameter):
			super().__setattr__(name, value)
		else:
			FieldAnnotation: Parameter = self.__annotations__[name]
			super().__setattr__(name, FieldAnnotation(value))



@dataclass(order=True)
class StandardParametres(Parametres):
	"""
	Parameter settings that a user has before manual changes.

	This class represents the standard parameter settings that a user has initially, 
	before making any manual changes.
	It inherits from the base class Parametres.

	Note:
	- The default values for the parameters are provided in the field initializers.
	- The parameters are represented as instances of the Parameter class.
	- The Parameter class allows specifying the title and value of a parameter.
	"""
	limits: Limits = Limits(None)
	banks: Banks = field(default_factory=lambda: Banks([
		"QIWI", "Tinkoff", "YandexMoney",
		"Payeer", "AdvCash", "Sberbank",
		"SBP", "Alfa-bank", "RaiffeisenBank",
		"RosBank"
	]))  # TODO: move to databse
	markets: Markets = field(default_factory=lambda: Markets([
		"Binance", "Huobi", "Bybit", "OKX", "Commex"
	]))  # TODO: move to databse
	spread: Spread = Spread(1.0)
	bid_type: BidType = BidType("Taker")
	ask_type: AskType = AskType("Maker")
	currencies: Currencies = field(default_factory=lambda: Currencies([
		"USDT", "BTC", "ETH"
	]))  # TODO: move to databse
	fiat: Fiat = Fiat("RUB")
	signals_type: SignalsType = SignalsType("p2p")



class TesterParametresChecker:
	"""
	Checker for Tester subscription restrictions.
	"""
	def __init__(self, user_id: int, *args: Union[Parameter, Tuple[Parameter]]):
		self.args = args
		self.user_id = user_id


	@logger.catch
	async def check(self) -> Union[Parameter, InputError]:
		"""
		Check if the parameter values match the Tester subscription restrictions.

		Args:
			*args: Variable number of Parameter objects representing the parameters to be checked.

		Returns:
			If the values match the restrictions, return the last checked parameter.
			Otherwise, return an InputError indicating the corresponding restriction violation.

		Note:
			This method iterates over the provided parameters and checks each one against the subscription restrictions.

		Raises:
			InputError: If any of the parameters violate the subscription restrictions.

		Restrictions:
			- Limits: The value should be 10,000. Otherwise, an InputError is returned.
			- Spread: The value should be greater than or equal to 1.0. Otherwise, an InputError is returned.
			- BidType: The value should be "Taker". Otherwise, an InputError is returned.
			- AskType: The value should be "Maker". Otherwise, an InputError is returned.
		"""
		from handlers import misc
		txt = await misc.get_language_module(self.user_id)

		for param in self.args:
			if isinstance(param, Limits):
				if not isinstance(param.value, None):
					return InputError(txt.tester_limits_restriction)

			if isinstance(param, Markets):
				available_markets = Parametres.get_annotations["markets"]
				if param.value != available_markets:
					return InputError(txt.tester_markets_restriction)

			if isinstance(param, Markets):
				available_currencies = Parametres.get_annotations["currencies"]
				if param.value != available_currencies:
					return InputError(txt.tester_currencies_restriction)

			elif isinstance(param, Spread):
				if param.value > 1.0:
					return InputError(txt.tester_spread_restriction)

			elif isinstance(param, BidType):
				if param.value != "Taker":
					return InputError(txt.tester_bid_ask_restriction)

			elif isinstance(param, AskType):
				if param.value != "Maker":
					return InputError(txt.tester_bid_ask_restriction)

		return param
