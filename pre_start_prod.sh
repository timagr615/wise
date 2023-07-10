sleep 5

alembic revision --autogenerate
alembic upgrade head

python /usr/src/app/pre_start.py

gunicorn app.main:app --bind 0.0.0.0:8000 -w 4 -k uvicorn.workers.UvicornWorker