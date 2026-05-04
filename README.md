# Mlai-Lab 网络安全培训平台

## 项目概述

Mlai-Lab 是一个网络安全培训平台，提供9种漏洞实战环境，用于网络安全学习和实践。

## 功能特点

- ✅ 9种漏洞环境（SQL注入、XSS、反序列化、文件上传）
- ✅ 用户隔离，多用户独立实验
- ✅ 随机端口分配（10000-13000）
- ✅ Flag提交验证
- ✅ 真实MySQL数据库环境
- ✅ Docker容器自动化管理

## 当前环境

- **后端服务**: 运行在 0.0.0.0:8000
- **前端服务**: 运行在 0.0.0.0:3000
- **数据库**: MySQL
- **漏洞环境**: Docker

---

## 📝 本地测试（开发环境）

### 环境要求

- Python 3.8+
- Node.js 16+
- Docker + Docker Compose
- MySQL

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

#### 8. 本地测试检查清单

- [ ] 服务启动成功（无报错）
- [ ] 可以访问 http://localhost:3000
- [ ] 可以使用 admin/password 登录
- [ ] 可以进入 Challenges 页面
- [ ] 可以启动一个漏洞环境（如SQL注入-入门）
- [ ] 容器正常运行，端口可访问
- [ ] Flag提交功能正常

---

## 🚀 服务器部署（持久化运行）

### 服务器要求

- 操作系统：Ubuntu 20.04/22.04 或 CentOS 7/8
- CPU：2核+
- 内存：4GB+
- 磁盘：20GB+
- 开放端口：3000, 8000, 10000-13000

### 服务器部署步骤

#### 第一步：准备服务器环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git curl wget vim

# 安装Python 3
sudo apt install -y python3 python3-pip python3-venv

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装Docker
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER

# 安装Docker Compose
sudo apt install -y docker-compose

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

#### 第六步：配置Systemd服务（持久化核心）

**复制服务文件：**
```bash
sudo cp mlai-backend.service /etc/systemd/system/
sudo cp mlai-frontend.service /etc/systemd/system/
```

**重载并启用服务：**
```bash
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable mlai-backend
sudo systemctl enable mlai-frontend

# 启动服务
sudo systemctl start mlai-backend
sudo systemctl start mlai-frontend

# 查看状态
sudo systemctl status mlai-backend mlai-frontend
```

#### 第七步：配置防火墙

```bash
# Ubuntu (ufw)
sudo ufw allow 3000
sudo ufw allow 8000
sudo ufw allow 10000:13000/tcp
sudo ufw enable

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-port=3000/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --permanent --add-port=10000-13000/tcp
sudo firewall-cmd --reload
```

#### 第八步：访问验证

```bash
# 检查服务状态
sudo systemctl status mlai-backend mlai-frontend

# 检查端口监听
ss -tlnp | grep -E ":(3000|8000)"

# 查看服务日志
sudo journalctl -u mlai-backend -f
sudo journalctl -u mlai-frontend -f
```

访问：http://your-server-ip:3000

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

# 重启服务
sudo systemctl restart mlai-backend mlai-frontend
```

### 清理Docker容器

```bash
# 清理所有停止的容器
docker container prune -f

# 清理未使用的镜像
docker image prune -f
```

### 备份数据库

```bash
mysqldump -u Mlai -p mlai_lab > backup_$(date +%Y%m%d).sql
```

---

## 默认账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | password | 教师 |
| user | userpass | 学生 |

---

## 服务管理命令（开发环境）

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

---

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

---

## 快速命令汇总

### 本地测试

```bash
git clone https://github.com/MlaiByu/Mlai-lab.git
cd Mlai-lab
pip install -r requirements.txt
cd frontend && npm install && cd ..
cd backend && python3 init_db.py && cd ..
chmod +x start.sh
./start.sh start
```

### 服务器部署

```bash
# 1. 环境准备
sudo apt update
sudo apt install -y git python3 python3-pip nodejs docker.io docker-compose mysql-server

# 2. MySQL配置
sudo mysql -u root -p
# 执行创建数据库和用户的SQL

# 3. 部署项目
cd /opt
sudo git clone https://github.com/MlaiByu/Mlai-lab.git
sudo chown -R $USER:$USER Mlai-lab
cd Mlai-lab
pip3 install -r requirements.txt
cd frontend && npm install && cd ..
cd backend && python3 init_db.py && cd ..

# 4. 配置Systemd
sudo cp mlai-backend.service /etc/systemd/system/
sudo cp mlai-frontend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mlai-backend mlai-frontend
sudo systemctl start mlai-backend mlai-frontend

# 5. 防火墙
sudo ufw allow 3000
sudo ufw allow 8000
sudo ufw allow 10000:13000/tcp
sudo ufw enable
```

---

## 项目结构

```
Mlai-lab/
├── backend/              # Flask后端
│   ├── app.py           # 主应用
│   ├── routes/          # API路由
│   │   ├── container.py # Docker容器管理
│   │   └── ...
│   ├── utils/           # 工具模块
│   └── init_db.py       # 数据库初始化
├── frontend/            # Vue3前端
│   ├── src/
│   │   ├── views/      # 页面
│   │   └── api/        # API调用
│   └── package.json
├── docker/              # 漏洞环境
│   ├── sqli-easy/      # SQL注入-入门
│   ├── sqli-medium/    # SQL注入-中级
│   ├── sqli-hard/      # SQL注入-高级
│   ├── xss-reflected/  # 反射型XSS
│   ├── xss-stored/     # 存储型XSS
│   ├── xss-dom/        # DOM型XSS
│   ├── php-deserialization/  # PHP反序列化
│   ├── python-deserialization/ # Python反序列化
│   └── file-upload/    # 文件上传
├── start.sh            # 服务管理脚本（开发）
├── mlai-backend.service  # Systemd后端服务
├── mlai-frontend.service # Systemd前端服务
└── requirements.txt
```

---

## 常见问题

### 端口已被占用

修改 `backend/app.py` 或 `frontend/vite.config.js` 中的端口配置。

### Docker权限问题

确保当前用户在 docker 用户组中：
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### npm依赖安装失败

尝试清理缓存：
```bash
cd frontend
npm cache clean --force
npm install
```

### MySQL连接失败

检查MySQL服务是否启动，用户名和密码是否正确：
```bash
sudo systemctl status mysql
```

### Systemd服务启动失败

查看日志：
```bash
sudo journalctl -u mlai-backend -n 100
```

---

## LICENSE

MIT License

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
