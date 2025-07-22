#!/bin/bash

# Backup script for AxeCollection
# Usage: ./backup.sh [backup_directory]

# Set backup directory
if [ -z "$1" ]; then
    BACKUP_DIR="./backups"
else
    BACKUP_DIR="$1"
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Get current timestamp
DATE=$(date +%Y%m%d_%H%M%S)

echo "Starting backup at $(date)..."

# Backup database
if [ -f "data/db.sqlite3" ]; then
    echo "Backing up database..."
    cp data/db.sqlite3 "$BACKUP_DIR/db_$DATE.sqlite3"
    echo "Database backed up to: $BACKUP_DIR/db_$DATE.sqlite3"
else
    echo "Warning: Database file not found at data/db.sqlite3"
fi

# Backup media files
if [ -d "media" ]; then
    echo "Backing up media files..."
    tar -czf "$BACKUP_DIR/media_$DATE.tar.gz" media/
    echo "Media files backed up to: $BACKUP_DIR/media_$DATE.tar.gz"
else
    echo "Warning: Media directory not found"
fi

# Backup logs
if [ -d "logs" ]; then
    echo "Backing up logs..."
    tar -czf "$BACKUP_DIR/logs_$DATE.tar.gz" logs/
    echo "Logs backed up to: $BACKUP_DIR/logs_$DATE.tar.gz"
fi

# Clean up old backups (keep last 7 days)
echo "Cleaning up old backups..."
find "$BACKUP_DIR" -name "db_*.sqlite3" -mtime +7 -delete
find "$BACKUP_DIR" -name "media_*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "logs_*.tar.gz" -mtime +7 -delete

# Show backup summary
echo ""
echo "Backup completed at $(date)"
echo "Backup directory: $BACKUP_DIR"
echo "Files created:"
ls -la "$BACKUP_DIR"/*"$DATE"* 2>/dev/null || echo "No files found"

# Show disk usage
echo ""
echo "Backup directory size:"
du -sh "$BACKUP_DIR" 