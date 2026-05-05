# Дисклеймер

> README був написаний за допомогою використання штучного інтелекту, проте був змінений в моментах де інформація була донесена не так як я пояснив ШІ в промпті




# Backend Hosting Guide

> Гайд охоплює запуск бекенду на різних фреймворках через Docker, деплой на Render, об'єднання сервісів через Docker Compose + Nginx, CI/CD через GitHub Actions та оркестрацію через Kubernetes. Прошу звернути уваги що докерфайли для .NET, phpMyAdmin, Java SpringBoot, Nodejs(Express, Next) не були створені, так як немає програміста якій міг би писати на цих інструментах, але саме розуміння хостингу цих сервісів я маю.

---

# FastAPI

FastAPI — сучасний Python-фреймворк для побудови REST API. Підтримує async/await і автоматично генерує Swagger документацію.

## Запуск через Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --root-user-action=ignore

COPY . .

EXPOSE 3300

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3300"]
```

```bash
docker build -t fastapi-app:latest .
docker run -d -p 3300:3300 fastapi-app:latest
```

Swagger документація доступна на `http://localhost:3300/docs`

## Деплой проекту

### Для ролі бесплатного хостингу будем використовувати Render. При наявності фінансів рекомендується використовувати AWS.

### Кроки

1. Запушити проєкт на GitHub
2. Зайти на [render.com](https://render.com) → **New Web Service**
3. Підключити репозиторій
4. Вказати команду запуску:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Render автоматично визначить Python і встановить залежності з `requirements.txt`

---

### Сам Render використовує docker image як образ для хоста,проте він омбежений в ресурсах, немає такої кількості інструментів, та не дає виділити потрібні характеристики для сервера в вигляді:ОЗУ,ЦП,пам'яті, як AWS


# phpMyAdmin

phpMyAdmin — веб-інтерфейс для керування MySQL/MariaDB базами даних. Зазвичай розгортається разом із базою.

## Запуск через Docker

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
docker compose up -d

# phpMyAdmin буде доступний на http://localhost:8080
# Логін: root | Пароль: rootpassword
```

## Деплой на Render

phpMyAdmin не деплоїться напряму на Render як окремий сервіс, але можна:

1. Створити **MySQL** базу через **Railway** або **PlanetScale**
2. Використовувати вбудований веб-інтерфейс Railway або підключитись через TablePlus/DBeaver
3. Або задеплоїти phpMyAdmin як **Docker** сервіс на Render:
   - Обрати **New Web Service → Deploy from Docker**
   - Вказати image: `phpmyadmin/phpmyadmin`
   - Додати env змінні: `PMA_HOST`, `PMA_USER`, `PMA_PASSWORD`


---

# Node.js

Node.js дозволяє запускати JavaScript на сервері. Популярний для REST API через фреймворки Express, Fastify або NestJS.

## Запуск через Docker

```dockerfile
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
{
  "name": "node-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.0"
  }
}
```

```bash
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

---

# Spring Boot

Spring Boot — потужний Java-фреймворк для enterprise-рівня бекенду. Має вбудований сервер Tomcat, IoC-контейнер і величезну екосистему.

## Запуск через Docker

```dockerfile
# multistage build — образ виходить легшим без Maven
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

---

# .NET

ASP.NET Core — крос-платформний фреймворк від Microsoft для побудови API. Працює на Linux, що робить його ідеальним для Docker.

## Запуск через Docker

```dockerfile
# multistage build — зменшує образ з ~800MB до ~200MB
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

Запускаємо всі фреймворки через **Docker Compose** за одним **Nginx reverse proxy** — один публічний порт і роутинг до кожного сервісу.

```
Internet → :80 (Nginx)
              ├── /api/fastapi/  →  FastAPI      :3300
              ├── /api/node/     →  Node.js      :3000
              ├── /api/spring/   →  Spring Boot  :8080
              ├── /api/dotnet/   →  .NET         :8080
              └── /phpmyadmin/   →  phpMyAdmin   :80
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
      - "3300"
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
            proxy_pass http://fastapi:3300/;
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

### docker-compose в данному випадку використовується для оркестрації сервісів, тобто він об'єднує контейнери в одну мережу, а nginx в свою чергу працює як reverse-proxy.Він перенаправляє відповідні HTTP запити всередині Docker мережі



## .env

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
docker compose logs -f fastapi

# Зупинка
docker compose down
```

## Перевірка

```bash
curl http://localhost/api/fastapi/
curl http://localhost/api/node/
curl http://localhost/api/spring/
curl http://localhost/api/dotnet/
# phpMyAdmin: http://localhost/phpmyadmin/
```

---

# CI/CD

Автоматичний деплой через **GitHub Actions** — при кожному пуші в `main` сервер сам підтягує зміни і перезапускає Docker.

## .github/workflows/deploy.yml

```yaml
name: CI/CD Deploy

on:
  push:
    branches:
      - production

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Deploy to server via SSH
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd /opt/backend-showcase
            git pull origin main
            docker compose up -d --build
            docker image prune -f
```

## Налаштування secrets

Йди в репо → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Значення |
|---|---|
| `VPS_HOST` | IP адреса сервера |
| `VPS_USER` | юзер на сервері (`root` або `ubuntu`) |
| `VPS_SSH_KEY` | приватний SSH ключ (`cat ~/.ssh/id_rsa`) |



## Перший деплой вручну

```bash
git clone https://github.com/yourname/backend-showcase.git /opt/backend-showcase
cd /opt/backend-showcase
echo "MYSQL_ROOT_PASSWORD=supersecretpassword" > .env
docker compose up -d --build
```

Після цього кожен пуш в `main` деплоїться автоматично.


### CI/CD в данному випадку використовується для ssh підключення

---


# Kubernetes

Kubernetes автоматично підтримує задану кількість запущених контейнерів. Якщо один впав — одразу піднімає новий.



```bash

```

## k8s/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-deployment
  labels:
    app: backend
spec:
  replicas: 2                        # 2 контейнери завжди
  selector:
    matchLabels:
      app: backend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
        - name: backend
          image: fastapi-app:latest
          ports:
            - containerPort: 3300

          # Якщо не відповідає 3 рази — перезапускає контейнер
          livenessProbe:
            httpGet:
              path: /
              port: 3300
            initialDelaySeconds: 10
            periodSeconds: 5
            failureThreshold: 3

          # Перевірка готовності приймати трафік
          readinessProbe:
            httpGet:
              path: /
              port: 3300
            initialDelaySeconds: 5
            periodSeconds: 3

          resources:
            requests:
              memory: "64Mi"
              cpu: "100m"
            limits:
              memory: "128Mi"
              cpu: "250m"

      restartPolicy: Always

---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  selector:
    app: backend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3300
  type: LoadBalancer
```

## Запуск

```bash
kubectl apply -f k8s/deployment.yaml

# Перевірити що 2 поди запущені
kubectl get pods
```

## Тест авто-відновлення

```bash
# Вбити один под вручну
kubectl delete pod <pod-name>

# Спостерігати як Kubernetes піднімає новий
kubectl get pods -w
```

```
NAME                      READY   STATUS
backend-xxx-aaa           1/1     Running    ← живий
backend-xxx-bbb           1/1     Running    ← живий

backend-xxx-bbb           0/1     Terminating   ← вбили
backend-xxx-ccc           0/1     Pending       ← k8s піднімає новий
backend-xxx-ccc           1/1     Running       ← готовий
```

## Генерація deployment.yaml без написання вручну

```bash
kubectl create deployment backend \
  --image=fastapi-app:latest \
  --replicas=2 \
  --dry-run=client \
  -o yaml > k8s/deployment.yaml
```
