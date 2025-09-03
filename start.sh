#!/bin/bash

# AxeCollection Startup Script for Unraid
# This script handles database initialization and permission fixes

set -e

echo "🚀 AxeCollection Startup Script"
echo "================================"

# Fix permissions for all app directories (Unraid: nobody:users)
echo "🔐 Fixing permissions..."
# Create directories if they don't exist
mkdir -p /app/data/ /app/logs/ /app/media/ /app/backups/ /app/staticfiles/ /app/tmp/

chown -R nobody:users /app/data/
chmod -R 755 /app/data/
chown -R nobody:users /app/logs/
chmod -R 755 /app/logs/
chown -R nobody:users /app/media/
chmod -R 755 /app/media/
chown -R nobody:users /app/backups/
chmod -R 755 /app/backups/
chown -R nobody:users /app/staticfiles/
chmod -R 755 /app/staticfiles/
chown -R nobody:users /app/tmp/
chmod -R 1777 /app/tmp/

# Check if database exists
if [ ! -f "/app/data/db.sqlite3" ]; then
    echo "📊 Database not found. Initializing..."
    
    # Create database and run migrations
    cd /app
    python manage.py migrate
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
    
    # Check if DEMO_MODE is enabled
    if [ "$DEMO_MODE" = "true" ]; then
        echo "🎭 DEMO_MODE enabled - Generating test data..."
        python manage.py generate_test_data --clear
        echo "✅ Demo data generated successfully!"
    else
        # Create superuser if environment variables are set
        if [ ! -z "$DJANGO_SUPERUSER_USERNAME" ] && [ ! -z "$DJANGO_SUPERUSER_EMAIL" ] && [ ! -z "$DJANGO_SUPERUSER_PASSWORD" ]; then
            echo "👤 Creating superuser..."
            python manage.py createsuperuser --noinput
        else
            echo "⚠️  No superuser created. Set DJANGO_SUPERUSER_* environment variables to create one automatically."
        fi
        
        # Import CSV data if available
        if [ -f "/app/axes/management/csv_data/Yxa.csv" ]; then
            echo "📥 Importing CSV data..."
            python manage.py import_csv
        fi
    fi
    
    echo "✅ Database initialized successfully!"
else
    echo "📊 Database exists. Running migrations..."
    cd /app
    python manage.py migrate --plan | grep -q "No planned operations" || {
        echo "🔄 Running pending migrations..."
        python manage.py migrate
    }
    echo "📦 Collecting static files..."
    python manage.py collectstatic --noinput
    
    # Check if DEMO_MODE is enabled for existing database
    if [ "$DEMO_MODE" = "true" ]; then
        echo "🎭 DEMO_MODE enabled - Regenerating test data..."
        python manage.py generate_test_data --clear
        echo "✅ Demo data regenerated successfully!"
    fi
    
    echo "✅ Database ready!"
fi

# Fix database file permissions specifically
if [ -f "/app/data/db.sqlite3" ]; then
    chown nobody:users /app/data/db.sqlite3
    chmod 664 /app/data/db.sqlite3
fi

echo "🎉 Startup script completed!"
echo "================================"

# Start supervisord
echo "🚀 Starting supervisord..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf 