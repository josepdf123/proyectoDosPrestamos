web: gunicorn config.wsgi:application
release: python manage.py migrate && python create_users.py