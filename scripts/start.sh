#!/bin/bash
cd ~/jurisai
mkdir -p logs backups crm/leads crm/cases
echo "Iniciando JurisAI..."
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ~/jurisai/logs/api.log 2>&1 &
echo "API iniciada (PID $!)"
sleep 3
curl -s http://localhost:8000/health | grep -q "online" && echo "API online" || echo "API iniciando..."
cd ~/jurisai && n8n start > ~/jurisai/logs/n8n.log 2>&1 &
echo "n8n iniciado (PID $!)"
echo "Acesso: API http://localhost:8000 | Docs http://localhost:8000/docs | n8n http://localhost:5678"
echo "Login: admin / JurisAI2024!"
