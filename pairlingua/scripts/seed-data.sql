-- PairLingua Seed Data
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
