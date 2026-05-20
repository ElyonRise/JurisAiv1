#!/bin/bash
cd ~/jurisai
mkdir -p data logs backend/uploads
echo "Instalando dependencias..."
pip3 install fastapi uvicorn python-jose passlib[bcrypt] httpx python-dotenv pydantic python-multipart --break-system-packages > /dev/null 2>&1
echo "Iniciando Backend (porta 8000)..."
cd backend && python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload > ~/jurisai/logs/api.log 2>&1 &
echo "Backend PID: $!"
cd ~/jurisai/frontend && python3 -m http.server 8080 > ~/jurisai/logs/web.log 2>&1 &
echo "Frontend PID: $!"
echo "Acesso: http://localhost:8080 | API Docs: http://localhost:8000/docs"
