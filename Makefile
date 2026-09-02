.PHONY: dev test lint backend-test frontend-test migrate

dev:
	docker compose up --build

test: backend-test frontend-test

backend-test:
	cd backend && python -m pytest -q

frontend-test:
	cd frontend && npm test -- --run

lint:
	cd backend && python -m ruff check . && python -m mypy app
	cd frontend && npm run lint || true

migrate:
	cd backend && python -m alembic upgrade head
