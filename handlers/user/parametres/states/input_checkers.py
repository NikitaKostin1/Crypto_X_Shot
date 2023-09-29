from aiogram import types
from typing import Union
from config import logger

from handlers.user import manager
from entities import (
	AdditionalMessage, InputError,
	Parametres, TesterParametresChecker
)
from entities.parametres import (
	Spread
)
from assets import texts as txt
from keyboards.user import (
	inline as ikb
)



@logger.catch
async def limits(user_input: str) -> Union[int, InputError]:
	"""
	Check the limits input. Returns the limits value if it matches the criteria.
	Returns an InputError object if the input is incorrect.
	"""
	try:
		limits = int(user_input.replace(" ", ""))
	except:
		return InputError(message=txt.limits_type_error)

	if limits == 0:
		# None is used to specify "any" limits
		return None

	if limits < 500:
		return InputError(message=txt.limits_min_error)
	if limits > 100_000:
		return InputError(message=txt.limits_max_error)

	return limits


@logger.catch
async def spread(user_id: int, user_input: str) -> Union[float, InputError]:
	"""
	Check the spread input. Returns the spread value if it matches the criteria.
	Returns an InputError object if the input is incorrect.
	"""
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