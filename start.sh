#!/bin/bash
# Mlai-Lab 持久化服务启动脚本

function start_services() {
    echo "正在启动 Mlai-Lab 服务..."

    # 停止已有进程
    pkill -f "python.*app.py" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    sleep 1

    # 启动后端 - 使用nohup和disown确保持久化
    cd /root/Mlai-lab/backend
    nohup python3 app.py </dev/null >/dev/null 2>&1 &
    BACKEND_PID=$!
    disown $BACKEND_PID
    echo "后端已启动 (PID: $BACKEND_PID)"

    # 启动前端
    cd /root/Mlai-lab/frontend
    nohup npm run dev </dev/null >/dev/null 2>&1 &
    FRONTEND_PID=$!
    disown $FRONTEND_PID
    echo "前端已启动 (PID: $FRONTEND_PID)"

    # 等待服务启动
    sleep 5

    # 验证服务状态
    echo ""
    echo "=== 服务状态检查 ==="
    if ss -tlnp 2>/dev/null | grep -q ":8000"; then
        echo "✅ 后端运行中: http://8.136.148.183:8000"
    else
        echo "❌ 后端启动失败"
    fi

    if ss -tlnp 2>/dev/null | grep -q ":3000"; then
        echo "✅ 前端运行中: http://8.136.148.183:3000"
    else
        echo "❌ 前端启动失败"
    fi
    echo ""
}

function stop_services() {
    echo "正在停止服务..."
    pkill -f "python.*app.py"
    pkill -f "vite"
    sleep 1
    echo "服务已停止"
}

function check_status() {
    echo "=== Mlai-Lab 服务状态 ==="
    if ps aux | grep -E "python.*app.py" | grep -v grep > /dev/null; then
        echo "✅ 后端运行中"
    else
        echo "❌ 后端未运行"
    fi

    if ps aux | grep -E "vite" | grep -v grep > /dev/null; then
        echo "✅ 前端运行中"
    else
        echo "❌ 前端未运行"
    fi
    echo ""
    ss -tlnp 2>/dev/null | grep -E ":(3000|8000)"
}

case "$1" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        sleep 2
        start_services
        ;;
    status)
        check_status
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
