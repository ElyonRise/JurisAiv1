#!/usr/bin/env bash
set -euo pipefail
API_URL="http://127.0.0.1:8000/health"   # ajuste se
seu endpoint for outro
TIMEOUT=5
LOG_FILE="${HOME}/jurisai/health.log"

if ! curl -s --max-time "${TIMEOUT}" "${API_URL}" |
grep -q '"status":"ok"'; then
    echo "[$(date)] API indisponível – tentando
reiniciar..." >> "${LOG_FILE}"
    # Tenta systemd primeiro, depois supervisor
    if systemctl list-units --type=service | grep -q
jurisai-api; then
        sudo systemctl restart jurisai-api
    elif command -v supervisorctl >/dev/null &&
supervisorctl status jurisai-api >/dev/null 2>&1;
then
        sudo supervisorctl restart jurisai-api
    else
        echo "[$(date)] Nenhum serviço conhecido
(jurisai-api) encontrado para reiniciar." >>
"${LOG_FILE}"
    fi
else
    echo "[$(date)] API OK" >> "${LOG_FILE}"
fi
