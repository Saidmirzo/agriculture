#!/bin/bash

#############################################################################
# Backup and Restore Script
# Database va static files backup-lashni avtomatlashtirish
#############################################################################

set -e

BACKUP_DIR="/var/backups/agriculture"
APP_DIR="/var/www/agriculture"
DB_NAME="agriculture_db"
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup directory
sudo mkdir -p "$BACKUP_DIR"

case "${1:-backup}" in
    backup)
        log_info "Starting backup process..."
        
        # Database backup
        log_info "Backing up PostgreSQL database..."
        sudo -u postgres pg_dump "$DB_NAME" | gzip > "$BACKUP_DIR/db_backup_$BACKUP_DATE.sql.gz"
        log_info "✓ Database backed up: db_backup_$BACKUP_DATE.sql.gz"
        
        # Media files backup
        log_info "Backing up media files..."
        sudo tar -czf "$BACKUP_DIR/media_backup_$BACKUP_DATE.tar.gz" -C "$APP_DIR" public/
        log_info "✓ Media backed up: media_backup_$BACKUP_DATE.tar.gz"
        
        # Static files backup
        log_info "Backing up static files..."
        sudo tar -czf "$BACKUP_DIR/static_backup_$BACKUP_DATE.tar.gz" -C "$APP_DIR" static/
        log_info "✓ Static files backed up: static_backup_$BACKUP_DATE.tar.gz"
        
        # Code backup
        log_info "Backing up code..."
        sudo tar -czf "$BACKUP_DIR/code_backup_$BACKUP_DATE.tar.gz" \
            --exclude=venv \
            --exclude=.git \
            --exclude=__pycache__ \
            --exclude="*.pyc" \
            -C "$APP_DIR" .
        log_info "✓ Code backed up: code_backup_$BACKUP_DATE.tar.gz"
        
        # List backups
        log_info "Recent backups:"
        ls -lh "$BACKUP_DIR" | tail -10
        
        log_info "✓ Backup complete!"
        ;;
        
    restore-db)
        log_warn "Database restore starting..."
        
        if [ -z "$2" ]; then
            log_error "Usage: $0 restore-db <backup_file.sql.gz>"
            exit 1
        fi
        
        BACKUP_FILE="$BACKUP_DIR/$2"
        
        if [ ! -f "$BACKUP_FILE" ]; then
            log_error "Backup file not found: $BACKUP_FILE"
            exit 1
        fi
        
        read -p "Drop existing database? (y/n): " confirm
        if [ "$confirm" = "y" ]; then
            log_warn "Dropping database..."
            sudo -u postgres dropdb "$DB_NAME" 2>/dev/null || true
            sudo -u postgres createdb "$DB_NAME"
        fi
        
        log_info "Restoring database..."
        sudo -u postgres gunzip -c "$BACKUP_FILE" | sudo -u postgres psql "$DB_NAME"
        log_info "✓ Database restored!"
        ;;
        
    restore-files)
        log_warn "File restore starting..."
        
        if [ -z "$2" ] || [ -z "$3" ]; then
            log_error "Usage: $0 restore-files <type> <backup_file>"
            log_error "Type: media, static, or code"
            exit 1
        fi
        
        BACKUP_FILE="$BACKUP_DIR/$3"
        
        if [ ! -f "$BACKUP_FILE" ]; then
            log_error "Backup file not found: $BACKUP_FILE"
            exit 1
        fi
        
        case "$2" in
            media)
                log_warn "Restoring media files..."
                sudo tar -xzf "$BACKUP_FILE" -C "$APP_DIR"
                log_info "✓ Media restored!"
                ;;
            static)
                log_warn "Restoring static files..."
                sudo tar -xzf "$BACKUP_FILE" -C "$APP_DIR"
                log_info "✓ Static files restored!"
                ;;
            code)
                log_warn "Restoring code (excluding venv)..."
                sudo tar -xzf "$BACKUP_FILE" -C "$APP_DIR"
                log_info "✓ Code restored!"
                ;;
            *)
                log_error "Unknown type: $2"
                exit 1
                ;;
        esac
        ;;
        
    list)
        log_info "Available backups:"
        ls -lh "$BACKUP_DIR/"
        ;;
        
    cleanup)
        log_warn "Removing old backups (older than 30 days)..."
        find "$BACKUP_DIR" -type f -mtime +30 -delete
        log_info "✓ Cleanup complete!"
        ;;
        
    *)
        echo "Usage: $0 {backup|restore-db|restore-files|list|cleanup}"
        echo ""
        echo "Examples:"
        echo "  $0 backup                    # Create full backup"
        echo "  $0 list                      # List all backups"
        echo "  $0 restore-db backup.sql.gz  # Restore database"
        echo "  $0 restore-files media backup.tar.gz  # Restore media"
        echo "  $0 cleanup                   # Remove old backups"
        exit 1
        ;;
esac
