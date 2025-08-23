import asyncio
from aiogram import Bot, Dispatcher
from anonac.config import settings
from anonac.database.controller import Database, UserController
from handlers import commands
from anonac.services.matchmaking import signal_controller

async def main():
    db = Database(settings.database_url)
    await db.connect()

    user_controller = UserController(db)

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()
    
    dp.include_router(commands.register_handlers(user_controller))

    try:
        await asyncio.gather(
            dp.start_polling(bot),
            signal_controller(bot, user_controller)
        )
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(main())
