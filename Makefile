.PHONY: dev dev-backend dev-frontend install install-backend install-frontend \
        test lint format seed docker-build docker-up docker-down docker-logs clean

# === Development ===

dev: dev-backend dev-frontend

dev-backend:
	cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

dev-frontend:
	cd frontend && npx next dev --port 3000

# === Installation ===

install: install-backend install-frontend

install-backend:
	pip install -e "backend/[dev]"

install-frontend:
	cd frontend && npm install

# === Quality ===

lint:
	ruff check backend/
	ruff format --check backend/

format:
	ruff format backend/

test:
	cd backend && python -m pytest

# === Demo Data ===

seed:
	cd backend && python -m app.seed

# === Docker ===

docker-build:
	docker compose build

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

# === Cleanup ===

clean:
	rm -rf backend/__pycache__ backend/**/__pycache__
	rm -rf frontend/.next frontend/node_modules
	rm -f data/*.db
