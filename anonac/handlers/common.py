from aiogram import Router, types
from aiogram.filters.command import Command
from anonac.messages import START
from anonac.database.controller import UserController

def register_handlers(user_controller: UserController) -> Router:
    router = Router()

    @router.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer(START)
        await user_controller.register_user(message.from_user.id, message.from_user.username)

    return router
