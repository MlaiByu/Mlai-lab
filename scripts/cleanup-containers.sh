#!/bin/bash

PROJECT_DIR="/root/Mlai-lab"
LOG_DIR="$PROJECT_DIR/log"
mkdir -p "$LOG_DIR"

LOG_FILE="$LOG_DIR/cleanup_$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========== 开始清理过期容器 =========="

docker ps -a --filter "label=mlai-lab-vulnerability=true" --format "{{.Names}}" | while read container_name; do
    if [ -n "$container_name" ]; then
        log "清理容器: $container_name"
        docker rm -f "$container_name" >> "$LOG_FILE" 2>&1
    fi
done

log "清理未使用的docker卷..."
docker volume prune -f >> "$LOG_FILE" 2>&1

log "清理未使用的docker网络..."
docker network prune -f >> "$LOG_FILE" 2>&1

log "========== 清理完成 =========="
