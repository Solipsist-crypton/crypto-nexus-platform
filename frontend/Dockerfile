# frontend/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Копіюємо файли залежностей
COPY package*.json ./
COPY yarn.lock ./

# Встановлюємо залежності
RUN npm ci --only=production

# Копіюємо всі файли
COPY . .

# Збираємо додаток
RUN npm run build

# Виробничий сервер
FROM nginx:alpine

# Копіюємо збірку
COPY --from=builder /app/dist /usr/share/nginx/html

# Копіюємо конфігурацію nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Відкриваємо порт
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]