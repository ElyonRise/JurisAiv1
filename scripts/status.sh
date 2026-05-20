#!/bin/bash
echo "Processos ativos:"
ps aux | grep -E "(uvicorn|http.server)" | grep -v grep
echo "API Health:"
curl -sf http://localhost:8000/health && echo " OK" || echo " OFFLINE"
