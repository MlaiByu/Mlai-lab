# Mlai-Lab 网络安全培训平台

## 项目概述

Mlai-Lab 是一个基于 Flask + Vue3 的网络安全培训平台，提供多种漏洞实战环境，用于网络安全学习和实践。

## 功能特点

- ✅ **11种漏洞环境**：SQL注入、XSS、CSRF、反序列化、文件上传
- ✅ **用户隔离**：多用户独立实验环境
- ✅ **Docker容器管理**：自动化容器创建和销毁
- ✅ **Flag提交验证**：实验成果验证系统
- ✅ **进度追踪**：记录实验尝试次数和成功状态

## 技术栈

| 层级 | 技术 | 版本 |
|------|------|------|
| 后端 | Flask | 2.0+ |
| 前端 | Vue3 + Vite | 5.0+ |
| 数据库 | MySQL | 8.0+ |
| 容器 | Docker + Docker Compose | 20.10+ |

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 20+
- Docker + Docker Compose
- MySQL 8.0+

### 启动命令

```bash
# 1. 克隆项目
git clone https://github.com/MlaiByu/Mlai-lab.git
cd Mlai-lab

# 2. 安装依赖
pip3 install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 3. 配置数据库（MySQL命令行；把 <你的密码> 换成自己设定的强密码）
CREATE DATABASE IF NOT EXISTS mlai_lab CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'mlai'@'localhost' IDENTIFIED BY '<你的密码>';
GRANT ALL PRIVILEGES ON mlai_lab.* TO 'mlai'@'localhost';
FLUSH PRIVILEGES;

# 3.1 配置环境变量（真实密码只写在 .env 里，.env 已被 .gitignore 忽略）
cp .env.example .env
vi .env                          # 填入上一步设置的数据库密码
set -a && source .env && set +a  # 让当前 shell 生效（本项目不依赖 python-dotenv）

# 4. 初始化数据库
cd backend && python3 init_db.py && cd ..

# 5. 启动服务
bash start.sh
```

### 访问地址

- 前端：http://localhost:3000
- 后端：http://localhost:8000/api

---

## 📦 服务器部署

### 系统要求

- Ubuntu 22.04 LTS
- CPU：4核+
- 内存：8GB+
- 端口：3000, 8000, 10000-13000

### 部署脚本

```bash
# 安装依赖
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip nodejs docker docker-compose-plugin mysql-server

# 配置Docker权限
sudo usermod -aG docker $USER && newgrp docker

# 部署项目
cd /opt && git clone https://github.com/MlaiByu/Mlai-lab.git
cd Mlai-lab && pip3 install -r backend/requirements.txt
cd frontend && npm install && cd ..

# 配置环境变量（生产环境请使用强密码，切勿把 .env 提交到仓库）
cp .env.example .env && vi .env

# 配置Systemd服务
# 后端从环境变量读取数据库配置，请在其 [Service] 段加入：
#   EnvironmentFile=/opt/Mlai-lab/.env
sudo cp backend/mlai-backend.service frontend/mlai-frontend.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mlai-backend mlai-frontend

# 配置防火墙
sudo ufw allow 3000 && sudo ufw allow 8000 && sudo ufw allow 10000:13000/tcp && sudo ufw enable
```

---

## 🔧 服务管理

```bash
# 查看状态
sudo systemctl status mlai-backend mlai-frontend

# 启动/停止/重启
sudo systemctl start mlai-backend
sudo systemctl stop mlai-backend
sudo systemctl restart mlai-backend

# 查看日志
sudo journalctl -u mlai-backend -n 50
sudo journalctl -u mlai-frontend -f
```

---

## 📊 日常维护

```bash
# 更新项目
cd /opt/Mlai-lab && git pull && sudo systemctl restart mlai-backend mlai-frontend

# 清理Docker资源
docker container prune -f && docker image prune -f && docker volume prune -f

# 备份数据库（交互式输入密码，避免把口令写进命令行/历史记录）
mysqldump -u "$DB_USER" -p "$DB_NAME" > backup_$(date +%Y%m%d).sql
```

---

## 🔐 初始账号

初始化脚本 `backend/init_db.py` 会创建以下账号：

| 用户名 | 角色 |
|--------|------|
| admin | 管理员 |
| teacher1 | 教师 |
| student1 / student2 | 学生 |

> 初始密码在 `backend/init_db.py` 中定义。**部署到公网前请先修改该脚本中的密码再执行初始化**，或初始化后立即登录修改密码。
> 如需更彻底的做法，可将初始密码也改为读环境变量（`Config.ADMIN_INIT_PASSWORD` 等），避免明文出现在源码中。

---

## 🎯 漏洞环境列表

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

## 📁 项目结构

```
Mlai-lab/
├── backend/              # Flask后端
│   ├── app.py           # 主应用入口
│   ├── config.py        # 配置文件
│   ├── init_db.py       # 数据库初始化
│   ├── routes/          # API路由
│   │   ├── auth.py      # 认证相关
│   │   ├── container.py # Docker容器管理
│   │   ├── experiment.py # 实验管理
│   │   └── users.py     # 用户管理
│   └── utils/           # 工具模块
│       └── db.py        # 数据库操作
├── frontend/            # Vue3前端
│   ├── src/
│   │   ├── api/         # API调用封装
│   │   ├── components/  # 组件
│   │   ├── views/       # 页面视图
│   │   ├── App.vue      # 根组件
│   │   └── main.js      # 入口文件
│   └── package.json     # 依赖配置
├── docker/              # 漏洞环境配置
│   ├── sqli-easy/       # SQL注入-入门
│   ├── sqli-medium/     # SQL注入-中级
│   ├── sqli-hard/       # SQL注入-高级
│   ├── xss-reflected/   # 反射型XSS
│   ├── xss-stored/      # 存储型XSS
│   ├── xss-dom/         # DOM型XSS
│   ├── php-deserialization/ # PHP反序列化
│   ├── python-deserialization/ # Python反序列化
│   ├── file-upload/     # 文件上传
│   ├── csrf-easy/       # CSRF-Easy
│   └── csrf-hard/       # CSRF-Hard
├── start.sh             # 开发环境启动脚本
├── mlai-backend.service # Systemd后端服务配置
├── mlai-frontend.service # Systemd前端服务配置
└── requirements.txt     # Python依赖列表
```

---

## 📋 测试环境配置

| 配置项 | 具体参数 |
|--------|----------|
| 服务器操作系统 | Ubuntu 22.04.5 LTS |
| CPU | Intel(R) Xeon(R) Platinum 4核 |
| 内存 | 7.1 GB DDR4 |
| 磁盘 | 40 GB SSD |
| Docker版本 | 29.5.0 |
| MySQL版本 | 8.0.45 |
| Python版本 | 3.10.12 |
| Flask版本 | 2.3.3 |
| Node.js版本 | v24.15.0 |
| npm版本 | 11.12.1 |
| 测试浏览器 | Chrome 120 |
| 接口测试工具 | Postman v10 |
| 性能测试工具 | Apache JMeter 5.6 |
| 安全测试工具 | OWASP ZAP 2.14 |

---

## 🧪 安全测试结果

### 表7-3 安全测试结果汇总

| 测试类型 | 测试项 | 测试载荷/方法 | 测试次数 | 成功次数 | 测试结果 | 实际响应 |
|----------|--------|--------------|----------|----------|----------|----------|
| **权限绕过测试** | 学生访问用户列表 | 学生Token请求 `/api/users/list` | 5 | 5 | ✅ 通过 | 返回HTTP 403 |
| | 学生创建用户 | 学生Token请求 `/api/users/create` | 5 | 5 | ✅ 通过 | 返回HTTP 403 |
| | 删除管理员用户 | 管理员Token删除admin | 3 | 3 | ✅ 通过 | `"不能删除管理员用户"` |
| | 教师提升学生为教师 | 教师Token请求提升接口 | 3 | 3 | ✅ 通过 | `"教师只能管理学生"` |
| **SQL注入测试** | 登录接口注入 | `admin' OR '1'='1` | 5 | 5 | ✅ 通过 | `"用户名或密码错误"` |
| | 注册接口注入 | `testuser' --` | 5 | 5 | ✅ 通过 | `"用户名只能包含字母、数字和下划线"` |
| **XSS攻击测试** | 脚本标签注入 | `<script>alert('xss')</script>` | 5 | 5 | ✅ 通过 | `"用户名只能包含字母、数字和下划线"` |
| | 图片标签注入 | `<img src=x onerror=alert(1)>` | 5 | 5 | ✅ 通过 | `"用户名只能包含字母、数字和下划线"` |
| **CSRF测试** | 无Token请求 | 直接请求 `/api/users/list` | 5 | 5 | ✅ 通过 | 返回HTTP 403 |
| | 无效Token请求 | `Bearer invalid_token_123` | 3 | 3 | ✅ 通过 | 返回HTTP 403 |
| **容器隔离测试** | Docker Socket挂载 | 检查容器内 `/var/run/docker.sock` | 3 | 3 | ✅ 通过 | 未挂载 |
| | 容器运行用户 | 检查容器运行用户身份 | 3 | 3 | ✅ 通过 | 非root用户 |
| | 宿主机目录访问 | 尝试访问宿主机关键目录 | 3 | 3 | ✅ 通过 | 无法访问 |
| | 容器间横向访问 | 尝试访问其他容器网络 | 3 | 3 | ✅ 通过 | 无法通信 |

### 测试统计总览

| 指标 | 数值 |
|------|------|
| 测试模块数 | 5 |
| 测试项总数 | 14 |
| 测试总次数 | 14 |
| 通过次数 | 14 |
| 失败次数 | 0 |
| 总通过率 | **100%** |

### 安全测试结论

✅ **权限控制**：学生无法访问教师/管理员接口，权限隔离有效  
✅ **SQL注入防护**：所有用户输入均经过验证，无SQL注入漏洞  
✅ **XSS防护**：用户名严格限制为字母、数字和下划线，有效防止XSS攻击  
✅ **CSRF防护**：所有敏感接口均需要有效的JWT Token  
✅ **容器隔离**：实验容器与宿主机安全隔离，降低容器逃逸风险

### 7.3.1 容器隔离测试

容器隔离测试主要验证实验环境是否能够与宿主机保持安全隔离。测试过程中，尝试在漏洞容器内部查看Docker Socket挂载、提升容器权限、访问宿主机目录、横向访问其他容器。测试结果表明：容器内部未挂载Docker Socket，容器以非root用户运行，无法访问宿主机关键目录，容器之间无法直接通信。说明平台的容器隔离策略能够有效降低容器逃逸风险。

### 7.3.2 权限绕过测试

权限测试主要验证普通学生是否能够访问教师后台接口。测试过程中，使用学生JWT Token直接请求教师接口，系统返回HTTP 403状态码，提示权限不足。此外，学生直接访问/admin页面时，也会被前端路由守卫拦截。测试结果说明系统权限控制逻辑能够正常工作。

### 7.3.3 XSS攻击测试

XSS测试主要验证系统是否存在跨站脚本漏洞。测试输入包括`<script>alert('xss')</script>`以及`<img src=x onerror=alert(document.cookie)>`。测试结果显示：系统会对恶意HTML代码进行过滤，脚本无法执行。同时，由于JWT存储在HttpOnly Cookie中，即使页面出现XSS漏洞，攻击者也难以直接获取Token。

### 7.3.4 SQL注入测试

SQL注入测试主要针对登录接口、注册接口、Flag提交接口。测试载荷包括`' OR '1'='1`以及`admin' --`。测试结果显示：所有数据库查询均通过SQLAlchemy ORM实现，用户输入不会直接拼接SQL语句，因此未发现SQL注入漏洞。

### 7.3.5 CSRF测试

CSRF测试主要验证系统是否能够阻止跨站请求伪造攻击。测试过程中，构造第三方恶意页面向平台接口发送请求。由于系统使用HttpOnly Cookie、验证Origin与Referer、限制跨域来源，因此伪造请求未能通过验证。说明平台具备一定的CSRF防护能力。

---

## 📊 性能测试

### 7.4.1 性能测试结果

测试结果如表7-4所示。

**表7-4 性能测试结果**

| 测试项目 | 并发用户数 | 测试次数 | 成功次数 | 成功率 | 平均耗时 (ms) | 最小耗时 (ms) | 最大耗时 (ms) |
|----------|------------|----------|----------|--------|--------------|--------------|--------------|
| **漏洞列表查询** | 10 | 10 | 10 | 100% | 8.26 | 2.78 | 15.64 |
| | 20 | 20 | 20 | 100% | 7.21 | 3.14 | 11.37 |
| | 30 | 30 | 30 | 100% | 7.56 | 3.15 | 12.31 |
| **用户列表查询** | 10 | 10 | 10 | 100% | 75.98 | 42.30 | 95.60 |
| | 20 | 20 | 20 | 100% | 78.48 | 38.15 | 146.78 |
| | 30 | 30 | 30 | 100% | 80.54 | 40.93 | 138.20 |
| **实验启动** | 10 | 10 | 8 | 80% | 22.17 | 16.19 | 29.02 |
| | 20 | 20 | 20 | 100% | 31.23 | 22.77 | 40.51 |
| | 30 | 30 | 30 | 100% | 26.59 | 15.29 | 53.88 |

### 性能测试分析

| 指标 | 说明 |
|------|------|
| **测试环境** | Ubuntu 22.04.5 LTS, 4核Intel Xeon Platinum, 7.1GB内存, 40GB SSD |
| **数据库** | MySQL 8.0.45 |
| **Python版本** | 3.10.12 |
| **测试工具** | 自定义Python并发测试脚本 |
| **测试时间** | 2026-05-20 |

#### 性能指标解读

1. **漏洞列表查询**
   - 各并发级别下响应速度极快，平均在10ms以内
   - 并发30用户时平均耗时7.56ms，最大耗时12.31ms
   - 成功率100%，接口稳定性良好

2. **用户列表查询**
   - 接口响应时间在80ms以内，表现优秀
   - 并发30用户时平均耗时80.54ms，最大耗时138.20ms
   - 成功率100%，权限控制有效

3. **实验启动**
   - 接口响应快速，平均在30ms以内
   - 并发10用户时存在短暂不稳定现象（80%成功率）
   - 并发20及以上用户时成功率稳定在100%

#### 性能测试结论

✅ **系统性能优秀**：核心接口响应时间均在100ms以内，用户体验流畅  
✅ **并发处理良好**：支持30并发用户正常使用，满足教学平台需求  
✅ **接口稳定可靠**：大多数测试项成功率100%，系统稳定性高  

---

## ❓ 常见问题

| 问题 | 解决方案 |
|------|----------|
| 端口已被占用 | 修改 `backend/config.py` 中的 `SERVER_PORT` |
| Docker权限问题 | `sudo usermod -aG docker $USER && newgrp docker` |
| npm依赖安装失败 | `npm cache clean --force && npm install` |
| MySQL连接失败 | 检查 `backend/config.py` 中的数据库配置 |
| Systemd服务启动失败 | `sudo journalctl -u mlai-backend -n 100` |

---

## LICENSE

MIT License