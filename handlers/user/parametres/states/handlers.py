from aiogram.dispatcher import FSMContext
from aiogram import types

from config import logger
from create_bot import bot

from . import input_checkers as checker

from handlers import misc
from ... import manager
from .. import util
from entities import (
	MainMessage, AdditionalMessage,
	Parametres, Parameter, InputError
)
from entities.parametres import (
	Limits, Spread
)



@logger.catch
async def limits(message: types.Message, state: FSMContext):
	"""
	Handle the input for limits and check its validity.
	"""
	user_id = message["chat"]["id"]
	user_input = message["text"]

	if not await misc.access_check(message):
		return

	result = await checker.limits(user_id, user_input)

	if isinstance(result, InputError):
		kb = await misc.get_keyboard_module(user_id)
		msg = await message.answer(
			result.message,
			reply_markup=kb.inline.back_to_parametres
		)
		await AdditionalMessage.acquire(msg)
		return
	else:
		limits = Limits(result)

	await state.finish()
	await util.save_parameter(user_id, limits)


@logger.catch
async def spread(message: types.Message, state: FSMContext):
	"""
	Handle the input for spread and check its validity.
	"""
	user_id = message["chat"]["id"]
	user_input = message["text"]

	kb = await misc.get_keyboard_module(user_id)
	result = await checker.spread(user_id, user_input)

	if isinstance(result, InputError):
		msg = await message.answer(
			result.message,
			reply_markup=kb.inline.back_to_parametres
		)
		await AdditionalMessage.acquire(msg)
		return
	else:
		spread = Spread(result)

	await state.finish()
	await util.save_parameter(user_id, spread)