from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.exceptions import (
	BotBlocked, ChatNotFound, 
	MessageToEditNotFound, MessageNotModified
)

from handlers import misc
from handlers.user import manager as user_manager
from database import parametres as db
from create_bot import bot
from config import logger
import asyncio

from typing import (
	NoReturn, Union, Tuple
)
from entities.parsing.types import (
	ParserResponse, Advertisement
)
from entities import (
	Parser, Signal,
	BinanceParser, HuobiParser,
	BybitParser, OkxParser, 
	BitpapaParser, CommexParser,
	Parametres
)



fiats_symbols: dict = dict()
async def set_fiats_symbols():
	global fiats_symbols

	symbols: dict = await db.fiats_symbols()
	fiats_symbols = symbols



@logger.catch
async def notificate_user(user_id: int) -> NoReturn:
	"""
	Send a notification to the user about inefficient parameters
	"""
	try:
		txt = await misc.get_language_module(user_id)
		await bot.send_message(user_id, txt.inefficient_parametres)
	except BotBlocked:
		await user_manager.disable_bot(user_id)
	except ChatNotFound:
		pass



@logger.catch
async def gather_parsers_responses(
	currency: str, parametres: Parametres
) -> Tuple[ParserResponse]:
	""""
	Gather responses from parsers for the specified currency and parameters.

	Args:
		currency (str): The currency to gather responses for.
		parametres (Parametres): The parameters to use for parsing.

	Returns:
		Tuple[ParserResponse]: A tuple of ParserResponse objects representing the responses from parsers.
	"""
	parsers = {
		"Binance": BinanceParser,
		"Huobi": HuobiParser,
		"Bybit": BybitParser, 
		"OKX": OkxParser,
		"bitpapa": BitpapaParser,
		"Commex": CommexParser
	}
	parsers_responses = list()

	for market in parametres.markets.value:
		if not parsers.get(market):
			continue
		MarketParser: Parser = parsers[market]

		parser = MarketParser(
			fiat=parametres.fiat.value,
			currency=currency,
			banks=parametres.banks.value,
			limits=parametres.limits.value
		)
		response: ParserResponse = await parser.get_p2p()
		parsers_responses.append(response)

	return tuple(parsers_responses)


@logger.catch	
async def send_signal(
	user_id: int, parametres: Parametres,
	bid: ParserResponse, ask: ParserResponse,
	former_signals: Tuple[Signal], signal_index: int
) -> Union[Signal, None]:
	"""
	Send a signal to the user if the spread meets the parameters.

	Args:
		user_id (int): The ID of the user.
		parametres (Parametres): The parameters to use for signal filtering.
		bid (ParserResponse): The bid response from a parser.
		ask (ParserResponse): The ask response from a parser.
		former_signals (Tuple[Signal]): Previously sent signals.
		signal_index (int): Index of the signal to compare with.

	Returns:
		Union[Signal, None]: Signal object if the signal is sent, None otherwise.
	"""
	# Define the threshold for identifying scam spreads
	scam_spread = 7

	txt = await misc.get_language_module(user_id)

	bid_price = bid.conditions.price
	ask_price = ask.conditions.price
	spread = round((1 - bid_price / ask_price) * 100, 2)

	if spread > scam_spread:
		# Skip signals with scam spread
		return None

	if spread < parametres.spread.value:
		# Skip signals that do not meet the spread parameter
		return None

	if signal_index < len(former_signals):
		# Check if the spread has decreased compared to a previous signal
		former_bid_price = former_signals[signal_index].bid.conditions.price
		former_ask_price = former_signals[signal_index].ask.conditions.price
		former_spread = round((1 - former_bid_price / former_ask_price) * 100, 2)

		if former_spread == spread:
			return former_signals[signal_index]
	else:  # Debugging
		former_spread = None

	if fiats_symbols.get(parametres.fiat.value):
		fiat_symbol = fiats_symbols[parametres.fiat.value]
	else:
		fiat_symbol = parametres.fiat.value

	text = txt.message.format(
		bid_market=bid.market,
		ask_market=ask.market,
		currency=bid.conditions.currency,
		bid_price=f"{bid_price:,.2f}",
		ask_price=f"{ask_price:,.2f}",
		spread=spread,
		bid_limits_min=f"{bid.conditions.limits_min:,}",
		bid_limits_max=f"{bid.conditions.limits_max:,}",
		bid_bank=bid.conditions.bank,
		ask_limits_min=f"{ask.conditions.limits_min:,}",
		ask_limits_max=f"{ask.conditions.limits_max:,}",
		ask_bank=ask.conditions.bank,
		fiat_symbol=fiat_symbol
	)

	markup = await generate_markup(user_id, bid, ask)

	try:
		if signal_index >= len(former_signals):
			msg = await bot.send_message(
				chat_id=user_id, 
				text=text, 
				reply_markup=markup,
				disable_web_page_preview=True
			)

		else:
			message_id = former_signals[signal_index].message_id
			msg = await bot.edit_message_text(
				chat_id=user_id,
				message_id=message_id,
				text=text,
				reply_markup=markup,
				disable_web_page_preview=True
			)

	except BotBlocked:
		await user_manager.disable_bot(user_id)
		return None
	except ChatNotFound:
		return None
	except (MessageToEditNotFound, MessageNotModified):
		msg = former_signals[signal_index]
		bid = former_signals[signal_index].bid
		ask = former_signals[signal_index].ask

	signal = Signal(
		message_id=msg.message_id,
		bid=bid,
		ask=ask
	)

	return signal


@logger.catch
async def delete_expired_signals(
	user_id: int, sent_signals_amount: int,
	former_signals: Tuple[Signal]
) -> NoReturn:
	"""
	Delete expired signals that are no longer relevant.

	Args:
		user_id (int): The ID of the user.
		sent_signals_amount (int): Number of signals sent.
		former_signals (Tuple[Signal]): Previously sent signals.

	Returns:
		None
	"""
	for signal_ndx in range(sent_signals_amount, len(former_signals)):
		signal = former_signals[signal_ndx]

		try:
			await bot.delete_message(
				chat_id=user_id, 
				message_id=signal.message_id
			)
		except:
			pass


@logger.catch
async def iterate_advertisments(
	user_id: int, parametres: Parametres,
	responses: Tuple[ParserResponse],
	former_signals: Tuple[Signal]
) -> Tuple[Signal]:
	"""
	Iterate through responses and send signals to the user for valid bid-ask pairs.

	Args:
		user_id (int): The ID of the user.
		parametres (Parametres): The parameters to use for signal filtering.
		responses (Tuple[ParserResponse]): The responses from parsers.
		former_signals (Tuple[Signal]): Previously sent signals.

	Returns:
		Tuple[Signal]: Tuple of sent signals.
	"""
	sent_signals = list()

	for response in responses:
		if parametres.bid_type.value == "Taker":
			bid = response.best_bid
		else:
			bid = response.second_ask
		if bid is None:
			continue

		for response in responses:
			if parametres.ask_type.value == "Taker":
				ask = response.best_ask
			else:
				ask = response.second_bid
			if ask is None:
				continue

			signal = await send_signal(
				user_id, parametres, bid, ask, 
				former_signals, len(sent_signals)
			)
			if signal:
				sent_signals.append(signal)

			await asyncio.sleep(0.3)

	return tuple(sent_signals)




@logger.catch
async def generate_markup(
	user_id: int, bid: Advertisement, ask: Advertisement
) -> InlineKeyboardMarkup: 
	"""
	Generate an inline keyboard markup for the bid and ask responses

	Args:
		bid (Advertisement): The bid advertisement
		ask (Advertisement): The ask advertisement

	Returns:
		InlineKeyboardMarkup: The generated inline keyboard markup
	"""
	advertiser_id_bid = bid.advertiser.advertiser_id
	advertiser_id_ask = ask.advertiser.advertiser_id

	bid_urls = {
		"Binance": f"https://p2p.binance.com/en/advertiserDetail?advertiserNo={advertiser_id_bid}",
		"Huobi": f"https://c2c.huobi.com/ru-ru/trader/{advertiser_id_bid}",
		"Bybit": f"https://www.bybit.com/fiat/trade/otc/?actionType=1&token={ask.conditions.currency}&fiat={ask.conditions.fiat}",
		"OKX": f"https://www.okx.com/ru/p2p/ads-merchant?publicUserId={advertiser_id_bid}",
		"bitpapa": f"https://bitpapa.com/user/{advertiser_id_bid}",
		"Commex": f"https://www.commex.com/en/advertiserDetail?advertiserNo={advertiser_id_bid}"
	}
	ask_urls = {
		"Binance": f"https://p2p.binance.com/en/advertiserDetail?advertiserNo={advertiser_id_ask}",
		"Huobi": f"https://c2c.huobi.com/ru-ru/trader/{advertiser_id_ask}",
		"Bybit": f"https://www.bybit.com/fiat/trade/otc/?actionType=0&token={ask.conditions.currency}&fiat={ask.conditions.fiat}",
		"OKX": f"https://www.okx.com/ru/p2p/ads-merchant?publicUserId={advertiser_id_ask}",
		"bitpapa": f"https://bitpapa.com/user/{advertiser_id_ask}",
		"Commex": f"https://www.commex.com/en/advertiserDetail?advertiserNo={advertiser_id_ask}"
	}

	try:
		bid_url = bid_urls[bid.market]
		ask_url = ask_urls[ask.market]
	except KeyError:
		return None

	kb = await misc.get_keyboard_module(user_id)

	return kb.inline.get_signal_keyboard(bid_url, ask_url)