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


class HuobiParser(Parser):
	currencies_alias = {
		"BTC": 1,
		"USDT": 2,
		"ETH": 3
	}
	fiats_alias = {
		"RUB": "11",
		"EUR": "14",
		"USD": "2",
		"GBP": "12",
		"UAH": "45",
		"BYN": "72",
		"KZT": "57",
		"UZS": "61",
		"TRY": "23"
	}
	banks_alias = {
		"A-Bank": "149",
		"AdvCash": "0",
		"AirTM": "75",
		"Alfa-bank": "25",
		"Bank_Transfer": "1",
		"Izibank": "499",
		"Monobank": "49",
		"Payeer": "24",
		"PerfectMoney": "43",
		"PrivatBank": "33",
		"QIWI": "9",
		"RaiffeisenBankAval": "155",
		"Sberbank": "29",
		"SBP": "69",
		"Skrill": "40",
		"Tinkoff": "28",
		"Wise": "34",
		"YandexMoney": "19",
		"RaiffeisenBank": "36",
		"RosBank": "358",
		"Revolut": "41",
		"Sepa_Transfer": "35",
		"Sepa_Instant": "303",
		"Forte": "355",
		"Halyk": "354",
		"HomeCreditKz": "425",
		"Eurasian": "137",
		"Jysan": "127",
		"Kaspi": "353",
		"CenterCredit": "424",
		"Humo": "287",
		"Uzcard": "288",
		"PayMe": "23",
		"KapitalBank": "289",
		"UzbekNational": "197",
		"Ziraat": "220",
		"Garanti": "221",
		"KuveytTurk": "375",
		"Papara": "222",
		"QNB": "544"
	}


	@logger.catch
	def _adv_validation(self, response: dict, adv_type: Union["bid", "ask"], bank: str) -> Tuple[AdvСonditions, Advertiser]:
		"""
		Perform validation on each advertisement in the response and return conditions and advertiser data if valid.
		"""
		for advertisement_ndx in range(len(response["data"])):
			advertisement = response["data"][advertisement_ndx]

			# Extract advertisement data from the response
			price = advertisement["price"]
			advertiser_advertisements_amount = advertisement["tradeMonthTimes"]
			advertiser_finish_rate = int(advertisement["orderCompleteRate"])
			total_adv_amount = len(response["data"])

			# Check price difference and advertiser validation criteria
			if advertisement_ndx != total_adv_amount - 1 and total_adv_amount > 7:
				next_advertisement = response["data"][advertisement_ndx+1]
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
				limits_min=int(float(advertisement["minTradeLimit"])),
				limits_max=int(float(advertisement["maxTradeLimit"]))
			)
			advertiser = Advertiser(
				advertiser_id=str(advertisement["uid"])
			)

			advertisement = Advertisement(
				market="Huobi",
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
		Fetch advertisements for the given advertisement type and bank using the Huobi API.
		"""
		if bank not in HuobiParser.banks_alias:
			return

		url_format = {
			"bid": "sell",
			"ask": "buy"
		}

		base = "https://www.huobi.com/-/x/otc/v1/data/trade-market"
		parametres = {
			"coinId": HuobiParser.currencies_alias[self.currency],
			"currency": HuobiParser.fiats_alias[self.fiat],
			"tradeType": url_format[adv_type],
			"currPage": "1",
			"payMethod": HuobiParser.banks_alias[bank],
			"acceptOrder": "-1",
			"country": "",
			"blockType": "general",
			"online": "1",
			"range": "0",
			"amount": self.limits,
			"onlyTradable": "false",
			"isFollowed": "false"
		}
		url_params = urllib.parse.urlencode(parametres)
		url = str(base) + "?" + str(url_params)


		async with session.get(url, headers=self.get_headers()) as client_response:
			try:
				response = json.loads(await client_response.text())
				if response["totalCount"] == 0:
					return
			except Exception as e:
				return

		self._adv_validation(response, adv_type, bank)


