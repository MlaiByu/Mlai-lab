# Mlai-Lab 网络安全培训平台

## 项目概述

Mlai-Lab 是一个基于 Flask + Vue3 的网络安全培训平台，提供多种漏洞实战环境，用于网络安全学习和实践。

## 功能特点

- ✅ **11种漏洞环境**：SQL注入、XSS、CSRF、反序列化、文件上传
- ✅ **用户隔离**：多用户独立实验环境
- ✅ **Docker容器管理**：自动化容器创建和销毁
- ✅ **Flag提交验证**：实验成果验证系统
- ✅ **进度追踪**：记录实验尝试次数和成功状态
- ✅ **随机端口分配**：10000-65535端口范围

## 当前运行状态

- **后端服务**: http://localhost:8000
- **前端服务**: http://localhost:3000
- **数据库**: MySQL
- **漏洞环境**: Docker容器

---

## 📝 本地测试（开发环境）

### 环境要求

- Python 3.10+
- Node.js 20+
- Docker + Docker Compose
- MySQL 8.0+

### 本地启动步骤

#### 1. 克隆项目

```bash
git clone https://github.com/MlaiByu/Mlai-lab.git
cd Mlai-lab
```

#### 2. 安装Python依赖

```bash
pip install -r requirements.txt
```

#### 3. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

#### 4. 配置MySQL数据库

```bash
mysql -u root -p
```

执行以下SQL：
```sql
CREATE DATABASE IF NOT EXISTS mlai_lab;
CREATE USER IF NOT EXISTS 'Mlai'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON mlai_lab.* TO 'Mlai'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 5. 初始化数据库表

```bash
cd backend
python3 init_db.py
cd ..
```

#### 6. 启动服务

```bash
chmod +x start.sh
./start.sh start
```

#### 7. 访问应用

- **前端**: http://localhost:3000
- **后端**: http://localhost:8000

---

## 🚀 服务器部署（持久化运行）

### 服务器要求

- 操作系统：Ubuntu 22.04 LTS
- CPU：4核+
- 内存：8GB+
- 磁盘：50GB+
- 开放端口：3000, 8000, 10000-65535

### 部署步骤

#### 第一步：准备服务器环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git curl wget vim

# 安装Python 3
sudo apt install -y python3 python3-pip python3-venv

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 安装Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker

# 安装Docker Compose
sudo apt install -y docker-compose-plugin

# 安装MySQL
sudo apt install -y mysql-server
sudo mysql_secure_installation
```

#### 第二步：配置MySQL

```bash
sudo mysql -u root -p
```

```sql
CREATE DATABASE IF NOT EXISTS mlai_lab;
CREATE USER IF NOT EXISTS 'Mlai'@'localhost' IDENTIFIED BY '1234';
GRANT ALL PRIVILEGES ON mlai_lab.* TO 'Mlai'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 第三步：部署项目

```bash
cd /opt
sudo git clone https://github.com/MlaiByu/Mlai-lab.git
sudo chown -R $USER:$USER Mlai-lab
cd Mlai-lab
```

#### 第四步：安装依赖

```bash
pip3 install -r requirements.txt

cd frontend
npm install
cd ..
```

#### 第五步：初始化数据库

```bash
cd backend
python3 init_db.py
cd ..
```

#### 第六步：配置Systemd服务

```bash
sudo cp mlai-backend.service /etc/systemd/system/
sudo cp mlai-frontend.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable mlai-backend mlai-frontend
sudo systemctl start mlai-backend mlai-frontend
```

#### 第七步：配置防火墙

```bash
sudo ufw allow 3000
sudo ufw allow 8000
sudo ufw allow 10000:65535/tcp
sudo ufw enable
```

---

## 🛠️ Systemd服务管理命令

```bash
# 查看状态
sudo systemctl status mlai-backend
sudo systemctl status mlai-frontend

# 启动/停止/重启
sudo systemctl start mlai-backend
sudo systemctl stop mlai-backend
sudo systemctl restart mlai-backend

# 查看日志
sudo journalctl -u mlai-backend -n 50
sudo journalctl -u mlai-frontend -f

# 禁用/启用开机自启
sudo systemctl disable mlai-backend
sudo systemctl enable mlai-backend
```

---

## 📊 日常维护

### 更新项目

```bash
cd /opt/Mlai-lab
git pull
sudo systemctl restart mlai-backend mlai-frontend
```

### 清理Docker资源

```bash
docker container prune -f
docker image prune -f
docker volume prune -f
```

### 备份数据库

```bash
mysqldump -u Mlai -p mlai_lab > backup_$(date +%Y%m%d).sql
```

---

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | password | 管理员 |
| teacher1 | teacherpass | 教师 |
| student1 | 123456 | 学生 |
| student2 | 123456 | 学生 |

---

## 漏洞环境列表

| 编号 | 漏洞名称 | 类型 | 难度 |
|------|----------|------|------|
| 1 | SQL注入-入门 | SQL注入 | ⭐ |
| 2 | SQL注入-中级 | SQL注入 | ⭐⭐ |
| 3 | SQL注入-高级 | SQL注入 | ⭐⭐⭐ |
| 4 | 反射型XSS | XSS攻击 | ⭐ |
| 5 | 存储型XSS | XSS攻击 | ⭐⭐ |
| 6 | DOM型XSS | XSS攻击 | ⭐ |
| 7 | PHP反序列化 | 反序列化 | ⭐⭐⭐ |
| 8 | Python反序列化 | 反序列化 | ⭐⭐⭐ |
| 9 | 文件上传 | 文件上传 | ⭐⭐ |
| 10 | CSRF-Easy | CSRF攻击 | ⭐ |
| 11 | CSRF-Hard | CSRF攻击 | ⭐⭐ |

---

## 项目结构

```
Mlai-lab/
├── backend/                    # Flask后端
│   ├── app.py                 # 主应用入口
│   ├── config.py              # 配置文件
│   ├── init_db.py             # 数据库初始化
│   ├── routes/                # API路由
│   │   ├── auth.py            # 认证相关
│   │   ├── container.py       # Docker容器管理
│   │   ├── experiment.py      # 实验管理
│   │   └── users.py           # 用户管理
│   └── utils/                 # 工具模块
│       └── db.py              # 数据库操作
├── frontend/                  # Vue3前端
│   ├── src/
│   │   ├── api/               # API调用封装
│   │   ├── components/        # 组件
│   │   ├── store/             # 状态管理
│   │   ├── views/             # 页面视图
│   │   ├── App.vue            # 根组件
│   │   └── main.js            # 入口文件
│   └── package.json           # 依赖配置
├── docker/                    # 漏洞环境配置
│   ├── sqli-easy/             # SQL注入-入门
│   ├── sqli-medium/           # SQL注入-中级
│   ├── sqli-hard/             # SQL注入-高级
│   ├── xss-reflected/         # 反射型XSS
│   ├── xss-stored/            # 存储型XSS
│   ├── xss-dom/               # DOM型XSS
│   ├── deserialization-php/   # PHP反序列化
│   ├── deserialization-python/# Python反序列化
│   ├── upload/                # 文件上传
│   └── csrf/                  # CSRF攻击
├── start.sh                   # 开发环境启动脚本
├── mlai-backend.service       # Systemd后端服务配置
├── mlai-frontend.service      # Systemd前端服务配置
└── requirements.txt           # Python依赖列表
```

---

## 数据库表结构

### users（用户表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 用户ID（主键） |
| username | VARCHAR(100) | 用户名 |
| password | VARCHAR(255) | 密码（SHA256加密） |
| role | VARCHAR(20) | 角色（admin/teacher/student） |
| score | INT | 积分 |
| created_at | DATETIME | 创建时间 |
| last_login | DATETIME | 最后登录时间 |

### vulnerabilities（漏洞表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 漏洞ID（主键） |
| name | VARCHAR(100) | 漏洞名称 |
| flag | VARCHAR(255) | 验证Flag |
| category | VARCHAR(50) | 漏洞类别 |
| difficulty | VARCHAR(20) | 难度等级 |

### experiment_records（实验记录表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 记录ID（主键） |
| user_id | INT | 用户ID |
| vulnerability_id | INT | 漏洞ID |
| attempt_count | INT | 尝试次数 |
| success | INT | 成功次数 |
| last_attempt | DATETIME | 最后尝试时间 |
| first_success | DATETIME | 首次成功时间 |

### experiment_sessions（实验会话表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 会话ID（主键） |
| session_id | VARCHAR(255) | 会话UUID |
| user_id | INT | 用户ID |
| vulnerability_id | INT | 漏洞ID |
| docker_container_id | VARCHAR(100) | Docker容器ID |
| server_port | INT | 服务器端口 |
| start_time | DATETIME | 开始时间 |
| end_time | DATETIME | 结束时间 |
| success | INT | 是否成功（0/1） |

---

## 常见问题

### 端口已被占用
修改 `backend/app.py` 或 `frontend/vite.config.js` 中的端口配置。

### Docker权限问题
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### npm依赖安装失败
```bash
cd frontend
npm cache clean --force
npm install
```

### MySQL连接失败
```bash
sudo systemctl status mysql
```

### Systemd服务启动失败
```bash
sudo journalctl -u mlai-backend -n 100
```

---

## LICENSE

MIT License