sleep 5

alembic revision --autogenerate
alembic upgrade head

python /usr/src/app/pre_start.py

gunicorn app.main:app --host 0.0.0.0 --port 8000 -w 4 uvicorn.workers.UvicornWorker