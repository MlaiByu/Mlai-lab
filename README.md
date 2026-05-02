# Mlai-Lab 网络安全培训平台

## 项目概述

Mlai-Lab 是一个网络安全培训平台，提供9种漏洞实战环境，用于网络安全学习和实践。

## 当前环境

- **后端服务**: 运行在 0.0.0.0:8000
- **前端服务**: 运行在 0.0.0.0:3000
- **数据库**: MySQL
- **漏洞环境**: Docker

## 环境要求

- Python 3.8+
- Node.js 16+
- Docker + Docker Compose
- MySQL

## 完整启动流程

### 第一步：克隆项目

```bash
git clone https://github.com/MlaiByu/Mlai-lab.git
cd Mlai-lab
```

### 第二步：安装Python依赖

```bash
pip install -r requirements.txt
```

### 第三步：安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 第四步：配置MySQL数据库

#### 4.1 登录MySQL

```bash
mysql -u root -p
```

#### 4.2 执行以下SQL命令

```sql
-- 创建数据库
CREATE DATABASE IF NOT EXISTS mlai_lab;

-- 创建用户并授权
CREATE USER IF NOT EXISTS 'Mlai'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON mlai_lab.* TO 'Mlai'@'localhost';
FLUSH PRIVILEGES;

-- 退出MySQL
EXIT;
```

### 第五步：构建Docker漏洞镜像（首次使用必须）

```bash
cd docker
./build-images.sh
cd ..
```

### 第六步：启动服务

```bash
chmod +x start.sh
./start.sh start
```

### 第七步：访问应用

- **前端地址**: http://localhost:3000
- **后端API**: http://localhost:8000
- **公网地址**: http://8.136.148.183:3000

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | password | 教师 |
| user | userpass | 学生 |

## 服务管理命令

```bash
# 启动服务
./start.sh start

# 停止服务
./start.sh stop

# 重启服务
./start.sh restart

# 查看服务状态
./start.sh status
```

## 漏洞环境列表

| 编号 | 漏洞类型 | 难度 |
|------|----------|------|
| 1 | SQL注入 - 入门 | ⭐ |
| 2 | SQL注入 - 中级 | ⭐⭐ |
| 3 | SQL注入 - 高级 | ⭐⭐⭐ |
| 4 | 反射型XSS | ⭐ |
| 5 | 存储型XSS | ⭐⭐ |
| 6 | DOM型XSS | ⭐⭐ |
| 7 | PHP反序列化 | ⭐⭐ |
| 8 | Python反序列化 | ⭐⭐⭐ |
| 9 | 文件上传 | ⭐ |

## 快速命令汇总

```bash
# 完整启动流程
git clone https://github.com/MlaiByu/Mlai-lab.git
cd Mlai-lab
pip install -r requirements.txt
cd frontend && npm install && cd ..
cd docker && ./build-images.sh && cd ..
chmod +x start.sh
./start.sh start

# 日常操作
./start.sh status    # 查看状态
./start.sh stop      # 停止服务
./start.sh restart   # 重启服务
```

## 项目结构

```
Mlai-lab/
├── backend/         # Flask后端
│   ├── app.py      # 主应用
│   ├── routes/      # API路由
│   └── utils/      # 工具模块
├── frontend/      # Vue3前端
│   ├── src/        # 源代码
│   └── package.json
├── docker/        # 漏洞环境
│   ├── build-images.sh
│   ├── sqli-easy/
│   ├── sqli-medium/
│   ├── sqli-hard/
│   ├── xss-reflected/
│   ├── xss-stored/
│   ├── xss-dom/
│   ├── php-deserialization/
│   ├── python-deserialization/
│   └── file-upload/
├── start.sh       # 服务管理脚本
└── requirements.txt
```

## 常见问题

### 端口已被占用

修改 `backend/app.py` 或 `frontend/vite.config.js` 中的端口配置。

### Docker权限问题

确保当前用户在 docker 用户组中：
```bash
sudo usermod -aG docker $USER
```

### npm依赖安装失败

尝试清理缓存：
```bash
cd frontend
npm cache clean --force
npm install
```

### MySQL连接失败

检查MySQL服务是否启动，用户名和密码是否正确。

## LICENSE

MIT License
