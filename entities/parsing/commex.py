from config import logger
import json
import asyncio
import aiohttp
import urllib
import random

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



class CommexParser(Parser):
	banks_alias = {
		"A-Bank": "ABank",
		"AdvCash": "Advcash",
		"Alfa-bank": "AlfaBank",
		"Bank_Transfer": "BANK",
		"Forte": "ForteBank",
		"Halyk": "HalykBank",
		"Jysan": "JysanBank",
		"Kaspi": "KaspiBank",
		"Monobank": "Monobank",
		"PrivatBank": "PrivatBank",
		"QIWI": "QIWI",
		"RaiffeisenBank":"RaiffeisenBankRussia",
		"RaiffeisenBankAval": "RaiffeisenBankAval",
		"RosBank": "RosBank",
		"Sberbank": "Sberbank",
		"SBP": "SBP",
		"Tinkoff": "Tinkoff",
		"YandexMoney": "Umoney"
	}

	@logger.catch
	def _adv_validation(self, response: dict, adv_type: Union["bid", "ask"], bank: str) -> Tuple[AdvСonditions, Advertiser]:
		"""
		Perform validation on each advertisement in the response and return conditions and advertiser data if valid.
		"""
		for advertisement_ndx in range(len(response)):
			advertisement = response[advertisement_ndx]

			# Extract advertisement data from the response
			price = float(advertisement["adDetailResp"]["price"])
			if advertisement["advertiserVo"]["userStatsRet"]["completedOrderNum"] is None:
				advertiser_advertisements_amount = 0
			else:
				advertiser_advertisements_amount = advertisement["advertiserVo"]["userStatsRet"]["completedOrderNum"]

			if advertisement["advertiserVo"]["userStatsRet"]["finishRate"] is None:
				advertiser_finish_rate = 0.0
			else:
				advertiser_finish_rate = float(advertisement["advertiserVo"]["userStatsRet"]["finishRate"]) * 100
			total_adv_amount = len(response)

			# Check price difference and advertiser validation criteria
			if advertisement_ndx != total_adv_amount - 1 and total_adv_amount > 7:
				next_advertisement = response[advertisement_ndx+1]
				next_price = float(next_advertisement["adDetailResp"]["price"])

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
				price=float(advertisement["adDetailResp"]["price"]),
				bank=bank,
				limits_min=float(advertisement["adDetailResp"]["minSingleTransAmount"]),
				limits_max=float(advertisement["adDetailResp"]["dynamicMaxSingleTransAmount"])
			)
			advertiser = Advertiser(
				advertiser_id=advertisement["advertiserVo"]["userNo"]
			)

			advertisement = Advertisement(
				market="Commex",
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
		Fetch advertisements for the given advertisement type and bank using the Commex API.
		"""
		if not CommexParser.banks_alias.get(bank):
			return

		url_format = {
			"bid": "BUY",
			"ask": "SELL"
		}

		endpoint = "https://www.commex.com/bapi/c2c/v1/friendly/c2c/ad/search"
		parametres = {
			"page": 1,
			"asset": self.currency,
			"fiat": self.fiat,
			"tradeType": url_format[adv_type],
			"rows": 10,
			"payTypes": [bank],
			"transAmount": str(self.limits)
		}
		status_code = 429
		cycles = 0

		try:
			while status_code == 429:
				async with session.post(
					endpoint, headers=self.get_headers(), json=parametres
				) as client_response:

					status_code = client_response.status
					if status_code == 200: 
						response = json.loads(await client_response.text())
						if not response["data"]: return
						break

				cycles += 1
				if cycles % 10 == 0: return

				await asyncio.sleep(random.randint(1, 3))

		except ClientConnectorError:
			return

		self._adv_validation(response["data"], adv_type, bank)
