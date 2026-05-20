#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=~/jurisai/backups
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/jurisai_backup_$DATE.tar.gz ~/jurisai/crm ~/jurisai/contracts/generated ~/jurisai/docs --exclude="*.pyc" 2>/dev/null
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
echo "[$(date)] Backup criado: jurisai_backup_$DATE.tar.gz"
