web: python manage.py migrate --no-input && gunicorn citysense.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 1 --worker-class sync --max-requests 100 --max-requests-jitter 10 --timeout 30
