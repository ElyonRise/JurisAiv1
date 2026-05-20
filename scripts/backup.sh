#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/jurisai/backups
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/jurisai_backup_$DATE.tar.gz ~/jurisai/data ~/jurisai/backend/uploads ~/jurisai/logs --exclude="*.pyc" 2>/dev/null
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
echo "[$(date)] Backup criado: jurisai_backup_$DATE.tar.gz"
