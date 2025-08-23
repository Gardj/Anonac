from aiogram import Router, types
from anonac.database.controller import UserController
import anonac.messages
import logging

logger = logging.getLogger(__name__)

def register_chat_handlers(user_controller: UserController) -> Router:
    router = Router()

    @router.message()
    async def relay_message(message: types.Message):
        try:
            user = message.from_user

            current_user_status = await user_controller.get_status(user.id)

            if current_user_status != "active":
                await message.answer(anonac.messages.NULL_SIGNAL_ERROR)
                return

            signal = await user_controller.get_signal(user.id)

            signal_id = signal["id"]


            if message.text:
                await message.bot.send_message(signal_id, message.text)
            elif message.photo:
                photo = message.photo[-1]
                await message.bot.send_photo(
                    signal_id,
                    photo.file_id,
                    caption=message.caption,
                    has_spoiler=True
                )
            elif message.video:
                await message.bot.send_video(
                    signal_id,
                    message.video.file_id,
                    caption=message.caption
                )
            elif message.voice:
                await message.bot.send_voice(
                    signal_id,
                    message.voice.file_id,
                    caption=message.caption
                )
            elif message.video_note:
                await message.bot.send_video_note(
                    signal_id,
                    message.video_note.file_id
                )
            elif message.document:
                await message.bot.send_document(
                    signal_id,
                    message.document.file_id,
                    caption=message.caption
                )
            elif message.sticker:
                await message.bot.send_sticker(
                    signal_id,
                    message.sticker.file_id
                )
            elif message.animation:
                await message.bot.send_animation(
                    signal_id,
                    message.animation.file_id,
                    caption=message.caption
                )
            else:
                await message.answer("Тип сообщения не поддерживается.")
        except Exception as e:
            logger.error(f"Ошибка пересылки сообщения от {user.id} к {signal_id}: {e}")
            await message.answer("Ошибка при отправке сообщения собеседнику.")

    return router