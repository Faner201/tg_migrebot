COMPOSE := docker compose

.PHONY: build lint fmt test run up down logs shell venv sync migrate help

help: ## Показать доступные команды Make
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-12s %s\n", $$1, $$2}'

venv: ## Создать venv через uv
	uv venv

sync: venv ## Установить зависимости через uv sync
	uv sync

lint: ## Ruff check
	$(COMPOSE) run --rm --no-deps bot uv run ruff check .

fmt: ## Ruff format
	$(COMPOSE) run --rm --no-deps bot uv run ruff format .

test: ## Запустить pytest
	$(COMPOSE) run --rm --no-deps bot uv run pytest

run: ## Поднять все сервисы и бота (python -m app.main)
	$(COMPOSE) up -d

build: ## Собрать образы
	$(COMPOSE) build

up: ## Поднять все сервисы
	$(COMPOSE) up -d

down: ## Остановить все сервисы
	$(COMPOSE) down

logs: ## Логи бота
	$(COMPOSE) logs -f bot

shell: ## Shell внутри bot контейнера
	$(COMPOSE) run --rm bot /bin/sh

migrate: ## Применить alembic upgrade head
	$(COMPOSE) run --rm bot uv run alembic -c alembic.ini upgrade head

