# Migrebot (MVP)

Телеграм-бот для дневника головной боли (MVP scaffold).

## Быстрый старт (локально)
1. Установите uv: `pip install uv`
2. Создайте `.env` по образцу:
   ```
   BOT_TOKEN=changeme
   POSTGRES_USER=migrebot
   POSTGRES_PASSWORD=migrebot
   POSTGRES_DB=migrebot
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   REDIS_URL=redis://localhost:6379/0
   LOG_LEVEL=INFO
   ```
3. Установите зависимости: `make sync`
4. Запуск бота: `make run`

## Docker Compose
```
make up      # поднимет bot + postgres + redis
make logs    # логи бота
make down    # остановка
```

## Качество
- `make lint` — ruff check
- `make fmt` — ruff format
- `make test` — pytest
