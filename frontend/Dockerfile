# Используем легкий Node.js образ
FROM node:20-alpine

# Рабочая директория внутри контейнера
WORKDIR /app

# Копируем package.json и package-lock.json для установки зависимостей
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем все остальные файлы проекта
COPY . .

# Экспонируем порт 5173 (Vite dev сервер)
EXPOSE 5173

# Запускаем Vite dev сервер
CMD ["npm", "run", "dev"]
