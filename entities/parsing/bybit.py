from config import logger
import json
import asyncio
import aiohttp
import urllib

from .parser import (
	Parser, ParserResponse, Advertisement,
	Advertiser, AdvСonditions
) 

from aiohttp.client import ClientSession
from aiohttp.client_reqrep import ClientResponse
from typing import (
	NoReturn, Union, Tuple
)


class BybitParser(Parser):
	banks_alias = {
		"A-Bank": "1",
		"AdvCash": "5",
		"Bank_Transfer": "14",
		"Monobank": "43",
		"Payeer": "51",
		"PrivatBank": "60",
		"QIWI": "62",
		"RaiffeisenBankAval": "63",
		"Tinkoff": "581",
		"Wise": "78",
		"YandexMoney": "88",
		"RaiffeisenBank": "64",
		"RosBank": "185",
		"Revolut": "65",
		"Sepa_Transfer": "118",
		"Sepa_Instant": "303",
		"Halyk": "203",
		"HomeCreditKz": "262",
		"Eurasian": "262",
		"Jysan": "149",
		"Kaspi": "150",
		"CenterCredit": "211",
		"Forte": "144",
		"Humo": "282",
		"Uzcard": "283",
		"PayMe": "53",
		"KapitalBank": "212",
		"UzbekNational": "290",
		"Ziraat": "122",
		"Garanti": "100",
		"KuveytTurk": "151",
		"Papara": "114",
		"QNB": "308",
		"Akbank": "532",
		"Alfa-bank": "583",
		"PayPal": "54",
		"SBP": "382",
		"Sberbank": "582",
		"Skrill": "162",
		"DenizBank": "535",
		"AirTM": "7",
		"MTBank": "332",
		"PerfectMoney": "56",
		"VakifBank": "412",
		"Izibank": "544",
		"ISBank": "414",
		"Technobank": "336"
	}

	@logger.catch
	def _adv_validation(self, response: dict, adv_type: Union["bid", "ask"], bank: str) -> Tuple[AdvСonditions, Advertiser]:
		"""
		Perform validation on each advertisement in the response and return conditions and advertiser data if valid.
		"""
		for advertisement_ndx in range(len(response)):
			advertisement = response[advertisement_ndx]

			 # Extract advertisement data from the response
			price = float(advertisement["price"])
			advertiser_advertisements_amount = advertisement["recentOrderNum"]
			advertiser_finish_rate = int(advertisement["recentExecuteRate"])
			total_adv_amount = len(response)

			# Check price difference and advertiser validation criteria
			if advertisement_ndx != total_adv_amount - 1 and total_adv_amount > 7:
				next_advertisement = response[advertisement_ndx+1]
				next_price = next_advertisement["price"]

				if not self.price_difference_validation(
							advertisement_ndx, adv_type,
							price, next_price, total_adv_amount):
					continue

			if not self.advertiser_validation(
						advertiser_advertisements_amount,
						advertiser_finish_rate):
				continue

			conditions = AdvСonditions(
				fiat=self.fiat,
				currency=self.currency,
				price=float(advertisement["price"]),
				bank=bank,
				limits_min=int(float(advertisement["minAmount"])),
				limits_max=int(float(advertisement["maxAmount"]))
			)
			advertiser = Advertiser(
				advertiser_id=advertisement["userId"]
			)

			advertisement = Advertisement(
				market="Bybit",
				conditions=conditions,
				advertiser=advertiser
			)

			# Determine the position of the advertisement in the list
			self.determine_adv_position(
				advertisement, adv_type
			)
			
		else:
			# No advertimsements
			return None


	@logger.catch
	async def _get_advertisements(self, adv_type: Union["bid", "ask"], bank: str, session: ClientSession) -> NoReturn:
		"""
		Fetch advertisements for the given advertisement type and bank using the Bybit API.
		"""
		if not BybitParser.banks_alias.get(bank):
			return

		# For some reason works only with these headers
		headers = {
			"Content-type": "application/json", 
			"Accept": "application/json"
		}

		url_format = {
			"bid": "1",
			"ask": "0"
		}

		endpoint = "https://api2.bybit.com/fiat/otc/item/online"
		parametres = {
			"userId": "",
			"tokenId": self.currency,
			"currencyId": self.fiat,
			"payment": BybitParser.banks_alias[bank],
			"side": url_format[adv_type],
			"size": "10",
			"page": "1",
			"amount": str(self.limits) if self.limits else "",
			"authMaker": False,
			"canTrade": False
		}

		try:
			async with session.post(
				endpoint, headers=headers, json=parametres
			) as client_response:

				if client_response.status != 200: return
				response = json.loads(await client_response.text())
				if response["result"]["count"] == 0: return

		except Exception as e:
			logger.error(e)
			return

		self._adv_validation(response["result"]["items"], adv_type, bank)
