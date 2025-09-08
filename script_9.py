# Создаем файлы миграций и SQL скрипты

# Alembic configuration
alembic_ini = """# A generic, single database configuration.

[alembic]
# path to migration scripts
script_location = alembic

# template used to generate migration files
# file_template = %%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
# If specified, requires the python-dateutil library that can be
# installed by adding `alembic[tz]` to the pip requirements
# string value is passed to dateutil.tz.gettz()
# leave blank for localtime
# timezone =

# max length of characters to apply to the
# "slug" field
# truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# version number format.  This value may contain date time variables
# version_num = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d

# the output encoding used when revision files
# are written from script.py.mako
# output_encoding = utf-8

sqlalchemy.url = postgresql://postgres:postgres@localhost/pairlingua


[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.

# format using "black" - use the console_scripts runner, against the "black" entrypoint
# hooks = black
# black.type = console_scripts
# black.entrypoint = black
# black.options = -l 79 REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

# Alembic env.py
alembic_env = """import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Add app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.database import Base
from app.models import *  # Import all models

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here
target_metadata = Base.metadata

# Set database URL from environment
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    \"\"\"Run migrations in 'offline' mode.\"\"\"
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    \"\"\"Run migrations in 'online' mode.\"\"\"
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
"""

# Alembic script template
alembic_script = """\"\"\"${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}

\"\"\"
from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# revision identifiers, used by Alembic.
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    ${downgrades if downgrades else "pass"}
"""

# Initial database setup SQL
init_db_sql = """-- PairLingua Database Initialization
-- This script creates the initial database structure

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set timezone
SET timezone = 'UTC';

-- Create custom types
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'cefr_level') THEN
        CREATE TYPE cefr_level AS ENUM ('A1', 'A2', 'B1', 'B2', 'C1', 'C2');
    END IF;
END $$;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nickname VARCHAR(100) UNIQUE,
    locale VARCHAR(10) DEFAULT 'ru',
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP,
    deleted_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false
);

-- User profiles table
CREATE TABLE IF NOT EXISTS profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    avatar_url TEXT,
    bio TEXT,
    daily_goal VARCHAR(20) DEFAULT '10',
    difficulty_preference VARCHAR(10) DEFAULT 'adaptive',
    notification_enabled BOOLEAN DEFAULT true,
    settings JSONB DEFAULT '{}'::jsonb
);

-- Word pairs table
CREATE TABLE IF NOT EXISTS word_pairs (
    id BIGSERIAL PRIMARY KEY,
    spanish_word VARCHAR(200) NOT NULL,
    russian_word VARCHAR(200) NOT NULL,
    audio_url TEXT,
    cefr_level VARCHAR(2),
    frequency_rank INTEGER,
    tags TEXT[] DEFAULT '{}',
    examples JSONB DEFAULT '[]'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User cards table (SM-2 algorithm)
CREATE TABLE IF NOT EXISTS user_cards (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    word_pair_id BIGINT NOT NULL REFERENCES word_pairs(id) ON DELETE CASCADE,
    ease_factor NUMERIC(4,2) DEFAULT 2.50,
    repetition_count INTEGER DEFAULT 0,
    interval_days INTEGER DEFAULT 0,
    due_date TIMESTAMP,
    last_quality SMALLINT,
    last_reviewed_at TIMESTAMP,
    total_reviews INTEGER DEFAULT 0,
    correct_reviews INTEGER DEFAULT 0,
    accuracy NUMERIC(4,2) DEFAULT 0.0,
    average_response_time INTEGER,
    is_learning BOOLEAN DEFAULT true,
    is_suspended BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, word_pair_id)
);

-- Reviews table
CREATE TABLE IF NOT EXISTS reviews (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    word_pair_id BIGINT NOT NULL REFERENCES word_pairs(id) ON DELETE CASCADE,
    user_card_id BIGINT NOT NULL REFERENCES user_cards(id) ON DELETE CASCADE,
    quality SMALLINT NOT NULL CHECK (quality >= 0 AND quality <= 5),
    response_time_ms INTEGER,
    source VARCHAR(50) DEFAULT 'web',
    session_id UUID,
    ease_factor_before INTEGER,
    ease_factor_after INTEGER,
    interval_before INTEGER,
    interval_after INTEGER,
    reviewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Study sessions table
CREATE TABLE IF NOT EXISTS study_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    active_pair_ids INTEGER[] DEFAULT '{}',
    session_data JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP
);

-- Achievements table
CREATE TABLE IF NOT EXISTS achievements (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    icon VARCHAR(100),
    requirement_type VARCHAR(50),
    requirement_value INTEGER,
    category VARCHAR(50) DEFAULT 'general',
    difficulty VARCHAR(20) DEFAULT 'medium',
    points INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- User achievements table
CREATE TABLE IF NOT EXISTS user_achievements (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    achievement_id BIGINT NOT NULL REFERENCES achievements(id) ON DELETE CASCADE,
    earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_data TEXT,
    UNIQUE(user_id, achievement_id)
);

-- Token blacklist table
CREATE TABLE IF NOT EXISTS tokens_blacklist (
    jti UUID PRIMARY KEY,
    user_id UUID,
    token_type VARCHAR(20) DEFAULT 'access',
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason VARCHAR(100) DEFAULT 'logout'
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_nickname ON users(nickname);
CREATE INDEX IF NOT EXISTS ix_users_created_at ON users(created_at);

CREATE INDEX IF NOT EXISTS ix_word_pairs_spanish ON word_pairs(spanish_word);
CREATE INDEX IF NOT EXISTS ix_word_pairs_russian ON word_pairs(russian_word);
CREATE INDEX IF NOT EXISTS ix_word_pairs_cefr_level ON word_pairs(cefr_level);
CREATE INDEX IF NOT EXISTS ix_word_pairs_frequency_rank ON word_pairs(frequency_rank);
CREATE INDEX IF NOT EXISTS ix_word_pairs_is_active ON word_pairs(is_active);
CREATE INDEX IF NOT EXISTS ix_word_pairs_tags ON word_pairs USING GIN(tags);

CREATE INDEX IF NOT EXISTS ix_user_cards_user_id ON user_cards(user_id);
CREATE INDEX IF NOT EXISTS ix_user_cards_due_date ON user_cards(due_date);
CREATE INDEX IF NOT EXISTS ix_user_cards_user_due ON user_cards(user_id, due_date);

CREATE INDEX IF NOT EXISTS ix_reviews_user_id ON reviews(user_id);
CREATE INDEX IF NOT EXISTS ix_reviews_reviewed_at ON reviews(reviewed_at);
CREATE INDEX IF NOT EXISTS ix_reviews_user_date ON reviews(user_id, reviewed_at);

CREATE INDEX IF NOT EXISTS ix_tokens_blacklist_expires ON tokens_blacklist(expires_at);
CREATE INDEX IF NOT EXISTS ix_tokens_blacklist_jti ON tokens_blacklist(jti);

CREATE INDEX IF NOT EXISTS ix_achievements_code ON achievements(code);
CREATE INDEX IF NOT EXISTS ix_user_achievements_user ON user_achievements(user_id);
CREATE INDEX IF NOT EXISTS ix_user_achievements_earned ON user_achievements(user_id, earned_at);

-- Create partial index for due cards (performance optimization)
CREATE INDEX IF NOT EXISTS ix_user_cards_due_now 
ON user_cards(user_id, due_date) 
WHERE due_date <= CURRENT_TIMESTAMP AND is_suspended = false;

-- Update triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_word_pairs_updated_at BEFORE UPDATE ON word_pairs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_cards_updated_at BEFORE UPDATE ON user_cards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_study_sessions_updated_at BEFORE UPDATE ON study_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'PairLingua database initialization completed successfully!';
END $$;
"""

# Seed data SQL
seed_data_sql = """-- PairLingua Seed Data
-- This script populates the database with initial data

-- Insert achievements
INSERT INTO achievements (code, title, description, icon, requirement_type, requirement_value, category, difficulty, points) VALUES
('first_review', 'First Steps', 'Complete your first review', '🌱', 'total_reviews', 1, 'beginner', 'easy', 10),
('perfect_day', 'Perfect Day', 'Get all reviews correct in a session of 5+ cards', '⭐', 'perfect_session', 5, 'accuracy', 'medium', 50),
('streak_3', '3-Day Streak', 'Study for 3 consecutive days', '🔥', 'streak', 3, 'consistency', 'easy', 30),
('streak_7', 'Week Warrior', 'Study for 7 consecutive days', '💪', 'streak', 7, 'consistency', 'medium', 100),
('streak_30', 'Monthly Master', 'Study for 30 consecutive days', '👑', 'streak', 30, 'consistency', 'hard', 500),
('reviews_100', 'Century Club', 'Complete 100 reviews', '💯', 'total_reviews', 100, 'milestone', 'medium', 200),
('reviews_1000', 'Review Master', 'Complete 1000 reviews', '🏆', 'total_reviews', 1000, 'milestone', 'hard', 1000),
('accuracy_80', 'Accurate Learner', 'Maintain 80% accuracy over 50+ reviews', '🎯', 'accuracy_milestone', 80, 'accuracy', 'medium', 150),
('accuracy_90', 'Precision Master', 'Maintain 90% accuracy over 100+ reviews', '🔍', 'accuracy_milestone', 90, 'accuracy', 'hard', 300),
('a1_master', 'A1 Graduate', 'Master all A1 level words', '🎓', 'level_completion', 1, 'progress', 'easy', 100),
('a2_master', 'A2 Graduate', 'Master all A2 level words', '🎓', 'level_completion', 2, 'progress', 'medium', 200),
('speed_demon', 'Speed Demon', 'Average response time under 2 seconds for 50+ reviews', '⚡', 'speed_milestone', 2000, 'performance', 'medium', 100),
('early_bird', 'Early Bird', 'Complete reviews before 8 AM', '🐦', 'time_based', 8, 'special', 'easy', 50),
('night_owl', 'Night Owl', 'Complete reviews after 10 PM', '🦉', 'time_based', 22, 'special', 'easy', 50),
('weekend_warrior', 'Weekend Warrior', 'Study on both Saturday and Sunday', '🏖️', 'weekend_study', 2, 'consistency', 'easy', 25)
ON CONFLICT (code) DO NOTHING;

-- Insert sample word pairs (Spanish-Russian A1-A2 level)
INSERT INTO word_pairs (spanish_word, russian_word, cefr_level, frequency_rank, tags, examples) VALUES
-- A1 Level - Most Common Words
('hola', 'привет', 'A1', 1, ARRAY['greeting', 'common'], '[{"es": "¡Hola! ¿Cómo estás?", "ru": "Привет! Как дела?"}]'),
('adiós', 'пока', 'A1', 2, ARRAY['greeting', 'common'], '[{"es": "Adiós, hasta mañana.", "ru": "Пока, до завтра."}]'),
('gracias', 'спасибо', 'A1', 3, ARRAY['politeness', 'common'], '[{"es": "Gracias por tu ayuda.", "ru": "Спасибо за твою помощь."}]'),
('por favor', 'пожалуйста', 'A1', 4, ARRAY['politeness', 'common'], '[{"es": "¿Puedes ayudarme, por favor?", "ru": "Можешь помочь мне, пожалуйста?"}]'),
('sí', 'да', 'A1', 5, ARRAY['common', 'response'], '[{"es": "Sí, me gusta mucho.", "ru": "Да, мне очень нравится."}]'),
('no', 'нет', 'A1', 6, ARRAY['common', 'response'], '[{"es": "No, no tengo tiempo.", "ru": "Нет, у меня нет времени."}]'),

-- Family and People
('familia', 'семья', 'A1', 10, ARRAY['family', 'people'], '[{"es": "Mi familia es muy grande.", "ru": "Моя семья очень большая."}]'),
('madre', 'мать', 'A1', 11, ARRAY['family', 'people'], '[{"es": "Mi madre cocina muy bien.", "ru": "Моя мать очень хорошо готовит."}]'),
('padre', 'отец', 'A1', 12, ARRAY['family', 'people'], '[{"es": "Mi padre trabaja en una oficina.", "ru": "Мой отец работает в офисе."}]'),
('hijo', 'сын', 'A1', 13, ARRAY['family', 'people'], '[{"es": "Mi hijo tiene cinco años.", "ru": "Моему сыну пять лет."}]'),
('hija', 'дочь', 'A1', 14, ARRAY['family', 'people'], '[{"es": "Mi hija estudia medicina.", "ru": "Моя дочь изучает медицину."}]'),
('hermano', 'брат', 'A1', 15, ARRAY['family', 'people'], '[{"es": "Mi hermano vive en Madrid.", "ru": "Мой брат живёт в Мадриде."}]'),
('hermana', 'сестра', 'A1', 16, ARRAY['family', 'people'], '[{"es": "Mi hermana es doctora.", "ru": "Моя сестра врач."}]'),

-- Numbers
('uno', 'один', 'A1', 20, ARRAY['numbers'], '[{"es": "Tengo un hermano.", "ru": "У меня один брат."}]'),
('dos', 'два', 'A1', 21, ARRAY['numbers'], '[{"es": "Dos cafés, por favor.", "ru": "Два кофе, пожалуйста."}]'),
('tres', 'три', 'A1', 22, ARRAY['numbers'], '[{"es": "Son las tres de la tarde.", "ru": "Сейчас три часа дня."}]'),
('cuatro', 'четыре', 'A1', 23, ARRAY['numbers'], '[{"es": "Tengo cuatro hermanos.", "ru": "У меня четыре брата."}]'),
('cinco', 'пять', 'A1', 24, ARRAY['numbers'], '[{"es": "Cinco euros, por favor.", "ru": "Пять евро, пожалуйста."}]'),

-- Colors
('rojo', 'красный', 'A1', 30, ARRAY['colors'], '[{"es": "Me gusta el vestido rojo.", "ru": "Мне нравится красное платье."}]'),
('azul', 'синий', 'A1', 31, ARRAY['colors'], '[{"es": "El cielo está azul.", "ru": "Небо синее."}]'),
('verde', 'зелёный', 'A1', 32, ARRAY['colors'], '[{"es": "Las hojas son verdes.", "ru": "Листья зелёные."}]'),
('amarillo', 'жёлтый', 'A1', 33, ARRAY['colors'], '[{"es": "El sol es amarillo.", "ru": "Солнце жёлтое."}]'),
('blanco', 'белый', 'A1', 34, ARRAY['colors'], '[{"es": "La nieve es blanca.", "ru": "Снег белый."}]'),
('negro', 'чёрный', 'A1', 35, ARRAY['colors'], '[{"es": "Mi gato es negro.", "ru": "Мой кот чёрный."}]'),

-- Food and Drink
('agua', 'вода', 'A1', 40, ARRAY['food', 'drink'], '[{"es": "Quiero un vaso de agua.", "ru": "Я хочу стакан воды."}]'),
('café', 'кофе', 'A1', 41, ARRAY['food', 'drink'], '[{"es": "Me gusta el café con leche.", "ru": "Я люблю кофе с молоком."}]'),
('té', 'чай', 'A1', 42, ARRAY['food', 'drink'], '[{"es": "¿Quieres té o café?", "ru": "Хочешь чай или кофе?"}]'),
('pan', 'хлеб', 'A1', 43, ARRAY['food'], '[{"es": "Compro pan en la panadería.", "ru": "Я покупаю хлеб в пекарне."}]'),
('leche', 'молоко', 'A1', 44, ARRAY['food', 'drink'], '[{"es": "Los niños beben mucha leche.", "ru": "Дети пьют много молока."}]'),
('carne', 'мясо', 'A1', 45, ARRAY['food'], '[{"es": "No como carne los viernes.", "ru": "Я не ем мясо по пятницам."}]'),

-- A2 Level Words
('conocer', 'знать', 'A2', 100, ARRAY['verb', 'common'], '[{"es": "Quiero conocer tu familia.", "ru": "Я хочу познакомиться с твоей семьёй."}]'),
('entender', 'понимать', 'A2', 101, ARRAY['verb', 'mental'], '[{"es": "No entiendo el problema.", "ru": "Я не понимаю проблему."}]'),
('explicar', 'объяснить', 'A2', 102, ARRAY['verb', 'communication'], '[{"es": "¿Puedes explicar esto?", "ru": "Можешь это объяснить?"}]'),
('olvidar', 'забыть', 'A2', 103, ARRAY['verb', 'mental'], '[{"es": "Siempre olvido las llaves.", "ru": "Я всегда забываю ключи."}]'),
('recordar', 'помнить', 'A2', 104, ARRAY['verb', 'mental'], '[{"es": "Recuerdo nuestra primera cita.", "ru": "Я помню наше первое свидание."}]'),
('preguntar', 'спрашивать', 'A2', 105, ARRAY['verb', 'communication'], '[{"es": "Voy a preguntar el precio.", "ru": "Я спрошу цену."}]'),
('responder', 'отвечать', 'A2', 106, ARRAY['verb', 'communication'], '[{"es": "No sé cómo responder.", "ru": "Я не знаю, как ответить."}]'),

-- Emotions and States
('feliz', 'счастливый', 'A2', 110, ARRAY['emotion', 'adjective'], '[{"es": "Estoy muy feliz hoy.", "ru": "Я очень счастлив сегодня."}]'),
('triste', 'грустный', 'A2', 111, ARRAY['emotion', 'adjective'], '[{"es": "¿Por qué estás triste?", "ru": "Почему ты грустный?"}]'),
('cansado', 'усталый', 'A2', 112, ARRAY['emotion', 'adjective'], '[{"es": "Estoy muy cansado.", "ru": "Я очень устал."}]'),
('enfermo', 'больной', 'A2', 113, ARRAY['health', 'adjective'], '[{"es": "Mi hijo está enfermo.", "ru": "Мой сын болен."}]'),
('nervioso', 'нервный', 'A2', 114, ARRAY['emotion', 'adjective'], '[{"es": "Estoy nervioso por el examen.", "ru": "Я нервничаю из-за экзамена."}]'),

-- Time and Dates
('mañana', 'утро', 'A2', 120, ARRAY['time'], '[{"es": "Por la mañana bebo café.", "ru": "Утром я пью кофе."}]'),
('tarde', 'вечер', 'A2', 121, ARRAY['time'], '[{"es": "Por la tarde estudio español.", "ru": "Вечером я изучаю испанский."}]'),
('noche', 'ночь', 'A2', 122, ARRAY['time'], '[{"es": "Buenas noches y dulces sueños.", "ru": "Спокойной ночи и сладких снов."}]'),
('semana', 'неделя', 'A2', 123, ARRAY['time'], '[{"es": "La próxima semana tengo vacaciones.", "ru": "На следующей неделе у меня отпуск."}]'),
('mes', 'месяц', 'A2', 124, ARRAY['time'], '[{"es": "Este mes hace mucho frío.", "ru": "В этом месяце очень холодно."}]'),
('año', 'год', 'A2', 125, ARRAY['time'], '[{"es": "El próximo año voy a España.", "ru": "В следующем году я поеду в Испанию."}]'),

-- Weather
('sol', 'солнце', 'A2', 130, ARRAY['weather', 'nature'], '[{"es": "Hoy hay mucho sol.", "ru": "Сегодня много солнца."}]'),
('lluvia', 'дождь', 'A2', 131, ARRAY['weather', 'nature'], '[{"es": "Me gusta caminar bajo la lluvia.", "ru": "Мне нравится гулять под дождём."}]'),
('viento', 'ветер', 'A2', 132, ARRAY['weather', 'nature'], '[{"es": "Hace mucho viento hoy.", "ru": "Сегодня очень ветрено."}]'),
('frío', 'холодный', 'A2', 133, ARRAY['weather', 'adjective'], '[{"es": "En invierno hace mucho frío.", "ru": "Зимой очень холодно."}]'),
('calor', 'жара', 'A2', 134, ARRAY['weather'], '[{"es": "En verano hace mucho calor.", "ru": "Летом очень жарко."}]')

ON CONFLICT (spanish_word, russian_word) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'PairLingua seed data inserted successfully!';
    RAISE NOTICE 'Inserted % achievements', (SELECT COUNT(*) FROM achievements);
    RAISE NOTICE 'Inserted % word pairs', (SELECT COUNT(*) FROM word_pairs);
END $$;
"""

# Start script
start_script = """#!/bin/bash

# PairLingua Application Start Script
set -e

echo "🚀 Starting PairLingua Application..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

echo "🔧 Environment: $ENVIRONMENT"

# Wait for services to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until PGPASSWORD=$DB_PASSWORD psql -h "localhost" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; do
    >&2 echo "PostgreSQL is unavailable - sleeping"
    sleep 1
done
echo "✅ PostgreSQL is ready!"

echo "⏳ Waiting for Redis to be ready..."
until redis-cli -h localhost -p 6379 -a "$REDIS_PASSWORD" ping > /dev/null 2>&1; do
    >&2 echo "Redis is unavailable - sleeping"
    sleep 1
done
echo "✅ Redis is ready!"

# Run database migrations
echo "🗄️ Running database migrations..."
cd backend
alembic upgrade head
cd ..

echo "🎉 PairLingua is ready!"
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/api/v1/health"
echo ""
echo "🛑 To stop all services: docker-compose down"
echo "📋 To view logs: docker-compose logs -f"
"""

# Записываем файлы
with open("pairlingua/backend/alembic.ini", "w") as f:
    f.write(alembic_ini)

with open("pairlingua/backend/alembic/env.py", "w") as f:
    f.write(alembic_env)

with open("pairlingua/backend/alembic/script.py.mako", "w") as f:
    f.write(alembic_script)

with open("pairlingua/scripts/init-db.sql", "w") as f:
    f.write(init_db_sql)

with open("pairlingua/scripts/seed-data.sql", "w", encoding="utf-8") as f:
    f.write(seed_data_sql)

with open("pairlingua/scripts/start.sh", "w" ,encoding="utf-8") as f:
    f.write(start_script)

# Сделать скрипт исполняемым
import os
os.chmod("pairlingua/scripts/start.sh", 0o755)

print("✅ Database файлы созданы")
print("🗃️ Alembic миграции настроены")
print("📊 SQL скрипты для инициализации и seed данных")
print("🚀 Start скрипт для быстрого запуска")