import asyncpg
import logging
from typing import Optional, List, Union

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Database:
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool: Optional[asyncpg.pool.Pool] = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(dsn=self.dsn)
        logger.info("Подключение к базе данных установлено.")

    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("Подключение к базе данных закрыто.")

class UserController:
    def __init__(self, db: Database):
        self.db = db

    async def register_user(self, telegram_id: int, telegram_name: Optional[str]) -> bool:
        try:
            async with self.db.pool.acquire() as conn:
                async with conn.transaction():
                    existing = await conn.fetchrow(
                        "SELECT id FROM anonac.userdata WHERE id = $1",
                        telegram_id
                    )
                    if existing:
                        logger.info(f"Пользователь уже существует с ID: {telegram_id}")
                        return False

                    await conn.execute(
                        """
                        INSERT INTO anonac.userdata (id, name, status, register_at, update_at)
                        VALUES ($1, $2, 'unactive', NOW(), NOW())
                        """,
                        telegram_id, telegram_name
                    )
                    logger.info(f"Пользователь добавлен с ID {telegram_id}")
                    return True
        except Exception as e:
            logger.error(f"Ошибка при регистрации пользователя с ID {telegram_id}: {e}")
            return False

    async def get_user_id(self, telegram_id: int) -> Optional[asyncpg.Record]:
        try:
            async with self.db.pool.acquire() as conn:
                user = await conn.fetchrow(
                    "SELECT * FROM anonac.userdata WHERE id = $1",
                    telegram_id
                )
                return user
        except Exception as e:
            logger.error(f"Ошибка при получении пользователя с ID {telegram_id}: {e}")
            return None
    async def get_status(self, telegram_id: int) -> Optional[str]:
        """
        Возвращает статус пользователя по его telegram_id.
        """
        try:
            async with self.db.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT status FROM anonac.userdata WHERE id = $1",
                    telegram_id
                )
                if row:
                    return row["status"]
                else:
                    logger.info(f"Пользователь с ID {telegram_id} не найден.")
                    return None
        except Exception as e:
            logger.error(f"Ошибка при получении статуса пользователя с ID {telegram_id}: {e}")
            return None
        
    async def get_status_list(self, status: str) -> List[asyncpg.Record]:
        try:
            async with self.db.pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT * FROM anonac.userdata WHERE status = $1",
                    status
                )
                return rows
        except Exception as e:
            logger.error(f"Ошибка при получении пользователей со статусом {status}: {e}")
            return []
        
    async def get_signal(self, user_id: int) -> Optional[asyncpg.Record]:
        try:
            async with self.db.pool.acquire() as conn:
                # Получаем signal_id для пользователя
                row = await conn.fetchrow(
                    "SELECT signal_id FROM anonac.userdata WHERE id = $1",
                    user_id
                )
                if not row or not row["signal_id"]:
                    logger.info(f"У пользователя {user_id} нет активного сигнала.")
                    return None

                signal_id = row["signal_id"]
                # Получаем все поля пользователя-сигнала
                signal_user = await conn.fetchrow(
                    "SELECT * FROM anonac.userdata WHERE id = $1",
                    signal_id
                )
                return signal_user
            
        except Exception as e:
            logger.error(f"Ошибка при получении объекта signal для пользователя {user_id}: {e}")
            return None
    async def set_signal(self, user_ids: Union[int, List[int]], signal_id: Optional[int]):
        try:
            async with self.db.pool.acquire() as conn:
                if isinstance(user_ids, int):
                    result = await conn.execute(
                        """
                        UPDATE anonac.userdata SET signal_id = $1, update_at = NOW() WHERE id = $2
                        """,
                        signal_id, user_ids
                    )
                    if result == "UPDATE 0":
                        logger.warning(f"Пользователь с ID {user_ids} не найден.")
                    else:
                        action = "очищен" if signal_id is None else f"установлен на {signal_id}"
                        logger.info(f"[Info] Сигнал пользователя с ID {user_ids} {action}.")
                else:
                    if signal_id is not None:
                        raise ValueError("Для списка user_ids signal_id должен быть None (только очистка).")

                    await conn.execute(
                        """
                        UPDATE anonac.userdata SET signal_id = NULL, update_at = NOW() WHERE id = ANY($1::bigint[])
                        """,
                        user_ids
                    )
                    logger.info(f"[Info] Сигналы очищены для пользователей с ID {user_ids}.")
        except Exception as e:
            logger.error(f"Ошибка при обновлении сигналов для пользователей {user_ids}: {e}")

    async def set_status(self, user_ids: Union[int, List[int]], status: str):
        try:
            async with self.db.pool.acquire() as conn:
                if isinstance(user_ids, int):
                    result = await conn.execute(
                        """
                        UPDATE anonac.userdata SET status = $1, update_at = NOW() WHERE id = $2
                        """,
                        status, user_ids
                    )
                    if result == "UPDATE 0":
                        logger.warning(f"Пользователь с ID {user_ids} не найден.")
                    else:
                        logger.info(f"[Info] Статус пользователя с ID {user_ids} обновлён на '{status}'.")
                else:
                    result = await conn.execute(
                        """
                        UPDATE anonac.userdata SET status = $1, update_at = NOW() WHERE id = ANY($2::bigint[])
                        """,
                        status, user_ids
                    )
                    updated_count = int(result.split(" ")[1]) if "UPDATE" in result else 0
                    if updated_count == 0:
                        logger.warning(f"Пользователи с ID {user_ids} не найдены.")
                    else:
                        logger.info(f"[Info] Статус пользователей с ID {user_ids} обновлён на '{status}'.")
        except Exception as e:
            logger.error(f"Ошибка при обновлении статуса для пользователей {user_ids}: {e}")

    async def set_gender(self, user_id: int, gender: str):
        allowed_genders = {'male', 'female', 'other'}
        if gender not in allowed_genders:
            logger.error(f"Недопустимое значение gender: {gender}. Допустимо только {allowed_genders}")
            raise ValueError(f"Недопустимое значение gender: {gender}. Допустимо только {allowed_genders}")

        try:
            async with self.db.pool.acquire() as conn:
                result = await conn.execute(
                    """
                    UPDATE anonac.userdata
                    SET gender = $1, update_at = NOW()
                    WHERE id = $2
                    """,
                    gender, user_id
                )
                if result == "UPDATE 0":
                    logger.warning(f"Пользователь с ID {user_id} не найден.")
                else:
                    logger.info(f"[Info] Пол пользователя с ID {user_id} обновлён на '{gender}'.")
        except Exception as e:
            logger.error(f"Ошибка при обновлении пола пользователя с ID {user_id}: {e}")
