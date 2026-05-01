#!/bin/bash
# Docker镜像预热脚本
# 提前拉取常用镜像，避免启动时等待

echo "=========================================="
echo "  Docker镜像预热"
echo "=========================================="
echo ""

# 常用镜像列表
IMAGES=(
    "mysql:5.7"
    "php:7.4-apache"
    "python:3.9-slim"
    "nginx:alpine"
)

for IMAGE in "${IMAGES[@]}"; do
    echo "检查镜像: $IMAGE"
    if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "$IMAGE"; then
        echo "  正在拉取..."
        docker pull "$IMAGE"
    else
        echo "  ✓ 已存在"
    fi
    echo ""
done

echo "=========================================="
echo "  预热完成！"
echo "=========================================="
