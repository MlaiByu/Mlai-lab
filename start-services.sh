#!/bin/bash

start_services() {
    echo "正在启动服务..."

    # 停止已有进程
    pkill -f "python.*app.py" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    sleep 1

    # 启动后端
    cd /root/Mlai-lab/backend
    nohup python3 app.py > /tmp/backend.log 2>&1 &
    disown
    echo "后端PID: $!"

    # 启动前端
    cd /root/Mlai-lab/frontend
    nohup npm run dev > /tmp/frontend.log 2>&1 &
    disown
    echo "前端PID: $!"

    # 等待服务启动
    sleep 5

    # 检查服务状态
    echo ""
    echo "服务状态检查:"
    if ss -tlnp 2>/dev/null | grep -q ":8000"; then
        echo "✓ 后端已启动 (端口 8000)"
    else
        echo "✗ 后端启动失败，请检查 /tmp/backend.log"
    fi

    if ss -tlnp 2>/dev/null | grep -q ":3000"; then
        echo "✓ 前端已启动 (端口 3000)"
    else
        echo "✗ 前端启动失败，请检查 /tmp/frontend.log"
    fi

    echo ""
    echo "=========================================="
    echo "服务已启动！"
    echo "访问地址: http://8.136.148.183:3000"
    echo "=========================================="
}

stop_services() {
    echo "正在停止服务..."
    pkill -f "python.*app.py"
    pkill -f "vite"
    sleep 1
    echo "服务已停止"
}

case $1 in
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
        echo "服务状态:"
        if ss -tlnp 2>/dev/null | grep -q ":8000"; then
            echo "✓ 后端运行中 (端口 8000)"
        else
            echo "✗ 后端未运行"
        fi
        if ss -tlnp 2>/dev/null | grep -q ":3000"; then
            echo "✓ 前端运行中 (端口 3000)"
        else
            echo "✗ 前端未运行"
        fi
        ;;
    *)
        echo "用法: ./start-services.sh {start|stop|restart|status}"
        ;;
esac