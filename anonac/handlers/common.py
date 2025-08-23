from aiogram import Router, types
from aiogram.filters.command import Command
import anonac.messages
from anonac.database.controller import UserController
import logging

logger = logging.getLogger(__name__)

def register_handlers(user_controller: UserController) -> Router:
    router = Router()

    @router.message(Command("start"))
    async def cmd_start(message: types.Message):
        try:
            user = message.from_user
            await message.answer(anonac.messages.START)

            success = await user_controller.register_user(user.id, user.username)
            if success:
                logger.info(f"Пользователь {user.id} успешно зарегистрирован.")
            else:
                logger.info(f"Пользователь {user.id} уже зарегистрирован.")
        except Exception as e:
            logger.error(f"Ошибка при обработке команды /start. USER({user.id}): {e}")


    @router.message(Command("search"))
    async def cmd_search(message: types.Message):
            try:
                user = message.from_user
                current_user_status = await user_controller.get_status(user.id)

                if current_user_status == "unactive":
                    await message.answer(anonac.messages.SEARCH)
                    await user_controller.set_status(user.id, "search")

                elif current_user_status == "active":
                    await message.answer(anonac.messages.SEARCH_ERROR_ACTIVE)
                
                else:
                    await message.answer(anonac.messages.SEARCH_ERROR_SEARCH)
  
            except Exception as e:
                logger.error(f"Ошибка при обработке команды /search. USER({user.id}): {e}")

    @router.message(Command("stop"))
    async def cmd_stop(message: types.Message):         
        try:
            user = message.from_user

            if await user_controller.get_status(user.id) == "active":
                signal = await user_controller.get_signal(user.id)

                await user_controller.set_status([user.id, signal["id"]], "unactive")
                await user_controller.set_signal([user.id, signal["id"]], None)

                await message.answer(anonac.messages.STOP_USER)
                await message.bot.send_message(signal["id"], anonac.messages.STOP_SIGNAL) 
            else:
                await message.answer(anonac.messages.STOP_ERROR)
    
        except Exception as e:
            logger.error(f"Ошибка при обработке команды /stop. USER({user.id}): {e}")
    
    return router    