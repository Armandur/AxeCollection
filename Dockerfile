# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=AxeCollection.settings_production
ENV DEMO_MODE=false

# Set work directory
WORKDIR /app

# Install system dependencies including nginx and supervisor
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libjpeg-dev \
        libpng-dev \
        libwebp-dev \
        zlib1g-dev \
        nginx \
        supervisor \
        curl \
    && rm -rf /var/lib/apt/lists/* \
    && ln -sf /usr/sbin/nginx /usr/bin/nginx

# Modify existing nobody user to have UID 99 and GID 100 for Unraid compatibility
RUN usermod -u 99 nobody && groupmod -g 100 users

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy project
COPY . .

# Copy backup script
COPY backup.sh ./backup.sh

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/media /app/staticfiles /var/log/nginx /var/log/supervisor

# Collect static files
RUN python manage.py collectstatic --noinput

# Configure nginx
COPY nginx.integrated.conf /etc/nginx/sites-available/default
RUN ln -sf /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

# Configure supervisor
COPY supervisor.unraid.conf /etc/supervisor/conf.d/supervisord.conf

# Create startup script for database initialization and permissions
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh
# Fix Windows line endings if present
RUN sed -i 's/\r$//' /app/start.sh

# Fix permissions for Unraid (nobody:users - UID 99, GID 100)
RUN chown -R nobody:users /app
RUN chown -R nobody:users /var/log/supervisor

# Fix nginx and supervisor permissions (nginx needs root)
RUN mkdir -p /var/log/nginx /var/cache/nginx /var/run /var/log/supervisor
RUN chown -R root:root /var/log/nginx /var/cache/nginx /var/run
RUN chmod -R 755 /var/log/nginx /var/cache/nginx /var/run
RUN chown -R root:root /var/log/supervisor
RUN chmod -R 755 /var/log/supervisor

# Fix nginx body directory permissions for uploads
RUN mkdir -p /var/lib/nginx/body
RUN chown -R www-data:www-data /var/lib/nginx/body
RUN chmod -R 700 /var/lib/nginx/body

# Fix app directory permissions for nobody user
RUN chown -R nobody:users /app/logs
RUN chmod -R 755 /app/logs

# Fix /tmp permissions for Gunicorn
RUN chown -R nobody:users /tmp
RUN chmod -R 1777 /tmp

# Expose port 80 for nginx
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health/ || exit 1

# Run supervisor to manage both nginx and gunicorn
CMD ["/app/start.sh"] 