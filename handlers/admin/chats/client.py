from aiogram import types
from datetime import datetime
from typing import Union

from config import logger
from create_bot import bot
from handlers import misc
from handlers.admin import manager
from handlers.user import manager as user_manager
from entities import User, Supergroup, Group, Channel

@logger.catch
async def create_chat(message: types.Message):
    """
    Handles the creation of a new chat and user registration.

    Notes:
        This function is designed to be triggered by the "/start" command in any chat.
        The user initiating the command must be an admin.
    """
    admin_id = message["from"]["id"]
    user_id = message["chat"]["id"]

    # Check if the initiator is an admin
    if not await user_manager.is_admin(admin_id):
        return

    # Get language module for the admin
    txt = await misc.get_language_module(admin_id)

    # Prepare chat data
    chat_data = {
        "user_id": user_id,
        "username": str(message["chat"]["title"])
    }

    # Create an instance of the appropriate chat type (Group, Supergroup, or Channel)
    chat: Union[Group, Supergroup, Channel] = User.create_from_chat_type(
        message["chat"]["type"], **chat_data
    )

    # Check if the user already exists
    is_exists = await user_manager.is_user_exists(user_id)

    if is_exists:
        await message.answer(
            txt.chat_restarted, reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        # Configure chat attributes
        chat.entry_date = datetime.now()
        chat.is_bot_on = True
        chat.is_subscription_active = True
        chat.subscription_id = 4
        chat.subscription_begin_date = datetime.now()

        # Register the user
        registered = await user_manager.create_user(chat)
        await manager.add_admin_chat(admin_id, user_id)

        if not registered:
            logger.error(f"{user_id}: {registered=}")
            await message.answer(txt.error)
            return

        # Send success message to the user
        await message.answer(txt.chat_added)

        # Notify the admin about the new user
        await bot.send_message(
            381906725, 
            txt.new_user.format(
                user_id=user_id, username=chat.username
            )
        )
