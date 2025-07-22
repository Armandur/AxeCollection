#!/bin/bash

# Backup script for AxeCollection
# Creates timestamped backups of database, media files, and logs

set -e

# Create backups directory if it doesn't exist
mkdir -p ./backups

# Get current timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "Starting backup at $(date)..."

# Backup database
echo "Backing up database..."
cp ./data/db.sqlite3 "./backups/db_${TIMESTAMP}.sqlite3"
echo "Database backed up to: ./backups/db_${TIMESTAMP}.sqlite3"

# Backup media files
echo "Backing up media files..."
if [ -d "./media" ] && [ "$(ls -A ./media)" ]; then
    tar -czf "./backups/media_${TIMESTAMP}.tar.gz" -C ./media .
    echo "Media files backed up to: ./backups/media_${TIMESTAMP}.tar.gz"
else
    echo "No media files to backup"
    touch "./backups/media_${TIMESTAMP}.tar.gz"
fi

# Backup logs
echo "Backing up logs..."
if [ -d "./logs" ] && [ "$(ls -A ./logs)" ]; then
    tar -czf "./backups/logs_${TIMESTAMP}.tar.gz" -C ./logs .
    echo "Logs backed up to: ./backups/logs_${TIMESTAMP}.tar.gz"
else
    echo "No logs to backup"
    touch "./backups/logs_${TIMESTAMP}.tar.gz"
fi

# Clean up old backups (keep last 7 days)
echo "Cleaning up old backups..."
find ./backups -name "*.sqlite3" -mtime +7 -delete
find ./backups -name "*.tar.gz" -mtime +7 -delete

# Show created files
echo "Files created:"
ls -la "./backups/db_${TIMESTAMP}.sqlite3"
ls -la "./backups/media_${TIMESTAMP}.tar.gz"
ls -la "./backups/logs_${TIMESTAMP}.tar.gz"

# Show backup directory size
echo "Backup directory size:"
du -sh ./backups

echo "Backup completed successfully!" 