from config import logger
import json
import asyncio
import aiohttp

from .parser import (
	Parser, ParserResponse, Advertisement,
	Advertiser, AdvСonditions
) 

from aiohttp.client import ClientSession
from aiohttp.client_reqrep import ClientResponse
from typing import (
	NoReturn, Union, Tuple
)



class BinanceParser(Parser):
	banks_alias = {
		"Bank_Transfer": "BANK",
		"YandexMoney": "YandexMoneyNew",
		"Payeer": "Payeer",
		"AdvCash": "Advcash",
		"PrivatBank": "PrivatBank",
		"QIWI": "QIWI",
		"A-Bank": "ABank",
		"Izibank": "izibank",
		"RaiffeisenBankAval": "RaiffeisenBankAval",
		"Monobank": "Monobank",
		"MTBank": "MTBank",
		"Tinkoff": "RaiffeisenBank",
		"Technobank": "Technobank",
		"Skrill": "SkrillMoneybookers",
		"Wise": "Wise",
		"AirTM": "AirTM",
		"RaiffeisenBank": "RaiffeisenBank",
		"RosBank": "RosBankNew",
		"Revolut": "Revolut",
		"Sepa_Transfer": "SEPA",
		"Sepa_Instant": "SEPAinstant",
		"Forte": "ForteBank",
		"Halyk": "HalykBank",
		"HomeCreditKz": "HomeCreditKazakhstan",
		"Eurasian": "EurasianBank",
		"Jysan": "JysanBank",
		"Kaspi": "KaspiBank",
		"CenterCredit": "CenterCreditBank",
		"Humo": "Humo",
		"Uzcard": "Uzcard",
		"PayMe": "Payme",
		"PerfectMoney": "PerfectMoney",
		"KapitalBank": "Kapitalbank",
		"UzbekNational": "UzbekNationalBank",
		"Ziraat": "Ziraat",
		"Garanti": "Garanti",
		"KuveytTurk": "KuveytTurk",
		"Papara": "Papara",
		"DenizBank": "DenizBank",
		"QNB": "QNB",
		"VakifBank": "VakifBank",
		"ISBank": "ISBANK",
		"Akbank": "Akbank"
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
			Advertisement: The validated advertisement object, or None if no valid advertisement found.
		"""
		for advertisement_ndx in range(len(response["data"])):
			advertisement = response["data"][advertisement_ndx]

			# Extract advertisement data
			price = float(advertisement["adv"]["price"])
			advertiser_advertisements_amount = advertisement["advertiser"]["monthOrderCount"]
			advertiser_finish_rate = advertisement["advertiser"]["monthFinishRate"] * 100
			total_adv_amount = len(response["data"])

			# Check price difference validation
			if advertisement_ndx != total_adv_amount - 1 and total_adv_amount > 7:
				next_advertisement = response["data"][advertisement_ndx+1]
				next_price = float(next_advertisement["adv"]["price"])

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
				price=float(advertisement["adv"]["price"]),
				bank=bank,
				limits_min=int(float(advertisement["adv"]["minSingleTransAmount"])),
				limits_max=int(float(advertisement["adv"]["maxSingleTransAmount"]))
			)
			advertiser = Advertiser(
				advertiser_id=str(advertisement["advertiser"]["userNo"])
			)

			advertisement = Advertisement(
				market="Binance",
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
		if not BinanceParser.banks_alias.get(bank):
			return

		parametres_format = {
			"bid": "BUY",
			"ask": "SELL"
		}

		parametres = {
			"fiat": self.fiat,
			"page": 1,
			"rows": 10,
			"tradeType": parametres_format[adv_type],
			"asset": self.currency,
			"countries": [],
			"proMerchantAds": False,
			"shieldMerchantAds": False,
			"publisherType": None,
			"payTypes": [BinanceParser.banks_alias[bank]],
			"classifies": ["mass", "profession"]
		}

		async with session.post(
			'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search',
			headers=self.headers, json=parametres) as client_response:
			response = json.loads(str(await client_response.text()))

			if not response["data"]:
				return

		if not response["success"]:
			logger.error(response)
			return

		self._adv_validation(response, adv_type, bank)
