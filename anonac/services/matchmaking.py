import asyncio
import random
from anonac.database.controller import UserController
from anonac.messages import FOUND
from aiogram import Bot


async def signal_controller(bot: Bot, user_controller: UserController):
    while True:
        try:
            users = await user_controller.get_status_list("search")
            if len(users) >= 2:
                
                signal_1, signal_2 = random.sample(users, 2)
                id_1 = signal_1["id"]
                id_2 = signal_2["id"]

                await user_controller.set_signal(id_1, id_2)
                await user_controller.set_signal(id_2, id_1)

                await user_controller.set_status([id_1, id_2], "active")


                await bot.send_message(id_1, FOUND)
                await bot.send_message(id_2, FOUND)

        except Exception as e:
            print(f"[Matchmaking Error] {e}")

        await asyncio.sleep(0.1)