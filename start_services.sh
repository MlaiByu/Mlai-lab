#!/bin/bash
# Mlai-Lab 服务启动脚本
# 直接根据端口杀死进程并启动服务

PROJECT_DIR="/root/Mlai-lab"
LOG_DIR="$PROJECT_DIR/log"
BACKEND_PORT=8000
FRONTEND_PORT=3000

mkdir -p "$LOG_DIR"

echo "========================================="
echo "  Mlai-Lab 服务启动脚本"
echo "========================================="

# =========================================
# 杀死占用端口的进程
# =========================================
echo ""
echo "🔪 正在杀死占用端口的进程..."

# 杀死占用8000端口的进程
echo "  - 杀死端口 $BACKEND_PORT 的进程..."
BACKEND_PID=$(ss -tlnp | grep ":$BACKEND_PORT" | grep -oP 'pid=\K[0-9]+' | head -1)
if [ -n "$BACKEND_PID" ]; then
    kill -9 $BACKEND_PID 2>/dev/null || true
    sleep 1
    echo "    ✓ 已杀死进程 $BACKEND_PID"
else
    echo "    ✓ 端口 $BACKEND_PORT 未被占用"
fi

# 杀死占用3000端口的进程
echo "  - 杀死端口 $FRONTEND_PORT 的进程..."
FRONTEND_PID=$(ss -tlnp | grep ":$FRONTEND_PORT" | grep -oP 'pid=\K[0-9]+' | head -1)
if [ -n "$FRONTEND_PID" ]; then
    kill -9 $FRONTEND_PID 2>/dev/null || true
    sleep 1
    echo "    ✓ 已杀死进程 $FRONTEND_PID"
else
    echo "    ✓ 端口 $FRONTEND_PORT 未被占用"
fi

# =========================================
# 启动服务
# =========================================
echo ""
echo "🚀 启动服务..."

# 启动后端服务
echo "  - 启动后端服务 (端口 $BACKEND_PORT)..."
cd "$PROJECT_DIR/backend"
nohup python3 app.py >> "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "    ✓ 后端服务已启动 (PID: $BACKEND_PID)"

# 启动前端服务
echo "  - 启动前端服务 (端口 $FRONTEND_PORT)..."
cd "$PROJECT_DIR/frontend"
nohup npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT >> "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo "    ✓ 前端服务已启动 (PID: $FRONTEND_PID)"

# =========================================
# 检查服务状态
# =========================================
echo ""
echo "⏳ 等待服务启动..."
sleep 5

echo ""
echo "========================================="
echo "  服务状态检查"
echo "========================================="

echo -n "后端 $BACKEND_PORT: "
if curl -s http://localhost:$BACKEND_PORT/ > /dev/null 2>&1; then
    echo "✅ 运行中"
else
    echo "❌ 未响应"
fi

echo -n "前端 $FRONTEND_PORT: "
if curl -s http://localhost:$FRONTEND_PORT/ > /dev/null 2>&1; then
    echo "✅ 运行中"
else
    echo "❌ 未响应"
fi

echo ""
echo "访问地址："
echo "  前端: http://localhost:$FRONTEND_PORT"
echo "  后端: http://localhost:$BACKEND_PORT"
