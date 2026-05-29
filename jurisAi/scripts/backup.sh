#!/usr/bin/env bash
set -euo pipefail

# JurisAI Backup Script
# Archives specific project directories into timestamped .tar.gz files
# with 30-day retention policy.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_FILE="$BACKUP_DIR/jurisai_backup_${TIMESTAMP}.tar.gz"

# Directories to back up (relative to project root)
BACKUP_DIRS=("crm" "contracts/generated" "docs")

# Retention period in days
RETENTION_DAYS=30

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Verify source directories exist
for dir in "${BACKUP_DIRS[@]}"; do
  if [[ ! -d "$PROJECT_ROOT/$dir" ]]; then
    echo "Warning: Directory '$dir' does not exist, skipping."
  fi
done

# Create tar archive
echo "Creating backup: $BACKUP_FILE"
tar -czf "$BACKUP_FILE" \
  -C "$PROJECT_ROOT" \
  "${BACKUP_DIRS[@]}" 2>/dev/null || true

if [[ -f "$BACKUP_FILE" ]]; then
  echo "Backup created successfully: $(basename "$BACKUP_FILE")"
else
  echo "Error: Backup creation failed."
  exit 1
fi

# Clean up old backups
echo "Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "jurisai_backup_*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete

echo "Backup complete."
