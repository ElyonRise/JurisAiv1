#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
PID_FILE="$PROJECT_DIR/.backend.pid"
N8N_PID_FILE="$PROJECT_DIR/.n8n.pid"

echo "🚀 Starting JurisAI Phase 7..."

# 1. Start Uvicorn Backend
echo "📡 Starting backend server on port 8000..."
cd "$BACKEND_DIR"
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > "$PROJECT_DIR/backend.log" 2>&1 &
echo $! > "$PID_FILE"
echo "   Backend PID: $(cat "$PID_FILE")"

# 2. Verify API Health
echo "⏳ Waiting for backend health check..."
for i in {1..30}; do
  if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is healthy!"
    break
  fi
  if [ "$i" -eq 30 ]; then
    echo "❌ Backend failed to start within 30 seconds. Check backend.log"
    exit 1
  fi
  sleep 1
done

# 3. Install n8n globally if not present
if ! command -v n8n &> /dev/null; then
  echo "📦 Installing n8n globally..."
  npm install -g n8n
else
  echo "✅ n8n is already installed."
fi

# 4. Start n8n
echo "🔄 Starting n8n automation engine on port 5678..."
cd "$PROJECT_DIR"
nohup n8n start > "$PROJECT_DIR/n8n.log" 2>&1 &
echo $! > "$N8N_PID_FILE"
echo "   n8n PID: $(cat "$N8N_PID_FILE")"

echo ""
echo "🎉 JurisAI Phase 7 started successfully!"
echo "🌐 API Docs: http://localhost:8000/docs"
echo "🤖 n8n Workflow Editor: http://localhost:5678"
echo "🔑 Default n8n credentials: admin / admin (setup on first run)"
echo ""
echo "To stop services:"
echo "  kill \$(cat $PID_FILE) && kill \$(cat $N8N_PID_FILE)"
