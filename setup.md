"""
.PHONY: install dev test clean migrate upgrade downgrade

install:
pip install -r requirements.txt

dev:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
pytest tests/ -v

test-cov:
pytest tests/ --cov=app --cov-report=html

clean:
find . -type f -name "\*.pyc" -delete
find . -type d -name "**pycache**" -delete

migrate:
alembic revision --autogenerate -m "$(message)"

upgrade:
alembic upgrade head

downgrade:
alembic downgrade -1

docker-build:
docker-compose build

docker-up:
docker-compose up -d

docker-down:
docker-compose down

docker-logs:
docker-compose logs -f

celery-worker:
celery -A app.core.celery_app worker --loglevel=info

celery-beat:
celery -A app.core.celery_app beat --loglevel=info

celery-flower:
celery -A app.core.celery_app flower --port=5555
"""
