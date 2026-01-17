from .base import *
import dj_database_url

# Security: Disable DEBUG in production
DEBUG = False

# Render deployment hostname
ALLOWED_HOSTS = [
    os.getenv("RENDER_EXTERNAL_HOSTNAME", "localhost"),
    "localhost",
    "127.0.0.1",
]

# PostgreSQL via dj-database-url (Render FREE Plan)
DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv("DATABASE_URL", "sqlite:///db.sqlite3"),
        conn_max_age=0,  # Close connections immediately on Free Plan
        conn_health_checks=False,  # Disable health checks to save connections
    )
}

# Security: Enforce HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Static files are served by WhiteNoise (already configured in base.py)
STATIC_ROOT = BASE_DIR / "staticfiles"

# Optimization: Reduce verbosity in logs to minimize I/O on Free Plan
LOGGING['loggers']['django']['level'] = 'WARNING'
LOGGING['loggers']['apps']['level'] = 'INFO'

