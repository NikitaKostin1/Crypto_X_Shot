from config import logger, get_conn
from typing import Union
from database import user as db

from assets.texts import (
	ru as txt_ru, en as txt_en
)
from keyboards import (
	ru as kb_ru, en as kb_en
)


lang_modules = {
	"ru": txt_ru,
	"en": txt_en
}
kb_modules = {
	"ru": kb_ru,
	"en": kb_en
}

async def _get_language_string(user_id: int) -> Union[str, None]:
	"""
	Get the language preference for a given user.

	Args:
		user_id (int): The ID of the user.

	Returns:
		Union[str, None]: The user's language preference or None if not found.
	"""
	try:
		connection = await get_conn()
		language_string = await db.get_language(connection, user_id)
		return language_string

	except Exception as e:
		logger.error(f"{user_id}: No language detected [{e}]")
		return None



@logger.catch
async def get_language_module(user_id: int, default_lang: str="ru"):
    """
    Get the language module for a user.

    Args:
        user_id (int): The ID of the user.
        default_lang (str): The default language if the user's language is not found.

    Returns:
        The language module for the user or the default language module.
    """
	language_string = await _get_language_string(user_id)

	if module := lang_modules.get(language_string):
		return module

	logger.warning(f"{user_id}: No language module detected for '{language_string}'")
	return lang_modules[default_lang]


@logger.catch
async def get_keyboard_module(user_id: int, default_lang: str="ru"):
    """
    Get the keyboard module for a user.

    Args:
        user_id (int): The ID of the user.
        default_lang (str): The default language if the user's language is not found.

    Returns:
        The keyboard module for the user or the default keyboard module.
    """
	language_string = await _get_language_string(user_id)

	if module := kb_modules.get(language_string):
		return module

	logger.warning(f"{user_id}: No keyboard module detected for '{language_string}'")
	return kb_modules[default_lang]
