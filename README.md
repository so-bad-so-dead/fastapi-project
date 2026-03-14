API-сервис сокращения ссылок

Репозиторий содержит сервис сокращения ссылок на базе FastAPI, PostgreSQL и Redis.

1) Описание API

- POST /register
  - Регистрация пользователя.
  - Тело: JSON { "username": "user", "password": "pass" }
  - Ответ: { "access_token": "...", "token_type": "bearer" }

- POST /login
  - Логин существующего пользователя.
  - Тело: JSON { "username": "user", "password": "pass" }
  - Ответ: { "access_token": "...", "token_type": "bearer" }

- POST /links/shorten
  - Создание короткой ссылки.
  - Авторизация: необязательная (если передан Bearer токен, ссылка привязывается к пользователю).
  - Тело: JSON { "original_url": "https://...", "custom_alias": "opt" (опционально), "expires_at": "ISO-datetime" (опционально) }
  - Ответ: объект ссылки с `short_code`, `original_url`, `created_at`, `expires_at`, `clicks`.

- GET /{short_code}
  - Перенаправление на оригинальный URL (HTTP 307 Temporary Redirect).

- GET /links/{short_code}/stats
  - Статистика по ссылке: оригинальный URL, дата создания, число переходов, дата последнего использования, дата истечения.

- PUT /links/{short_code}
  - Обновление ссылки (только владелец). Тело: { "original_url": ..., "expires_at": ... }.

- DELETE /links/{short_code}
  - Удаление ссылки (только владелец).

- GET /links/search?original_url=...
  - Поиск ссылок по точному совпадению оригинального URL.

2) Примеры запросов (curl)

- Регистрация:
```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"pass123"}' \
  http://localhost:8000/register
```

- Логин:
```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"pass123"}' \
  http://localhost:8000/login
```

- Создать короткую ссылку (с токеном):
```bash
TOKEN="<ACCESS_TOKEN>"
curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{"original_url":"https://example.com","custom_alias":"myalias"}' \
  http://localhost:8000/links/shorten
```

- Создать анонимно (без токена):
```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"original_url":"https://example.com/anon"}' \
  http://localhost:8000/links/shorten
```

- Редирект:
```bash
curl -v http://localhost:8000/myalias
```

- Получить статистику:
```bash
curl -s http://localhost:8000/links/myalias/stats
```

- Обновить ссылку (владелец):
```bash
curl -s -X PUT -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" \
  -d '{"original_url":"https://example.com/new"}' \
  http://localhost:8000/links/myalias
```

- Удалить ссылку (владелец):
```bash
curl -s -X DELETE -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/links/myalias
```

3) Инструкция по запуску

Docker:

1. Установи Docker Desktop и запусти его.
2. В корне репозитория выполни:
```bash
docker-compose up --build
```
3. API будет доступен по http://localhost:8000. Swagger UI: http://localhost:8000/docs

Остановить:
```bash
docker-compose down (или `Ctrl + C` в том же терминале)
```

4) Описание БД

В проекте используются две основные таблицы (SQLAlchemy модели в `app/models.py`):

- `users`:
  - `id` (PK, integer)
  - `username` (string, unique)
  - `password_hash` (string)
  - `created_at` (datetime)

- `links`:
  - `id` (PK, integer)
  - `short_code` (string, unique) — короткий код
  - `original_url` (text) — оригинальный URL
  - `owner_id` (FK -> users.id, nullable) — владелец (если создан пользователем)
  - `created_at` (datetime)
  - `expires_at` (datetime, nullable)
  - `clicks` (integer)
  - `last_used_at` (datetime, nullable)
  - `custom_alias` (string, unique, nullable)