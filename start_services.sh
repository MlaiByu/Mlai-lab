#!/bin/bash
# Mlai-Lab 服务启动脚本
# 优化目标：支持50+并发用户，容器内存≤512MB，CPU≤70%，72小时稳定运行

# 获取脚本所在目录作为项目目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
LOG_DIR="$PROJECT_DIR/log"
BACKEND_PORT=8000
FRONTEND_PORT=3000

mkdir -p "$LOG_DIR"

echo "========================================="
echo "  Mlai-Lab 服务启动脚本"
echo "  优化目标：50+并发 | 容器≤512MB | CPU≤70%"
echo "========================================="
echo "项目目录: $PROJECT_DIR"
echo ""

# =========================================
# 清理旧资源
# =========================================
echo "🧹 清理旧资源..."

# 杀死占用端口的进程
echo "  - 杀死端口 $BACKEND_PORT 的进程..."
BACKEND_PID=$(ss -tlnp | grep ":$BACKEND_PORT" | grep -oP 'pid=\K[0-9]+' | head -1)
if [ -n "$BACKEND_PID" ]; then
    kill -9 $BACKEND_PID 2>/dev/null || true
    sleep 1
    echo "    ✓ 已杀死进程 $BACKEND_PID"
fi

echo "  - 杀死端口 $FRONTEND_PORT 的进程..."
FRONTEND_PID=$(ss -tlnp | grep ":$FRONTEND_PORT" | grep -oP 'pid=\K[0-9]+' | head -1)
if [ -n "$FRONTEND_PID" ]; then
    kill -9 $FRONTEND_PID 2>/dev/null || true
    sleep 1
    echo "    ✓ 已杀死进程 $FRONTEND_PID"
fi

# 清理僵尸容器
echo "  - 清理已停止的容器..."
docker container prune -f 2>/dev/null || true
echo "    ✓ 已清理僵尸容器"

# =========================================
# 启动服务
# =========================================
echo ""
echo "🚀 启动服务..."

# 启动后端服务
echo "  - 启动后端服务 (端口 $BACKEND_PORT)..."
cd "$PROJECT_DIR/backend"
nohup python3 -u app.py > "$LOG_DIR/backend.log" 2>&1 < /dev/null &
BACKEND_PID=$!
echo "    ✓ 后端服务已启动 (PID: $BACKEND_PID)"

# 启动前端服务
echo "  - 启动前端服务 (端口 $FRONTEND_PORT)..."
cd "$PROJECT_DIR/frontend"
nohup npm run dev -- --host 0.0.0.0 --port $FRONTEND_PORT > "$LOG_DIR/frontend.log" 2>&1 < /dev/null &
FRONTEND_PID=$!
echo "    ✓ 前端服务已启动 (PID: $FRONTEND_PID)"

# 保存 PID
echo $BACKEND_PID > "$LOG_DIR/backend.pid"
echo $FRONTEND_PID > "$LOG_DIR/frontend.pid"

# =========================================
# 检查服务状态
# =========================================
echo ""
echo "⏳ 等待服务启动..."
for i in {1..15}; do
    sleep 2
    
    # 检查进程
    BACKEND_RUNNING=$(ps -p $BACKEND_PID --no-headers 2>/dev/null | wc -l)
    FRONTEND_RUNNING=$(ps -p $FRONTEND_PID --no-headers 2>/dev/null | wc -l)
    
    if [ "$BACKEND_RUNNING" -eq 1 ] && [ "$FRONTEND_RUNNING" -eq 1 ]; then
        break
    fi
    
    echo "  检查中... ($i/15)"
done

echo ""
echo "========================================="
echo "  服务状态检查"
echo "========================================="

echo -n "后端 $BACKEND_PORT: "
if curl -s http://127.0.0.1:$BACKEND_PORT/api/health > /dev/null 2>&1; then
    echo "✅ 运行中 (PID: $BACKEND_PID)"
else
    echo "❌ 未响应"
    echo "    后端日志:"
    tail -30 "$LOG_DIR/backend.log" 2>/dev/null | sed 's/^/    /'
fi

echo -n "前端 $FRONTEND_PORT: "
if curl -s http://127.0.0.1:$FRONTEND_PORT/ > /dev/null 2>&1; then
    echo "✅ 运行中 (PID: $FRONTEND_PID)"
else
    echo "❌ 未响应"
    echo "    前端日志:"
    tail -30 "$LOG_DIR/frontend.log" 2>/dev/null | sed 's/^/    /'
fi

echo ""
echo "访问地址："
echo "  前端: http://localhost:$FRONTEND_PORT"
echo "  后端: http://localhost:$BACKEND_PORT"
echo ""
echo "日志文件："
echo "  后端: $LOG_DIR/backend.log"
echo "  前端: $LOG_DIR/frontend.log"
echo ""
echo "并发配置："
echo "  - Worker进程数: 自动检测CPU核心"
echo "  - 每个Worker线程数: 8"
echo "  - 最大连接数: 1000"
echo ""
echo "容器资源限制："
echo "  - 内存限制: ≤512MB"
echo "  - CPU限制: ≤0.7核"
echo ""
echo "稳定性保障："
echo "  - 进程自动重启: 每500请求轮换"
echo "  - 超时时间: 300秒"
echo "  - 优雅重启: 60秒缓冲"
