import asyncpg
from typing import Optional, List, Union

class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: Optional[asyncpg.pool.Pool] = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)

    async def close(self):
        if self.pool:
            await self.pool.close()

class UserController:
    def __init__(self, db: Database):
        self.db = db

    async def register_user(self, telegram_id: int, telegram_name: Optional[str]) -> bool:
        async with self.db.pool.acquire() as conn:
            async with conn.transaction():
                existing = await conn.fetchrow(
                    "SELECT id FROM anonac.userdata WHERE id = $1",
                    telegram_id
                )
                if existing:
                    print(f"Пользователь уже существует с ID: {telegram_id}")
                    return False

                await conn.execute(
                    """
                    INSERT INTO anonac.userdata (id, name, status, register_at, update_at)
                    VALUES ($1, $2, 'unactive', NOW(), NOW())
                    """,
                    telegram_id, telegram_name
                )
                print(f"Пользователь добавлен с ID {telegram_id}")
                return True



    async def get_user_id(self, telegram_id: int) -> Optional[asyncpg.Record]:
        async with self.db.pool.acquire() as conn:
            user = await conn.fetchrow(
                "SELECT * FROM anonac.userdata WHERE id = $1",
                telegram_id
            )
            return user
    async def get_status(self, status: str) -> List[asyncpg.Record]:
        async with self.db.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM anonac.userdata WHERE status = $1",
                status
            )
            return rows
        





    async def set_signal(self, user_ids: Union[int, List[int]], signal_id: Optional[int]):
        async with self.db.pool.acquire() as conn:
            if isinstance(user_ids, int):
                # Обработка одного пользователя
                result = await conn.execute(
                    """
                    UPDATE anonac.userdata SET signal_id = $1, update_at = NOW() WHERE id = $2
                    """,
                    signal_id, user_ids
                )
                if result == "UPDATE 0":
                    print(f"Пользователь с ID {user_ids} не найден.")
                else:
                    action = "очищен" if signal_id is None else f"установлен на {signal_id}"
                    print(f"[Info] Сигнал пользователя с ID {user_ids} {action}.")
            else:
                # Обработка списка пользователей (очистка)
                if signal_id is not None:
                    raise ValueError("Для списка user_ids signal_id должен быть None (только очистка).")

                await conn.execute(
                    """
                    UPDATE anonac.userdata SET signal_id = NULL, update_at = NOW() WHERE id = ANY($1::bigint[])
                    """,
                    user_ids
                )
                print(f"[Info] Сигналы очищены для пользователей с ID {user_ids}.")
        

        
    async def set_status(self, user_ids: Union[int, List[int]], status: str):
        async with self.db.pool.acquire() as conn:
            if isinstance(user_ids, int):
                result = await conn.execute(
                    """
                    UPDATE anonac.userdata SET status = $1, update_at = NOW() WHERE id = $2
                    """,
                    status, user_ids
                )
                if result == "UPDATE 0":
                    print(f"Пользователь с ID {user_ids} не найден.")
                else:
                    print(f"[Info] Статус пользователя с ID {user_ids} обновлён на '{status}'.")
            else:
                result = await conn.execute(
                    """
                    UPDATE anonac.userdata SET status = $1, update_at = NOW() WHERE id = ANY($2::bigint[])
                    """,
                    status, user_ids
                )
                # Проверка затруднительна, т.к. UPDATE вернёт количество строк, например "UPDATE 3"
                updated_count = int(result.split(" ")[1]) if "UPDATE" in result else 0
                if updated_count == 0:
                    print(f"Пользователи с ID {user_ids} не найдены.")
                else:
                    print(f"[Info] Статус пользователей с ID {user_ids} обновлён на '{status}'.")

    async def set_gender(self, user_id: int, gender: str):
        allowed_genders = {'male', 'female', 'other'}
        if gender not in allowed_genders:
            raise ValueError(f"Недопустимое значение gender: {gender}. Допустимо только {allowed_genders}")

        async with self.db.pool.acquire() as conn:
            result = await conn.execute(
                """
                UPDATE achat.userdata
                SET gender = $1, update_at = NOW()
                WHERE id = $2
                """,
                gender, user_id
            )
            if result == "UPDATE 0":
                print(f"Пользователь с ID {user_id} не найден.")
            else:
                print(f"[Info] Пол пользователя с ID {user_id} обновлён на '{gender}'.")
