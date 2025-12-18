COMPOSE := docker compose

.PHONY: build lint fmt test run up down logs shell

lint:
	$(COMPOSE) run --rm --no-deps bot uv run ruff check .

fmt:
	$(COMPOSE) run --rm --no-deps bot uv run ruff format .

test:
	$(COMPOSE) run --rm --no-deps bot uv run pytest

run:
	$(COMPOSE) up -d bot

build:
	$(COMPOSE) build

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f bot

shell:
	$(COMPOSE) run --rm bot /bin/sh

