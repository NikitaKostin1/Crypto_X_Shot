from dataclasses import dataclass



@dataclass
class AdvСonditions:
	"""Data class representing the conditions of an advertisement"""
	fiat: str
	currency: str
	price: float
	bank: str
	limits_min: int
	limits_max: int


	def __post_init__(self):
		self.fiat = str(self.fiat)
		self.currency = str(self.currency)
		self.price = float(self.price)
		self.bank = str(self.bank)
		self.limits_min = int(self.limits_min)
		self.limits_max = int(self.limits_max)



@dataclass
class Advertiser:
	"""Data class representing an advertiser"""
	advertiser_id: str



@dataclass
class Advertisement:
	"""Data class representing an advertisement"""
	market: str
	conditions: AdvСonditions
	advertiser: Advertiser



@dataclass
class ParserResponse:
	"""Data class representing the response from the parser"""
	best_bid: 	Advertisement = None
	best_ask: 	Advertisement = None
	second_bid: Advertisement = None
	second_ask: Advertisement = None
