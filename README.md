# Migrebot (MVP)

Телеграм-бот для дневника головной боли (MVP scaffold).

## Быстрый старт (локально)
1. Установите uv: `pip install uv`
2. Скопируйте `env.example` в `.env` и задайте `BOT_TOKEN`.
3. Установите зависимости: `make sync`
4. Примените миграции: `make migrate`
5. Запуск бота: `make run`

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
