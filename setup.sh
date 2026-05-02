#!/bin/bash
# Mlai-Lab 一键部署脚本

set -e

echo "==================================="
echo "    Mlai-Lab 部署脚本"
echo "==================================="
echo ""

# 检查是否有虚拟环境（可选）
if [ ! -d "venv" ]; then
    echo "建议创建Python虚拟环境 (跳过执行)"
fi

echo ""
echo "1. 检查依赖..."

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装"
    exit 1
fi

# 检查Node.js
if ! command -v node &> /dev/null; then
    echo "❌ 未找到Node.js，请先安装"
    exit 1
fi

# 检查Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  未找到Docker，漏洞环境将无法使用"
fi

echo "✅ 基础依赖检查完成"
echo ""

# 安装后端依赖
echo "2. 安装后端依赖..."
pip install -r requirements.txt

# 安装前端依赖
echo "3. 安装前端依赖..."
cd frontend
npm install
cd ..

# 初始化数据库
echo "4. 初始化数据库..."
cd backend
python3 -c "
from utils.db import init_db
init_db()
print('数据库初始化完成')
"
cd ..

# 检查Docker镜像
if command -v docker &> /dev/null; then
    echo ""
    echo "5. 检查Docker镜像..."
    echo "建议运行: cd docker && ./build-images.sh"
fi

echo ""
echo "==================================="
echo "    部署完成！"
echo "==================================="
echo ""
echo "启动服务: ./start.sh start"
echo ""
echo "默认账号："
echo "  admin / password (教师)"
echo "  user / userpass (学生)"
echo ""
echo "访问地址: http://localhost:3000"
echo ""
