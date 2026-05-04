#!/bin/bash

PROJECT_DIR="/root/Mlai-lab"
LOG_DIR="$PROJECT_DIR/log"

mkdir -p "$LOG_DIR"

echo "[$(date)] 开始自启动检查" >> "$LOG_DIR/autostart.log"

BACKEND_PID=$(pgrep -f "python3.*app.py")
FRONTEND_PID=$(pgrep -f "vite.*3000")

if [ -z "$BACKEND_PID" ]; then
    cd "$PROJECT_DIR/backend"
    nohup python3 app.py >> "$LOG_DIR/backend.log" 2>&1 &
    echo "[$(date)] 后端服务已启动 (PID: $!)" >> "$LOG_DIR/autostart.log"
else
    echo "[$(date)] 后端服务已在运行 (PID: $BACKEND_PID)" >> "$LOG_DIR/autostart.log"
fi

if [ -z "$FRONTEND_PID" ]; then
    cd "$PROJECT_DIR/frontend"
    nohup npm run dev -- --host 0.0.0.0 --port 3000 >> "$LOG_DIR/frontend.log" 2>&1 &
    echo "[$(date)] 前端服务已启动 (PID: $!)" >> "$LOG_DIR/autostart.log"
else
    echo "[$(date)] 前端服务已在运行 (PID: $FRONTEND_PID)" >> "$LOG_DIR/autostart.log"
fi

echo "[$(date)] 自启动检查完成" >> "$LOG_DIR/autostart.log"