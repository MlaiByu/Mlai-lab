#!/bin/bash

echo "========================================="
echo "  Mlai-Lab 部署脚本"
echo "========================================="
echo ""

PROJECT_DIR="/root/Mlai-lab"
LOG_DIR="$PROJECT_DIR/log"

mkdir -p "$LOG_DIR"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/deploy.log"
}

log "========== 开始部署 Mlai-Lab =========="

if [ "$EUID" -ne 0 ]; then
    log "此脚本需要 root 权限"
    log "请运行: sudo bash deploy.sh"
    exit 1
fi

log "检查环境..."
log "Python: $(python3 --version)"
log "Node: $(node --version)"

log "========== 初始化数据库 =========="

mysql -u root -p1234 <<EOF 2>/dev/null
CREATE DATABASE IF NOT EXISTS mlai_lab CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EOF

cd "$PROJECT_DIR/backend"
python3 init_db.py

log "========== 安装前端依赖 =========="

cd "$PROJECT_DIR/frontend"

if [ ! -d "node_modules" ]; then
    log "安装前端依赖..."
    npm install
fi

log "========== 配置自启动 =========="

AUTO_START="@reboot cd $PROJECT_DIR && bash $PROJECT_DIR/auto-start.sh"

EXISTING_CRON=$(crontab -l 2>/dev/null | grep -v "auto-start.sh")
echo "$EXISTING_CRON" | grep -q "$AUTO_START" || {
    (echo "$EXISTING_CRON"; echo "$AUTO_START") | crontab -
    log "自启动已配置 (使用 cron @reboot)"
}

log "========== 启动服务 =========="

bash "$PROJECT_DIR/auto-start.sh"

sleep 3

BACKEND_STATUS=$(pgrep -f "python3.*app.py" > /dev/null && echo "运行中" || echo "未运行")
FRONTEND_STATUS=$(pgrep -f "vite.*3000" > /dev/null && echo "运行中" || echo "未运行")

log "========== 部署完成 =========="
log "后端 8000: $BACKEND_STATUS"
log "前端 3000: $FRONTEND_STATUS"
log ""
log "访问地址："
log "  前端: http://localhost:3000"
log "  后端: http://localhost:8000"
log ""
log "管理命令："
log "  bash $PROJECT_DIR/auto-start.sh  # 启动/重启服务"
log "  crontab -e                      # 编辑定时任务"
