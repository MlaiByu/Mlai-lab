#!/bin/bash

set -e

DOCKER_DIR=$(dirname "$(realpath "$0")")
cd "$DOCKER_DIR"

echo "=========================================="
echo "开始构建 Mlai Lab Docker 镜像"
echo "=========================================="
echo ""

echo "[1/10] 构建基础镜像: mlai-lab/php-mysqli"
cd base-images/php-mysqli
docker build -t mlai-lab/php-mysqli:latest .
cd ../..
echo ""

echo "[2/10] 构建镜像: mlai-lab/sqli-easy"
cd sqli-easy
docker build -t mlai-lab/sqli-easy:latest .
cd ..
echo ""

echo "[3/10] 构建镜像: mlai-lab/sqli-medium"
cd sqli-medium
docker build -t mlai-lab/sqli-medium:latest .
cd ..
echo ""

echo "[4/10] 构建镜像: mlai-lab/sqli-hard"
cd sqli-hard
docker build -t mlai-lab/sqli-hard:latest .
cd ..
echo ""

echo "[5/10] 构建镜像: mlai-lab/xss-reflected"
cd xss-reflected
docker build -t mlai-lab/xss-reflected:latest .
cd ..
echo ""

echo "[6/10] 构建镜像: mlai-lab/xss-stored"
cd xss-stored
docker build -t mlai-lab/xss-stored:latest .
cd ..
echo ""

echo "[7/10] 构建镜像: mlai-lab/xss-dom"
cd xss-dom
docker build -t mlai-lab/xss-dom:latest .
cd ..
echo ""

echo "[8/10] 构建镜像: mlai-lab/php-deserialization"
cd php-deserialization
docker build -t mlai-lab/php-deserialization:latest .
cd ..
echo ""

echo "[9/10] 构建镜像: mlai-lab/python-deserialization"
cd python-deserialization
docker build -t mlai-lab/python-deserialization:latest .
cd ..
echo ""

echo "[10/10] 构建镜像: mlai-lab/file-upload"
cd file-upload
docker build -t mlai-lab/file-upload:latest .
cd ..
echo ""

echo "=========================================="
echo "所有镜像构建完成！"
echo "=========================================="
echo ""
echo "已构建的镜像："
docker images | grep mlai-lab
