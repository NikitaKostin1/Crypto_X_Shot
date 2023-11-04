from config import logger
import asyncio
import aiohttp
import http.cookiejar
import json
import urllib

from .parser import (
	Parser
)
from .types import (
	ParserResponse, Advertisement,
	Advertiser, AdvСonditions
)

from aiohttp.client import ClientSession
from aiohttp.client_reqrep import ClientResponse
from typing import (
	NoReturn, Union, Tuple
)



class BitpapaParser(Parser):
	banks_alias = {	
		"Bank_Transfer": "SPECIFIC_BANK",
		"PerfectMoney": "Perfect money",
		"Payeer RUB": "Payeer RUB",
		"Payeer USD": "Payeer USD",
		"Payeer EUR": "Payeer EUR",
		"PayPal": "Paypal",
		"Skrill": "Skrill",
		"QIWI": "QIWI",
		"YandexMoney": "YM",
		"Sberbank": "B1",
		"Alfa-bank": "B2",
		"Tinkoff": "B3",
		"RaiffeisenBank": "B8",
		"PrivatBank": "B11",
		"Kaspi": "B17",
		"Revolut": "B25",
		"HomeCreditKz": "B29",
		"Monobank": "B30",
		"Forte": "B36",
		"Sepa_Transfer": "B46",
		"Sepa_Instant": "B46",
		"SBP": "B80",
		"MTBank": "B81",
		"Technobank": "B85",
		"A-Bank": "B87",
		"RosBank": "B93",
		"Ziraat": "B102",
		"Garanti": "B103",
		"KuveytTurk": "B105",
		"DenizBank" :"B106",
		"VakifBank": "B108",
		"Jysan": "B149"
	}


	@logger.catch
	def _adv_validation(self, response: dict, adv_type: Union["bid", "ask"], bank: str) -> Advertisement:
		"""
		Validate and process the advertisement data from the response.

		Args:
			response (dict): The response data containing advertisement information.
			adv_type (Union["bid", "ask"]): The type of advertisement ("bid" or "ask").
			bank (str): The bank associated with the advertisements.

		Returns:
			Advertisement: The validated p2p advertisement object, or None if no valid advertisement found.
		"""
		for advertisement_ndx in range(len(response["ads"])):
			advertisement = response["ads"][advertisement_ndx]

			# Extract advertisement data
			price = float(advertisement["price"])
			advertiser_advertisements_amount = advertisement["user"]["trades_count"]
			advertiser_deals = advertisement["user"]["feedback_count_detailed"]

			total_deals = advertisement["user"]["trades_count"]
			if total_deals == 0:
				continue
			advertiser_finish_rate = ((total_deals - advertiser_deals["block"]) / total_deals) * 100

			total_adv_amount = len(response["ads"])

			# Check price difference validation
			if advertisement_ndx != total_adv_amount - 1 and total_adv_amount > 7:
				next_advertisement = response["ads"][advertisement_ndx+1]
				next_price = float(next_advertisement["price"])

				if not self.price_difference_validation(
							advertisement_ndx, adv_type,
							price, next_price, total_adv_amount):
					continue

			# Check advertiser validation
			if not self.advertiser_validation(
						advertiser_advertisements_amount,
						advertiser_finish_rate):
				continue

			conditions = AdvСonditions(
				fiat=self.fiat,
				currency=self.currency,
				price=float(advertisement["price"]),
				bank=bank,
				limits_min=int(float(advertisement["amount_min"])),
				limits_max=int(float(advertisement["amount_max"]))
			)
			advertiser = Advertiser(
				advertiser_id=advertisement["user"]["user_name"]
			)

			advertisement = Advertisement(
				market="bitpapa",
				conditions=conditions,
				advertiser=advertiser
			)

			# Determine the position of the advertisement
			self.determine_adv_position(
				advertisement, adv_type
			)
			
		else:
			# No advertisements found
			return None


	@logger.catch
	async def _get_advertisements(self, adv_type: Union["bid", "ask"], bank: str, session: ClientSession) -> NoReturn:
		"""
		Fetch and process advertisements from the API based on the specified parameters.

		Args:
			adv_type (Union["bid", "ask"]): The type of advertisement ("bid" or "ask").
			bank (str): The bank associated with the advertisements.
			session (ClientSession): The aiohttp ClientSession to use for the HTTP request.
		"""

		# Closed duo to cloudflare defense
		return 


		if bank == "Payeer":
			bank = bank + " " + self.fiat

		if not BitpapaParser.banks_alias.get(bank):
			return

		adv_type_alias = {
			"bid": "sell",
			"ask": "buy"
		}
		sort_alias = {
			"bid": "price",
			"ask": "-price",
		}

		base = "https://bitpapa.com/api/v1/pro/search"
		parametres = {
			"crypto_amount": "",
			"type": adv_type_alias[adv_type],
			"page": "1",
			"sort": sort_alias[adv_type],
			"currency_code": self.fiat,
			"previous_currency_code": self.fiat,
			"crypto_currency_code": self.currency,
			"payment_method_bank_code": BitpapaParser.banks_alias[bank],
			"with_correct_limits": False,
			"limit": "20"
		}

		url_params = urllib.parse.urlencode(parametres)
		url = str(base) + "?" + str(url_params)
		headers = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0",
			"Accept": self.headers["Accept"],
			"Cookie": "cf_clearance=H0fxWy0kOTT3.Q3pNNUESmIwx355drYKz4GvywOCd_o-1699032768-0-1-2bf61a3b.6ad02537.7cf745db-150.0.0",
			# The problem is cloudflare cookies that are generated every time 
		}

		async with session.get(url, headers=headers) as client_response:
			if client_response.status != 200: return

			response = json.loads(str(await client_response.text()))

		self._adv_validation(response, adv_type, bank)
