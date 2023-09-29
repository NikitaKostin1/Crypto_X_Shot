from dataclasses import dataclass, field
from fake_useragent import UserAgent
from config import logger

import asyncio
import aiohttp

from .types import *

from typing import (
	NoReturn, Union, Dict
)



@dataclass
class Parser:
	fiat: str
	currency: str
	banks: list
	limits: Union[int, None]
	headers: Dict["Accept", "User-Agent"] = field(default_factory=lambda: {
		"Accept": str(),
		"User-Agent": str()
	})


	def __post_init__(self):
		if self.limits is None:
			self.limits = ""

		self.headers = self.get_headers()


	@logger.catch
	def get_headers(self) -> Dict[str, str]:
		"""
		Generate and return headers with a random User-Agent.

		Returns:
			Dict[str, str]: The generated headers.
		"""
		# creating random User-Agent
		ua = UserAgent()
		user_agent = ua.random

		headers = {
			"Accept": "application/json,*/*",
			"User-Agent": user_agent
		}

		return headers


	@logger.catch
	async def get_p2p(self) -> ParserResponse:
		"""
		Fetch P2P advertisements asynchronously from the specified banks.

		Returns:
			ParserResponse: The response containing the best and second best bid and ask advertisements.
		"""
		self.bid_advertisements = {"best_adv": None, "second_adv": None}
		self.ask_advertisements = {"best_adv": None, "second_adv": None}

		try:
			tasks = list()

			async with aiohttp.ClientSession() as session:
				for bank in self.banks:
					task_bid = asyncio.create_task(self._get_advertisements("bid", bank, session))
					task_ask = asyncio.create_task(self._get_advertisements("ask", bank, session))

					tasks.append(task_bid)
					tasks.append(task_ask)

				await asyncio.gather(*tasks)

			return ParserResponse(
				best_bid=self.bid_advertisements["best_adv"],
				best_ask=self.ask_advertisements["best_adv"],
				second_bid=self.bid_advertisements["second_adv"],
				second_ask=self.ask_advertisements["second_adv"]
			)

		except Exception as e:
			logger.error(e)
			return ParserResponse()


	@logger.catch
	def determine_adv_position(
		self,
		advertisement: Advertisement,
		adv_type: Union["bid", "ask"]
	) -> NoReturn:
		"""
		Determine the position of the advertisement in the given dictionary.

		Args:
			advertisements (Dict[str, Advertisement]): The dictionary of advertisements.
			advertisement (Advertisement): The advertisement to be positioned.
			adv_type (Union[str, str]): The type of advertisement ("bid" or "ask").
		"""
		if adv_type == "bid":
			advertisements = self.bid_advertisements
		else:
			advertisements = self.ask_advertisements
		
		if advertisements["best_adv"]:
			best_adv_price = advertisements["best_adv"].conditions.price
		else:
			best_adv_price = None

		if advertisements["second_adv"]:
			second_adv_price = advertisements["second_adv"].conditions.price
		else:
			second_adv_price = None

		current_adv_price = advertisement.conditions.price

		if best_adv_price:
			if (adv_type == "bid" and current_adv_price < best_adv_price) \
				or (adv_type == "ask" and current_adv_price > best_adv_price):

				advertisements["second_adv"] = advertisements["best_adv"]
				advertisements["best_adv"] = advertisement

			else:
				if second_adv_price:
					if (adv_type == "bid" and current_adv_price < best_adv_price) \
					or (adv_type == "ask" and current_adv_price > best_adv_price):
						advertisements["second_adv"] = advertisement
				else:
					advertisements["second_adv"] = advertisement

		else:
			advertisements["best_adv"] = advertisement


	@logger.catch
	def price_difference_validation(
		self, 
		advertisement_ndx: int,
		adv_type: Union["bid", "ask"],
		curr_price: float, next_price: float,
		adv_amount: int
	) -> bool:
		"""
		Validate the price difference between advertisements.

		Args:
			advertisement_ndx (int): The index of the current advertisement.
			adv_type (Union[str, str]): The type of advertisement ("bid" or "ask").
			curr_price (float): The price of the current advertisement.
			next_price (float): The price of the next advertisement.
			adv_amount (int): The total number of advertisements.

		Returns:
			bool: True if the price difference is appropriate, False otherwise.
		"""
		max_percent_difference = {
			"bid": 10,
			"ask": 7
		}
		""" if it is not the last advertisement and there are more 
			than 7 advertisements in response """
		price_percent_difference = \
		float(round((1 - float(curr_price) / float(next_price)) * 100, 2))

		return not (abs(price_percent_difference) >= max_percent_difference[adv_type])


	@logger.catch
	def advertiser_validation(
		self,
		advertiser_advertisements_amount: int, \
		advertiser_finish_rate: int
	) -> bool:
		"""
		Validate the advertiser based on the number of advertisements and finish rate.

		Args:
			advertiser_advertisements_amount (int): The number of advertisements by the advertiser.
			advertiser_finish_rate (int): The finish rate of the advertiser.

		Returns:
			bool: True if the advertiser is valid, False if it is a scam.
		"""
		return not\
		(advertiser_advertisements_amount < 20 or advertiser_finish_rate < 70)
