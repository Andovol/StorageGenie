.PHONY: dev test lint backend-test frontend-test check-postgres-dialect migrate clean

dev:
	docker compose up --build

test: backend-test frontend-test

backend-test:
	cd backend && python -m pytest -q

frontend-test:
	cd frontend && npm test -- --run

lint:
	cd backend && python -m ruff check . && python -m mypy app
	cd frontend && npm run lint

check-postgres-dialect:
	cd backend && venv/bin/python -m pytest -q tests/test_postgres_dialect.py

migrate:
	cd backend && python -m alembic upgrade head

clean:
	powershell -NoProfile -Command "Get-ChildItem -Path '.' -Recurse -Force -Directory -Include '__pycache__','.mypy_cache','.ruff_cache','.pytest_cache' -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force; Remove-Item -Recurse -Force -LiteralPath 'frontend/dist' -ErrorAction SilentlyContinue"
