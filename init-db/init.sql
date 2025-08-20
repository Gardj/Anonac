-- Создание схемы, если не существует
CREATE SCHEMA IF NOT EXISTS anonac;

-- Создание таблицы anonac.userdata
CREATE TABLE IF NOT EXISTS anonac.userdata (
    id BIGINT PRIMARY KEY,                            -- Telegram ID
    name TEXT,                                        -- Имя пользователя (username)
    status TEXT CHECK (status IN ('active', 'unactive', 'search')),  -- Статус пользователя
    signal_id BIGINT REFERENCES anonac.userdata(id) ON DELETE SET NULL, -- ID собеседника
    gender TEXT CHECK (gender IN ('male', 'female')),                 -- Пол пользователя
    interests TEXT[],                                  -- Интересы (список)
    register_at TIMESTAMP DEFAULT NOW(),              -- Дата регистрации
    update_at TIMESTAMP DEFAULT NOW()                 -- Последнее обновление
);
