API-сервис сокращения ссылок

Этот репозиторий содержит базовый API для сокращения ссылок, созданный с использованием FastAPI, PostgreSQL и Redis.

Быстрый старт (с Docker):

1. Соберите и запустите контейнеры:

```bash
docker-compose up --build
```

2. API будет доступен по адресу `http://localhost:8000`.

Эндпоинты:
- `POST /register` — body: `{ "username": "u", "password": "p" }` returns token
- `POST /login` — body: `{ "username": "u", "password": "p" }` returns token
- `POST /links/shorten` — нужна аутентификация (Bearer token). Body: `{ "original_url": "https://...", "custom_alias": "opt", "expires_at": "2026-03-20T12:00:00" }`
- `GET /{short_code}` — перенаправляет на оригинальный url
- `GET /links/{short_code}/stats` — статистика по алиасу
- `PUT /links/{short_code}` — обновление ссылки (только владелец)
- `DELETE /links/{short_code}` — удаление ссылки (только владелец)
- `GET /links/search?original_url=...` — поиск алиаса по оригинальному URL
