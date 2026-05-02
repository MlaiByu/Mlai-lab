#!/bin/bash
# Mlai-Lab 项目启动脚本（持久化版本）
# 确保终端断开后服务仍在运行

function start() {
    echo "正在停止旧进程..."
    pkill -f "python.*app.py" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    pkill -f "node.*vite" 2>/dev/null
    sleep 2

    echo "正在启动后端..."
    cd /root/Mlai-lab/backend
    nohup python3 app.py > /tmp/mlai-backend.log 2>&1 &
    echo "后端进程ID: $!"

    echo "正在启动前端..."
    cd /root/Mlai-lab/frontend
    nohup npm run dev > /tmp/mlai-frontend.log 2>&1 &
    echo "前端进程ID: $!"

    echo "等待服务启动..."
    sleep 6

    echo ""
    echo "=== 服务状态检查 ==="
    if ss -tlnp 2>/dev/null | grep -q ":8000"; then
        echo "✅ 后端: http://127.0.0.1:8000 (外网: http://8.136.148.183:8000)"
    else
        echo "❌ 后端启动失败，请查看 /tmp/mlai-backend.log"
    fi

    if ss -tlnp 2>/dev/null | grep -q ":3000"; then
        echo "✅ 前端: http://127.0.0.1:3000 (外网: http://8.136.148.183:3000)"
    else
        echo "❌ 前端启动失败，请查看 /tmp/mlai-frontend.log"
    fi
}

function stop() {
    echo "正在停止服务..."
    pkill -f "python.*app.py"
    pkill -f "vite"
    pkill -f "node.*vite"
    echo "服务已停止"
}

function status() {
    echo "=== Mlai-Lab 服务状态 ==="
    ps aux | grep -E "(python.*app|vite|node.*vite)" | grep -v grep || echo "无服务在运行"
    echo ""
    ss -tlnp 2>/dev/null | grep -E ":(3000|8000)" || echo "无端口在监听"
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        stop
        sleep 2
        start
        ;;
    status)
        status
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
