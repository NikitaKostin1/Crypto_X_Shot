from aiogram.dispatcher import FSMContext
from aiogram import types
from typing import Union, List

from create_bot import bot
from config import logger

from .. import manager
from entities import (
	MainMessage, AdditionalMessage,
	Parametres, Parameter
)
from assets import texts as txt
from keyboards.user import (
	reply as rkb,
	inline as ikb
)



@logger.catch
async def parametres_text(user_id: int) -> str:
	"""
	Return the formatted text for the parametres message based on the user's parameters.
	"""
	params: Parametres = await manager.get_user_parametres(user_id)

	if not params:
		return None

	parametres_text = txt.parametres.format(
		limits="Любая" if not params.limits.value else f"{params.limits.value:,}₽",
		banks=" | ".join(params.banks.value),
		currencies=" | ".join(params.currencies.value),
		markets=" | ".join(params.markets.value),
		spread=params.spread.value,
		bid_type=params.bid_type.value,
		ask_type=params.ask_type.value,
		fiat=params.fiat.value
	)
	return parametres_text


@logger.catch
async def back_to_parametres(user_id_or_query: Union[int, types.CallbackQuery], state: FSMContext=None):
	"""
	Delete the info or error message and return the markup for the Parametres menu message.
	The function can be called manually or handle the callback.
	"""
	if state:
		await state.finish()

	if isinstance(user_id_or_query, types.CallbackQuery):
		user_id = user_id_or_query["from"]["id"]
		await user_id_or_query.answer()
	else:
		user_id = user_id_or_query

	await AdditionalMessage.delete(user_id)

	parametres_message = await parametres_text(user_id)
	if not parametres_message:
		return

	await MainMessage.edit(user_id, parametres_message, reply_markup=ikb.parametres)
	

@logger.catch
async def save_parameter(user_id: int, new_param: Parameter) -> bool:
	"""
	Save the parameters in the database for the user.
	"""
	updated = await manager.update_user_parameter(user_id, new_param)
	await back_to_parametres(user_id)

	if not updated:
		await bot.send_message(user_id, txt.error)


@logger.catch
def mark_markup_chosen_buttons(markup: dict, chosen_values: List[str]) -> dict:
	"""
	Mark chosen buttons in the inline keyboard markup.
	Args:
		markup (dict): The inline keyboard markup.
		chosen_values (list): List of chosen values.

	Returns:
		dict: The modified inline keyboard markup with chosen buttons marked.
	"""
	for row_ndx in range(len(markup["inline_keyboard"])):
		for btn_ndx in range(len(markup["inline_keyboard"][row_ndx])):

			market_btn = markup["inline_keyboard"][row_ndx][btn_ndx]["text"].split()[0]
			if market_btn == "Готово":
				continue

			if market_btn in chosen_values:
				markup["inline_keyboard"][row_ndx][btn_ndx]["text"] = f"{market_btn} ☑️"
			else:
				markup["inline_keyboard"][row_ndx][btn_ndx]["text"] = market_btn

	return markup


@logger.catch
def get_markup_chosen_values(markup: types.InlineKeyboardMarkup) -> List[str]:
	"""
	Get the chosen values from the inline keyboard markup.
	Args:
		markup (types.InlineKeyboardMarkup): The inline keyboard markup.
	Returns:
		List[str]: List of chosen values.
	"""
	chosen_values = []
	for row in markup.inline_keyboard:
		for button in row:
			value = button.callback_data.split()[1]

			if len(button.text.split()) == 2 and \
							value != "complete":
				chosen_values.append(value)

	return chosen_values
