from config import logger
import json
import asyncio
import aiohttp
import urllib

from .parser import (
	Parser, ParserResponse, Advertisement,
	Advertiser, AdvСonditions
) 

from aiohttp.client_exceptions import ClientConnectorError
from datetime import datetime
from aiohttp.client import ClientSession
from typing import (
	NoReturn, Union, Tuple
)



class OkxParser(Parser):
	banks_alias = {
		"A-Bank": "A-Bank",
		"AdvCash": "AdvCash",
		"AirTM": "AirTM",
		"Alfa-bank": "Alfa Bank",
		"Bank_Transfer": "bank",
		"Belarusbank": "Belarusbank",
		"Izibank": "Izibank",
		"Monobank": "Monobank",
		"MTBank": "MTBank",
		"Payeer": "Payeer",
		"PayPal": "PayPal",
		"PerfectMoney": "Perfect Money",
		"PrivatBank": "PrivatBank",
		"QIWI": "QiWi",
		"RaiffeisenBankAval": "Raiffaisen Bank",
		"Sberbank": "Sberbank",
		"SBP": "SBP Fast Bank Transfer",
		"Skrill": "Skrill",
		"Technobank": "Technobank",
		"Tinkoff": "Tinkoff",
		"Wise": "Wise",
		"YandexMoney": "Yandex.Money",
		"RaiffeisenBank":"Raiffaizen",
		"RosBank": "Rosbank",
		"Revolut": "Revolut'",
		"Sepa_Instant": "SEPA Instant",
		"Halyk": "Halyk Bank",
		"HomeCreditKz": "Home Credit",
		"Eurasian": "Eurasian Bank",
		"Jysan": "Jysan Bank",
		"Kaspi": "Kaspi Bank",
		"CenterCredit": "CenterCredit Bank",
		"Forte": "ForteBank",
		"Ziraat": "Ziraat Bankası",
		"Garanti": "Garanti Bankası",
		"KuveytTurk": "Kuveyt Turk",
		"Papara": "Papara",
		"DenizBank": "Denizbank",
		"QNB": "QNB Finansbank",
		"VakifBank": "Vakıflar Bankası",
		"ISBank": "İş Bankası",
		"Akbank": "Akbank"
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
			advertiser_advertisements_amount = advertisement["completedOrderQuantity"]
			advertiser_finish_rate = float(advertisement["completedRate"]) * 100
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
				limits_min=int(float(advertisement["quoteMinAmountPerOrder"])),
				limits_max=int(float(advertisement["quoteMaxAmountPerOrder"]))
			)
			advertiser = Advertiser(
				advertiser_id=str(advertisement["publicUserId"])
			)

			advertisement = Advertisement(
				market="OKX",
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
		Fetch advertisements for the given advertisement type and bank using the OKX API.
		"""
		if not OkxParser.banks_alias.get(bank):
			return

		adv_type_alias = {
			"bid": "sell",
			"ask": "buy"
		}
		sort_alias = {
			"bid": "price_inc",
			"ask": "price_desc"
		}

		endpoint = "https://www.okx.com/v3/c2c/tradingOrders/getMarketplaceAdsPrelogin"
		parametres = {
			"t": int(datetime.now().timestamp()),
			"side": adv_type_alias[adv_type],
			"paymentMethod": OkxParser.banks_alias[bank],
			"userType": "all",
			"hideOverseasVerificationAds": "false",
			"sortType": sort_alias[adv_type],
			"urlId": "1",
			"limit": "20",
			"cryptoCurrency": self.currency.lower(),
			"fiatCurrency": self.fiat.lower(),
			"currentPage": "1",
			"numberPerPage": "20"
		}

		url_params = urllib.parse.urlencode(parametres)
		url = str(endpoint) + "?" + str(url_params)

		try:
			async with session.get(
				url, headers=self.get_headers(), ssl=False
			) as client_response:
				if client_response.status != 200: return
				response = json.loads(await client_response.text())

				if not response["data"]:
					return
				if not response["data"][adv_type_alias[adv_type]]:
					return

		except ClientConnectorError:
			return

		self._adv_validation(response["data"][adv_type_alias[adv_type]], adv_type, bank)