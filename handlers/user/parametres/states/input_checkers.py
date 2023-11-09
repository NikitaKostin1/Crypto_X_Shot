from aiogram import types
from typing import Union
from config import logger

from handlers import misc
from handlers.user import manager
from entities import (
	AdditionalMessage, InputError,
	Parametres, TesterParametresChecker
)
from entities.parametres import (
	Spread, Fiat
)



@logger.catch
async def limits(user_id: int, user_input: str) -> Union[int, InputError]:
	"""
	Check the limits input. Returns the limits value if it matches the criteria.
	Returns an InputError object if the input is incorrect.
	"""
	txt = await misc.get_language_module(user_id)

	try:
		limits = int(user_input.replace(" ", ""))
	except:
		return InputError(message=txt.limits_type_error)

	if limits == 0:
		# None is used to specify "any" limits
		return None

	fiat: Fiat = await manager.get_parameter(
		user_id, Fiat
	)
	fiat_string = fiat.value

	min_limits_by_fiat = {
		"RUB": 500,
		"EUR": 10,
		"USD": 10,
		"GBP": 10,
		"UAH": 300,
		"BYN": 35,
		"KZT": 5_000,
		"TRY": 300
	}
	max_limits_by_fiat = {
		"RUB": 300_000,
		"EUR": 3_000,
		"USD": 3_000,
		"GBP": 3_000,
		"UAH": 115_000,
		"BYN": 10_000,
		"KZT": 1_500_000,
		"TRY": 100_000
	}

	min_limits = min_limits_by_fiat.get(fiat_string, 500)
	max_limits = max_limits_by_fiat.get(fiat_string, 300_000)

	if limits < min_limits:
		return InputError(
			message=txt.limits_min_error.format(limits=f"{min_limits:,}{fiat.symbol}")
			)
	if limits > max_limits:
		return InputError(
			message=txt.limits_max_error.format(limits=f"{max_limits:,}{fiat.symbol}")
		)

	return limits


@logger.catch
async def spread(user_id: int, user_input: str) -> Union[float, InputError]:
	"""
	Check the spread input. Returns the spread value if it matches the criteria.
	Returns an InputError object if the input is incorrect.
	"""
	txt = await misc.get_language_module(user_id)

	try:	
		spread = float(
			user_input.replace(" ", "").replace(",", ".").replace("%", "")
		)
	except:
		return InputError(message=txt.spread_type_error)

	spread = Spread(spread)

	is_tester = await manager.is_tester(user_id)
	if is_tester:
		result = TesterParametresChecker(spread).check()
		if isinstance(result, InputError):
			return result

	if spread.value < 0.5:
		return InputError(message=txt.spread_min_error)
	if spread.value > 5.0:
		return InputError(message=txt.spread_max_error)

	return round(spread.value, 2)