#!/bin/bash
echo "=== STATUS JURISAI ==="
ps aux | grep -E "(uvicorn|n8n)" | grep -v grep | awk '{print "  PID:"$2, $11}'
echo "API:"
curl -s http://localhost:8000/health 2>/dev/null || echo "  Offline"
echo "Disco:"
du -sh ~/jurisai/* 2>/dev/null | sort -h
