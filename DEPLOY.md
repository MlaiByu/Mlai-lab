# Mlai-Lab 网络安全培训平台 - 部署指南

## 项目概述

Mlai-Lab 是一个网络安全培训平台，提供9种漏洞实战环境。

## 环境要求

- Python 3.8+
- Node.js 16+
- Docker + Docker Compose
- MySQL (可选，默认为SQLite)

## 快速部署（推荐）

### 1. 克隆项目

```bash
git clone https://github.com/MlaiByu/Mlai-lab.git
cd Mlai-lab
```

### 2. 安装依赖

#### 后端依赖

```bash
pip install -r requirements.txt
```

#### 前端依赖

```bash
cd frontend
npm install
cd ..
```

### 3. 初始化数据库

```bash
cd backend
python init_db.py
cd ..
```

### 4. 构建Docker漏洞环境（首次使用）

```bash
cd docker
./build-images.sh
cd ..
```

### 5. 启动服务

```bash
chmod +x start.sh
./start.sh start
```

### 6. 访问应用

- 前端地址: http://localhost:3000
- 后端API: http://localhost:8000

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

| 漏洞类型 | 难度 | 说明 |
|----------|------|------|
| SQL注入 - 入门 | ⭐ | 简单的SQL注入演示 |
| SQL注入 - 中级 | ⭐⭐ | 含简单过滤的SQL注入 |
| SQL注入 - 高级 | ⭐⭐⭐ | 含复杂WAF规则的SQL注入 |
| 反射型XSS | ⭐ | 反射型跨站脚本攻击 |
| 存储型XSS | ⭐⭐ | 存储型跨站脚本攻击 |
| DOM型XSS | ⭐⭐ | DOM型跨站脚本攻击 |
| PHP反序列化 | ⭐⭐ | PHP反序列化漏洞 |
| Python反序列化 | ⭐⭐⭐ | Python反序列化漏洞 |
| 文件上传 | ⭐ | 文件上传漏洞 |

## 配置数据库（可选）

### 使用SQLite（默认）

无需额外配置，开箱即用。

### 使用MySQL

1. 修改 `backend/config.py` 或 `backend/utils/db.py` 中的数据库连接信息
2. 创建数据库：
   ```sql
   CREATE DATABASE mlai_lab;
   CREATE USER 'Mlai'@'localhost' IDENTIFIED BY '1234';
   GRANT ALL PRIVILEGES ON mlai_lab.* TO 'Mlai'@'localhost';
   FLUSH PRIVILEGES;
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

## 项目结构

```
Mlai-lab/
├── backend/              # Flask后端
│   ├── app.py           # 主应用
│   ├── routes/          # API路由
│   ├── utils/           # 工具模块
│   └── init_db.py       # 数据库初始化
├── frontend/            # Vue3前端
│   ├── src/
│   │   ├── views/       # 页面组件
│   │   ├── api/         # API请求
│   │   └── router/      # 路由配置
│   └── package.json
├── docker/              # 漏洞环境
│   ├── build-images.sh  # 构建脚本
│   └── */               # 各漏洞环境
├── start.sh             # 服务管理脚本
└── requirements.txt     # Python依赖
```

## 开发指南

### 后端开发

```bash
cd backend
python app.py  # 开发模式
```

### 前端开发

```bash
cd frontend
npm run dev    # 开发模式
npm run build  # 生产构建
```

## LICENSE

MIT License
