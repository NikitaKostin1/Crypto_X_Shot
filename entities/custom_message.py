from aiogram.utils.exceptions import MessageNotModified
from aiogram.types.input_media import InputMedia
from aiogram.types.input_file import InputFile
from aiogram import types
from typing import Union, Dict

from create_bot import bot
from config import logger



class MessageHandler:
	"""
	Messages pool to handle inline markup
	or to edit an old message
	"""
	def __init__(self):
		self.storage: Dict[int, types.Message] = {}


	@logger.catch
	async def acquire(self, message: types.Message, text: str=None, reply_markup: types.InlineKeyboardMarkup=None) -> None:
		"""
		Rewrite message in storage 
		or set new message.
		If in storage was message, inline markup deletes
		"""
		if not message:
			return None

		user_id = message["chat"]["id"]

		if user_id in self.storage:
			if self.storage[user_id]:
				former_message: types.Message = self.storage[user_id]

				if not text:
					text = former_message["text"]

				try:
					await former_message.edit_text(
						text=text,
						reply_markup=reply_markup
					)
				except:
					pass

		self.storage[user_id] = message


	@logger.catch
	async def release(self, user_id: int) -> types.Message:
		"""
		Deletes message from storage by user_id
		Returns rewritten message: types.Message
		"""
		if not user_id in self.storage:
			return
		if not self.storage[user_id]:
			return

		message = self.storage[user_id]
		self.storage[user_id] = None
		message_id = message["message_id"]

		if "text" in message:
			text = message["text"]
		else:
			text = message["caption"]

		try:
			await bot.edit_message_text(
				chat_id=user_id,
				message_id=message_id,
				text=text,
				reply_markup=None,
				disable_web_page_preview=True
			)
		except:
			pass

		return message


	@logger.catch
	async def edit(self, user_id: int, text: str=None, reply_markup: types.InlineKeyboardMarkup=None) -> Union[types.Message, None]:
		"""
		Edit message from storage
		Return bool value of operation
		"""
		if not user_id in self.storage:
			return None
		if not self.storage[user_id]:
			return None			

		message = self.storage[user_id]	
		message_id = message["message_id"]

		if not text:
			if "text" in message:
				text = message["text"]
			else:
				text = message["caption"]

		try:
			msg = await message.edit_text(
				text=text,
				reply_markup=reply_markup
			)
			await self.acquire(msg, text, reply_markup)

			return msg
		except:
			return None


	@logger.catch
	async def delete(self, user_id: int) -> bool:
		"""
		Deletes message from chat
		(Remains in storage)
		"""
		if not user_id in self.storage:
			return False
		if not self.storage[user_id]:
			return False	

		message = await self.release(user_id)

		try:
			await message.delete()
			return True
		except:
			return False
		


	@logger.catch
	async def edit_media(self, user_id: int, media: InputMedia) -> bool:
		"""
		Use this method to edit animation, audio, document, photo, or video messages. 
		If a message is part of a message album, then it can be edited only to an audio for audio albums, 
		only to a document for document albums and to a photo or a video otherwise.
		Media's caption removes.

		https://docs.aiogram.dev/en/dev-3.x/api/methods/edit_message_media.html
		"""
		if not user_id in self.storage:
			return
		if not self.storage[user_id]:
			return False

		message = self.storage[user_id]	
		# message_id = message["message_id"]

		try:
			await message.edit_media(
					media=media
				)
			return True
		except:
			return False


	@logger.catch
	async def get_message(self, user_id: int) -> types.Message:
		if not user_id in self.storage:
			return None
		if not self.storage[user_id]:
			return None

		return self.storage[user_id]



MainMessage = MessageHandler()
AdditionalMessage = MessageHandler()