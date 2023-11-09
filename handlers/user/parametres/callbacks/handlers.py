from aiogram import types

from create_bot import bot
from config import logger
from database import parametres as db

from handlers import misc
from ... import manager
from .. import util
from entities import (
	MainMessage, AdditionalMessage,
	User, Parametres
)
from entities.parametres import (
	Banks, Markets, BidType, AskType,
	Currencies, Fiat
)



@logger.catch
async def banks(callback: types.CallbackQuery):
	"""
	Handle the callback for banks and check its validity.
	"""
	user_id = callback["message"]["chat"]["id"]
	await callback.answer()

	button_value = callback["data"].split()[1]
	message = await AdditionalMessage.get_message(user_id)

	txt = await misc.get_language_module(user_id)
	kb = await misc.get_keyboard_module(user_id)

	if not message:
		await callback.message.delete()
		return

	message_markup = message.reply_markup
	chosen_banks: list = util.get_markup_chosen_values(message_markup)
	fiat: Fiat = await manager.get_parameter(user_id, Fiat)

	if button_value == "complete":
		new_param = Banks(chosen_banks)

		await util.save_parameter(user_id, new_param)
		return
	else:
		bank = button_value


	if bank in chosen_banks:
		if len(chosen_banks) == 1:
			return
		chosen_banks.remove(bank)
	else:
		chosen_banks.append(bank)


	markup = await kb.inline.get_parametres_banks(fiat)
	edited_markup = util.mark_markup_chosen_buttons(
		dict(markup).copy(), chosen_banks
	)
	
	message_text = txt.banks_info.format(banks=" | ".join(chosen_banks))
	msg = await AdditionalMessage.edit(
		user_id, message_text,
		reply_markup=edited_markup
	)
	await AdditionalMessage.acquire(msg, message_text, edited_markup)


@logger.catch
async def currencies(callback: types.CallbackQuery):
	"""
	Handle the callback for currencies and check its validity.
	"""
	user_id = callback["message"]["chat"]["id"]
	await callback.answer()

	txt = await misc.get_language_module(user_id)
	kb = await misc.get_keyboard_module(user_id)

	button_value = callback["data"].split()[1]
	message = await AdditionalMessage.get_message(user_id)

	if not message:
		await callback.message.delete()
		return

	message_markup = message.reply_markup
	chosen_currencies: list = util.get_markup_chosen_values(message_markup)

	if button_value == "complete":
		currencies = Currencies(chosen_currencies)

		await util.save_parameter(user_id, currencies)
		return
	else:
		currency = button_value


	if currency in chosen_currencies:
		if len(chosen_currencies) == 1:
			return
		chosen_currencies.remove(currency)
	else:
		chosen_currencies.append(currency)

	markup = await kb.inline.get_parametres_currencies()
	edited_markup = util.mark_markup_chosen_buttons(
		dict(markup).copy(), chosen_currencies
	)

	message_text = txt.currencies_info.format(currencies=" | ".join(chosen_currencies))
	msg = await AdditionalMessage.edit(
		user_id, message_text,
		reply_markup=edited_markup
	)
	await AdditionalMessage.acquire(msg, message_text, edited_markup)



@logger.catch
async def markets(callback: types.CallbackQuery):
	"""
	Handle the callback for markets and check its validity.
	"""
	user_id = callback["message"]["chat"]["id"]
	await callback.answer()

	txt = await misc.get_language_module(user_id)
	kb = await misc.get_keyboard_module(user_id)

	button_value = callback["data"].split()[1]
	message = await AdditionalMessage.get_message(user_id)

	if not message:
		await callback.message.delete()
		return

	message_markup = message.reply_markup
	chosen_markets: list = util.get_markup_chosen_values(message_markup)


	if button_value == "complete":
		markets = Markets(chosen_markets)

		await util.save_parameter(user_id, markets)
		return
	else:
		market = button_value


	if market in chosen_markets:
		if len(chosen_markets) == 1:
			return
		chosen_markets.remove(market)
	else:
		chosen_markets.append(market)

	markup = await kb.inline.get_parametres_markets()
	edited_markup = util.mark_markup_chosen_buttons(
		dict(markup).copy(), chosen_markets
	)


	message_text = txt.markets_info.format(markets=" | ".join(chosen_markets))
	msg = await AdditionalMessage.edit(
		user_id, message_text,
		reply_markup=edited_markup
	)
	await AdditionalMessage.acquire(msg, message_text, edited_markup)


@logger.catch
async def trading_type(callback: types.CallbackQuery):
	"""
	Handle the callback for trading_type and check its validity.
	"""
	user_id = callback["message"]["chat"]["id"]
	await callback.answer()

	txt = await misc.get_language_module(user_id)
	kb = await misc.get_keyboard_module(user_id)

	button_value = callback["data"].split()[1]
	message = await AdditionalMessage.get_message(user_id)

	if not message:
		await callback.message.delete()
		return

	message_markup = message.reply_markup
	chosen_trading_type: list = util.get_markup_chosen_values(message_markup)[0]
	chosen_bid_type, chosen_ask_type = chosen_trading_type.split("-")

	if button_value == "complete":
		bid_type = BidType(chosen_bid_type)
		ask_type = AskType(chosen_ask_type)

		await util.save_parameter(user_id, bid_type)
		await util.save_parameter(user_id, ask_type)
		return
	else:
		trading_type = button_value
		bid_type, ask_type = trading_type.split("-")

	markup = kb.inline.parametres_trading_type
	edited_markup = util.mark_markup_chosen_buttons(
		dict(markup).copy(), trading_type
	)

	message_text = txt.trading_type_info.format(bid_type=bid_type, ask_type=ask_type)
	msg = await AdditionalMessage.edit(
		user_id, message_text,
		reply_markup=edited_markup
	)
	await AdditionalMessage.acquire(msg, message_text, edited_markup)


@logger.catch
async def fiat(callback: types.CallbackQuery):
	"""
	Handle the callback for fiat and check its validity.
	"""
	user_id = callback["message"]["chat"]["id"]
	await callback.answer()

	txt = await misc.get_language_module(user_id)
	kb = await misc.get_keyboard_module(user_id)

	button_value = callback["data"].split()[1]
	message = await AdditionalMessage.get_message(user_id)

	if not message:
		await callback.message.delete()
		return

	message_markup = message.reply_markup
	chosen_fiat: str = util.get_markup_chosen_values(message_markup)[0]

	if button_value == "complete":
		fiat = Fiat(chosen_fiat)
		await util.save_parameter(user_id, fiat)

		available_banks: Banks = await db.get_banks_by_fiat(fiat)
		await util.save_parameter(user_id, available_banks)

		return
	else:
		fiat = Fiat(button_value)

	markup = kb.inline.parametres_fiat
	edited_markup = util.mark_markup_chosen_buttons(
		dict(markup).copy(), fiat.value
	)

	message_text = txt.fiat_info.format(fiat=fiat.value)
	msg = await AdditionalMessage.edit(
		user_id, message_text,
		reply_markup=edited_markup
	)
	await AdditionalMessage.acquire(msg, message_text, edited_markup)