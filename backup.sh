#!/usr/bin/env bash
set -euo pipefail
BACKUP_DIR="${HOME}/jurisai/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
mkdir -p "${BACKUP_DIR}"
if [[ -f "./jurisai.db" ]]; then
    cp "./jurisai.db"
"${BACKUP_DIR}/jurisai_${TIMESTAMP}.db"
    echo "[$(date)] Backup SQLite criado:
jurisai_${TIMESTAMP}.db"
else
    echo "[$(date)] Arquivo jurisai.db não
encontrado – nada a fazer."
fi
