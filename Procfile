web: gunicorn murra.wsgi --log-file -
main_worker: python manage.py celery worker --beat --loglevel=info
