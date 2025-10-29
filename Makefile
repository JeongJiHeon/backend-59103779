.PHONY: help install run test clean docker-up docker-down migrate

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make run          - Run development server"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make clean        - Clean cache and build files"
	@echo "  make docker-up    - Start Docker services"
	@echo "  make docker-down  - Stop Docker services"
	@echo "  make migrate      - Run database migrations"
	@echo "  make migration    - Create new migration"

install:
	pip install -r requirements.txt

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest -v

test-cov:
	pytest --cov=app --cov-report=html --cov-report=term

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .coverage htmlcov

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f api

migrate:
	alembic upgrade head

migration:
	@read -p "Enter migration message: " msg; \
	alembic revision --autogenerate -m "$$msg"

format:
	black app/ tests/
	isort app/ tests/

lint:
	flake8 app/ tests/
	mypy app/

dev-setup:
	cp .env.example .env
	make install
	make docker-up
	sleep 5
	make migrate
