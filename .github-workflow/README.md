# Backend Hosting Guide

> Цей гайд пояснює як захостити бекенд на різних фреймворках та як об'єднати їх в одну систему через Docker Compose + Nginx.

---

# FastAPI

FastAPI — сучасний Python-фреймворк для побудови REST API. Він надзвичайно швидкий, підтримує async/await і автоматично генерує документацію Swagger.

## Запуск локально через Docker

```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```txt
# requirements.txt
fastapi
uvicorn
```

```python
# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"framework": "FastAPI", "status": "running"}
```

```bash
# Збірка та запуск
docker build -t fastapi-app .
docker run -d -p 8000:8000 fastapi-app
```

## Деплой проекту

### Так як в мене немає коштів для хорошо хостинга як приклад будемо використовувати бесплатний хостинг Render при наявності коштів рекомендується використовувати AWS

1. Запушити проєкт на GitHub
2. Зайти на [render.com](https://render.com) → **New Web Service**
3. Підключити репозиторій
4. Вказати команду запуску:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. Render автоматично визначить Python і встановить залежності з `requirements.txt`


---

# phpMyAdmin

phpMyAdmin — веб-інтерфейс для керування MySQL/MariaDB базами даних. Зазвичай розгортається разом із базою.

## Запуск локально через Docker

```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: mydb
    ports:
      - "3306:3306"
    volumes:
      - db_data:/var/lib/mysql

  phpmyadmin:
    image: phpmyadmin:latest
    ports:
      - "8080:80"
    environment:
      PMA_HOST: db
      PMA_PORT: 3306
    depends_on:
      - db

volumes:
  db_data:
```

```bash
# Запуск
docker compose up -d

# phpMyAdmin буде доступний на http://localhost:8080
# Логін: root | Пароль: rootpassword
```

## Деплой на Render

phpMyAdmin не деплоїться напряму на Render як окремий сервіс, але можна:

1. Створити **MySQL** базу через **Railway** або **PlanetScale** (мають безкоштовні тіри)
2. Використовувати вбудований веб-інтерфейс Railway або підключитись через TablePlus/DBeaver
3. Або задеплоїти phpMyAdmin як **Docker** сервіс на Render:
   - Обрати **New Web Service → Deploy from Docker**
   - Вказати image: `phpmyadmin/phpmyadmin`
   - Додати env змінні: `PMA_HOST`, `PMA_USER`, `PMA_PASSWORD`



---

# Node.js

Node.js дозволяє запускати JavaScript на сервері. Популярний для REST API через фреймворки Express, Fastify або NestJS.

## Запуск локально через Docker

```dockerfile
# Dockerfile
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["node", "server.js"]
```

```javascript
// server.js
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.json({ framework: 'Node.js + Express', status: 'running' });
});

app.listen(3000, '0.0.0.0', () => {
  console.log('Server running on port 3000');
});
```

```json
// package.json
{
  "name": "node-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.0"
  }
}
```

```bash
# Збірка та запуск
docker build -t node-app .
docker run -d -p 3000:3000 node-app
```

## Деплой на Render

1. Запушити на GitHub
2. **New Web Service** → підключити репо
3. Render автоматично визначить Node.js
4. Start Command:
   ```
   node server.js
   ```
5. Або якщо є `npm start` в `package.json` — Render викличе його сам



---

# Spring Boot

Spring Boot — потужний Java-фреймворк для enterprise-рівня бекенду. Має вбудований сервер (Tomcat), IoC-контейнер і величезну екосистему.

## Запуск локально через Docker

```dockerfile
# Dockerfile — multistage build
FROM maven:3.9-eclipse-temurin-21 AS build

WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn package -DskipTests

FROM eclipse-temurin:21-jre-alpine

WORKDIR /app
COPY --from=build /app/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
```

```bash
# Збірка та запуск
docker build -t spring-app .
docker run -d -p 8080:8080 spring-app
```

```java
// src/main/java/com/example/demo/DemoController.java
@RestController
public class DemoController {
    @GetMapping("/")
    public Map<String, String> root() {
        return Map.of("framework", "Spring Boot", "status", "running");
    }
}
```

## Деплой на Render

1. Переконатись що є `Dockerfile` в корені репо
2. **New Web Service → Docker**
3. Render збере образ і запустить контейнер
4. У **Environment Variables** вказати:
   ```
   SPRING_PROFILES_ACTIVE=prod
   SERVER_PORT=8080
   ```
5. Health check: `/actuator/health` (якщо підключений Spring Actuator)



---

# .NET

ASP.NET Core — крос-платформний фреймворк від Microsoft для побудови API та веб-додатків. Працює на Linux, що робить його ідеальним для Docker.

## Запуск локально через Docker

```dockerfile
# Dockerfile — multistage build
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build

WORKDIR /src
COPY *.csproj .
RUN dotnet restore

COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0

WORKDIR /app
COPY --from=build /app/publish .

EXPOSE 8080

ENV ASPNETCORE_URLS=http://+:8080

ENTRYPOINT ["dotnet", "MyApi.dll"]
```

```csharp
// Program.cs
var builder = WebApplication.CreateBuilder(args);
var app = builder.Build();

app.MapGet("/", () => new { framework = ".NET 8", status = "running" });

app.Run();
```

```bash
# Збірка та запуск
docker build -t dotnet-app .
docker run -d -p 8080:8080 dotnet-app
```

## Деплой на Render

1. Додати `Dockerfile` в корінь репо
2. **New Web Service → Docker**
3. Вказати порт `8080` (або через `ASPNETCORE_URLS`)
4. Render підхопить Dockerfile і задеплоїть автоматично



---

# Об'єднання беку

Найкращий варіант — запустити всі фреймворки через **Docker Compose** за одним **Nginx reverse proxy**. Це дозволяє мати один публічний порт (80/443) і роутити трафік до потрібного сервісу.

```
Internet → :80 (Nginx)
              ├── /api/fastapi/  →  FastAPI      :8001
              ├── /api/node/     →  Node.js      :8002
              ├── /api/spring/   →  Spring Boot  :8003
              ├── /api/dotnet/   →  .NET         :8004
              └── /phpmyadmin/   →  phpMyAdmin   :8005
```

## docker-compose.yml

```yaml
version: '3.8'

services:

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - fastapi
      - node
      - spring
      - dotnet
      - phpmyadmin
    restart: always

  fastapi:
    build: ./fastapi
    expose:
      - "8000"
    restart: always

  node:
    build: ./node
    expose:
      - "3000"
    restart: always

  spring:
    build: ./spring
    expose:
      - "8080"
    restart: always

  dotnet:
    build: ./dotnet
    expose:
      - "8080"
    restart: always

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: mydb
    volumes:
      - db_data:/var/lib/mysql
    restart: always

  phpmyadmin:
    image: phpmyadmin:latest
    expose:
      - "80"
    environment:
      PMA_HOST: db
    depends_on:
      - db
    restart: always

volumes:
  db_data:
```

## nginx/nginx.conf

```nginx
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;

        location /api/fastapi/ {
            proxy_pass http://fastapi:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /api/node/ {
            proxy_pass http://node:3000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /api/spring/ {
            proxy_pass http://spring:8080/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /api/dotnet/ {
            proxy_pass http://dotnet:8080/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        location /phpmyadmin/ {
            proxy_pass http://phpmyadmin:80/;
            proxy_set_header Host $host;
        }
    }
}
```

## .env файл

```env
MYSQL_ROOT_PASSWORD=supersecretpassword
```

## Запуск

```bash
# Піднімаємо всі сервіси
docker compose up -d --build

# Перевірка статусу
docker compose ps

# Логи конкретного сервісу
docker compose logs -f spring

# Зупинка
docker compose down

---

## Деплой всього стека на VPS

Для повноцінного продакшн-деплою на VPS (Hetzner, DigitalOcean):

```bash
# 1. Клонуємо репо на сервер
git clone https://github.com/yourname/backend-showcase.git
cd backend-showcase

# 2. Створюємо .env
echo "MYSQL_ROOT_PASSWORD=supersecretpassword" > .env

# 3. Запускаємо
docker compose up -d --build

# 4. Налаштовуємо SSL через Let's Encrypt (опціонально)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

> 💡 Цей підхід демонструє реальні DevOps-скіли: контейнеризація, reverse proxy, multi-service оркестрація, environment variables та потенційно CI/CD через GitHub Actions.
