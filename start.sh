#!/bin/bash
# Mlai-Lab 服务启动脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
LOG_DIR="$PROJECT_DIR/log"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3000}"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

info() { echo "[$(date '+%H:%M:%S')] $1"; }
success() { echo -e "[${GREEN}OK${NC}] $1"; }
error() { echo -e "[${RED}ERR${NC}] $1"; exit 1; }

kill_port() {
    local pid=$(ss -tlnp | grep ":$1" | grep -oP 'pid=\K[0-9]+' | head -1)
    [ -n "$pid" ] && kill -9 "$pid" 2>/dev/null || true
}

mkdir -p "$LOG_DIR"

echo "========================================="
echo "  Mlai-Lab 服务启动"
echo "========================================="
echo "项目目录: $PROJECT_DIR"
echo ""

info "停止旧服务..."
kill_port "$BACKEND_PORT"
kill_port "$FRONTEND_PORT"
docker container prune -f >/dev/null 2>&1 || true
success "旧服务已停止"

info "启动后端服务..."
cd "$PROJECT_DIR/backend"
if ! python3 -c "import flask" 2>/dev/null; then
    info "安装后端依赖..."
    pip3 install -q -r requirements.txt
fi

if command -v gunicorn >/dev/null 2>&1; then
    nohup gunicorn -c gunicorn.conf.py app:app > "$LOG_DIR/backend.log" 2>&1 < /dev/null &
else
    nohup python3 -u app.py > "$LOG_DIR/backend.log" 2>&1 < /dev/null &
fi
echo "$!" > "$LOG_DIR/backend.pid"
success "后端服务已启动 (端口: $BACKEND_PORT)"

info "启动前端服务..."
cd "$PROJECT_DIR/frontend"
if [ ! -d node_modules ]; then
    info "安装前端依赖..."
    npm install --production > "$LOG_DIR/npm_install.log" 2>&1
fi
nohup npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" > "$LOG_DIR/frontend.log" 2>&1 < /dev/null &
echo "$!" > "$LOG_DIR/frontend.pid"
success "前端服务已启动 (端口: $FRONTEND_PORT)"

echo ""
echo "========================================="
echo "  服务启动完成"
echo "========================================="
echo "前端: http://localhost:$FRONTEND_PORT"
echo "后端: http://localhost:$BACKEND_PORT/api"
echo "日志: $LOG_DIR/"