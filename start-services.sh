#!/bin/bash

PROJECT_DIR="/root/Mlai-lab"
LOG_DIR="$PROJECT_DIR/log"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

start_backend() {
    log "启动后端服务..."

    if pgrep -f "python3.*app.py" > /dev/null; then
        log "后端服务已在运行 (PID: $(pgrep -f 'python3.*app.py'))"
    else
        cd "$PROJECT_DIR/backend"
        nohup python3 app.py >> "$LOG_DIR/backend.log" 2>&1 &
        sleep 2

        if pgrep -f "python3.*app.py" > /dev/null; then
            log "后端服务启动成功 (PID: $(pgrep -f 'python3.*app.py'))"
        else
            log "后端服务启动失败，请检查日志: $LOG_DIR/backend.log"
        fi
    fi
}

start_frontend() {
    log "启动前端服务..."

    if pgrep -f "vite.*3000" > /dev/null; then
        log "前端服务已在运行 (PID: $(pgrep -f 'vite.*3000'))"
    else
        cd "$PROJECT_DIR/frontend"
        nohup npm run dev -- --host 0.0.0.0 --port 3000 >> "$LOG_DIR/frontend.log" 2>&1 &
        sleep 3

        if pgrep -f "vite.*3000" > /dev/null; then
            log "前端服务启动成功 (PID: $(pgrep -f 'vite.*3000'))"
        else
            log "前端服务启动失败，请检查日志: $LOG_DIR/frontend.log"
        fi
    fi
}

stop_backend() {
    log "停止后端服务..."

    if pgrep -f "python3.*app.py" > /dev/null; then
        pkill -f "python3.*app.py"
        log "后端服务已停止"
    else
        log "后端服务未运行"
    fi
}

stop_frontend() {
    log "停止前端服务..."

    if pgrep -f "vite.*3000" > /dev/null; then
        pkill -f "vite.*3000"
        log "前端服务已停止"
    else
        log "前端服务未运行"
    fi
}

check_status() {
    echo "========================================="
    echo "  Mlai-Lab 服务状态"
    echo "========================================="
    echo ""

    if pgrep -f "python3.*app.py" > /dev/null; then
        echo "后端服务: 运行中 (PID: $(pgrep -f 'python3.*app.py'))"
    else
        echo "后端服务: 未运行"
    fi

    if pgrep -f "vite.*3000" > /dev/null; then
        echo "前端服务: 运行中 (端口: 3000)"
    else
        echo "前端服务: 未运行"
    fi

    echo ""
    echo "访问地址："
    echo "  前端: http://localhost:3000"
    echo "  后端: http://localhost:8000"
    echo ""
    echo "查看日志："
    echo "  后端: tail -f $LOG_DIR/backend.log"
    echo "  前端: tail -f $LOG_DIR/frontend.log"
}

case "${1:-status}" in
    start)
        log "========== 启动 Mlai-Lab 服务 =========="
        start_backend
        start_frontend
        check_status
        ;;
    stop)
        log "========== 停止 Mlai-Lab 服务 =========="
        stop_backend
        stop_frontend
        ;;
    restart)
        log "========== 重启 Mlai-Lab 服务 =========="
        stop_backend
        stop_frontend
        sleep 2
        start_backend
        start_frontend
        check_status
        ;;
    status|*)
        check_status
        ;;
esac
