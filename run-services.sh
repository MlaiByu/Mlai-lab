#!/bin/bash
case $1 in
start)
    echo "启动服务..."
    pkill -f "python.*app.py" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    pkill -f "node.*vite" 2>/dev/null
    sleep 1
    cd /root/Mlai-lab
    setsid bash -c 'cd /root/Mlai-lab/backend && python3 app.py </dev/null >/dev/null 2>&1' &
    setsid bash -c 'cd /root/Mlai-lab/frontend && npm run dev </dev/null >/dev/null 2>&1' &
    sleep 3
    if ss -tlnp 2>/dev/null | grep -q ":8000"; then
        echo "后端已启动 (端口 8000)"
    fi
    if ss -tlnp 2>/dev/null | grep -q ":3000"; then
        echo "前端已启动 (端口 3000)"
    fi
    echo "完成！前端: http://8.136.148.183:3000"
    ;;
stop)
    echo "停止服务..."
    pkill -f "python.*app.py"
    pkill -f "vite"
    pkill -f "node.*vite"
    sleep 1
    echo "完成！"
    ;;
*)
    echo "用法: ./run-services.sh {start|stop}"
    ;;
esac