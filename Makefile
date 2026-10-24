.PHONY: dev test lint backend-test backend-test-image frontend-test check-postgres-dialect migrate clean

dev:
	docker compose up --build

test: backend-test frontend-test

backend-test:
	cd backend && python -m pytest -q

backend-test-image:
	docker run --rm --network none storagegenie-backend:latest python -m pytest -q tests/test_signals.py::test_generated_codes_are_validated_and_bad_checksum_is_not_an_identifier tests/test_signals.py::test_ocr_has_text_boxes_and_mean_confidence

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
