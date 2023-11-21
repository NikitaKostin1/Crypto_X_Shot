from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.admin import manager
from loguru import logger

from typing import Union
from entities import (
	Supergroup, Group, Channel
)


@logger.catch
async def get_admin_chats(admin_id: int) -> InlineKeyboardMarkup:
	chats_list: List[Union[Supergroup, Group, Channel]] = await manager.get_admin_chats(admin_id)

	added_chats = InlineKeyboardMarkup(row_width=3)
	for chat in chats_list:
		chat_btn = InlineKeyboardButton(text=chat.username, callback_data=f"chat_parametres {chat.user_id}")
		added_chats.insert(chat_btn)
	complete_btn = InlineKeyboardButton(text="Назад ↩️", callback_data=f"back_to_chats_menu")
	added_chats.add(complete_btn)

	return added_chats