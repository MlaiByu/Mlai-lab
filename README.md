# Mlai-Lab 网络安全培训平台

## 项目简介

Mlai-Lab 是一个网络安全培训平台，提供多种漏洞环境供学习者进行实战练习。

### 主要功能

- 用户认证系统（注册、登录、角色管理）
- 9个漏洞实验环境（SQL注入、XSS、反序列化、文件上传等）
- 实验记录管理（开始时间、结束时间、成功状态）
- 个人学习进度追踪
- 教师端查看学生完成情况

### 技术栈

**后端**: Python 3.10+ / Flask 2.3.3 / SQLite / JWT
**前端**: Vue 3 / Vite 5 / Element Plus / Vue Router
**容器化**: Docker（仅漏洞环境）

---

## 项目结构

```
Mlai-Lab/
├── backend/                    # 后端服务（服务器直接运行）
│   ├── app.py                 # Flask应用入口
│   ├── config.py              # 配置文件
│   ├── init_db.py             # 数据库初始化
│   ├── routes/                # 路由模块
│   │   ├── auth.py           # 认证
│   │   ├── container.py      # Docker容器管理
│   │   ├── experiment.py     # 实验记录
│   │   ├── health.py          # 健康检查
│   │   └── users.py          # 用户管理
│   └── utils/
│       └── db.py             # 数据库操作
├── frontend/                  # 前端服务（服务器直接运行）
│   ├── src/                  # 源代码
│   │   ├── api/              # API调用
│   │   ├── components/        # 组件
│   │   ├── router/           # 路由
│   │   ├── store/            # 状态管理
│   │   └── views/            # 页面
│   └── vite.config.js        # Vite配置
├── docker/                    # Docker漏洞环境
│   ├── sqli-easy/            # SQL注入-入门
│   ├── sqli-medium/          # SQL注入-中级
│   ├── sqli-hard/            # SQL注入-高级
│   ├── xss-reflected/        # 反射型XSS
│   ├── xss-stored/           # 存储型XSS
│   ├── xss-dom/              # DOM型XSS
│   ├── php-deserialization/   # PHP反序列化
│   ├── python-deserialization/ # Python反序列化
│   ├── file-upload/           # 文件上传
│   └── build-images.sh        # 镜像构建脚本
├── requirements.txt           # Python依赖
├── start-services.sh         # 服务管理脚本
└── README.md
```

---

## 快速开始

### 1. 安装依赖

```bash
# 后端依赖
pip install -r requirements.txt

# 前端依赖
cd frontend && npm install
```

### 2. 启动服务

```bash
# 启动所有服务
./start-services.sh start

# 查看服务状态
./start-services.sh status

# 停止服务
./start-services.sh stop
```

### 3. 访问

- 前端：http://8.136.148.183:3000
- 后端：http://8.136.148.183:8000

### 4. 默认账号

- 管理员：admin / admin123
- 学生：student / student123

---

## Docker漏洞环境

首次使用需要构建镜像：

```bash
cd docker
./build-images.sh
```

---

## 服务管理

```bash
./start-services.sh start    # 启动服务
./start-services.sh stop     # 停止服务
./start-services.sh restart  # 重启服务
./start-services.sh status   # 查看状态
```

---

## 漏洞环境列表

| 编号 | 漏洞名称 | 难度 |
|------|----------|------|
| 1 | SQL注入-入门 | ⭐ |
| 2 | SQL注入-中级 | ⭐⭐ |
| 3 | SQL注入-高级 | ⭐⭐⭐ |
| 4 | 反射型XSS | ⭐ |
| 5 | 存储型XSS | ⭐⭐ |
| 6 | DOM型XSS | ⭐⭐ |
| 7 | PHP反序列化 | ⭐⭐ |
| 8 | Python反序列化 | ⭐⭐⭐ |
| 9 | 文件上传 | ⭐ |

---

## API接口

### 认证
- `POST /api/auth/register` - 注册
- `POST /api/auth/login` - 登录
- `GET /api/auth/userinfo` - 用户信息

### 容器
- `POST /api/container/create` - 创建容器
- `POST /api/container/remove/<id>` - 删除容器
- `POST /api/container/get_by_vuln` - 获取容器

### 实验
- `POST /api/experiment/start` - 开始实验
- `POST /api/experiment/complete` - 完成实验
- `POST /api/experiment/stop` - 停止实验

---

## 注意事项

1. Docker靶场端口限制在10000-13000范围内
2. 容器默认1小时后自动过期
3. 漏洞环境运行在Docker中，前后端直接运行在服务器