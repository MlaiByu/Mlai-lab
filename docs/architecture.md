# Mlai-Lab B/S 架构与前后端分离技术

## 目录
1. [系统总体架构](#系统总体架构)
2. [技术栈详解](#技术栈详解)
3. [前后端通信流程](#前后端通信流程)
4. [数据流程图](#数据流程图)
5. [部署架构](#部署架构)

---

## 系统总体架构

```mermaid
graph TB
    subgraph "客户端层 (Browser)"
        A[用户浏览器<br>Chrome/Firefox/Safari]
    end
    
    subgraph "前端层 (Frontend)"
        B[Vue 3 应用<br>单页应用 SPA]
        C[Element Plus UI<br>组件库]
        D[Vue Router<br>路由管理]
        E[Vuex Store<br>状态管理]
        F[Axios<br>HTTP客户端]
    end
    
    subgraph "网关层 (Gateway)"
        G[Vite Dev Server<br>开发环境代理]
        H[Nginx<br>生产环境反向代理]
    end
    
    subgraph "后端层 (Backend)"
        I[Flask 应用<br>RESTful API]
        J[Flask-CORS<br>跨域处理]
        K[路由模块<br>Routes]
        L[业务逻辑<br>Business Logic]
    end
    
    subgraph "数据层 (Data)"
        M[MySQL 数据库<br>持久化存储]
        N[Docker Daemon<br>容器运行时]
    end
    
    A -->|HTTP/HTTPS| B
    B --> C
    B --> D
    B --> E
    E --> F
    F -->|HTTP请求<br>JSON格式| G
    G -->|代理转发| I
    F -->|生产环境| H
    H -->|反向代理| I
    I --> J
    I --> K
    K --> L
    L -->|SQL操作| M
    L -->|容器API| N
    N -->|返回容器状态| L
    M -->|返回数据| L
    L -->|JSON响应| K
    K -->|JSON响应| I
    I -->|JSON响应| G
    I -->|JSON响应| H
    G -->|JSON响应| F
    H -->|JSON响应| F
    F -->|更新数据| E
    E -->|更新视图| B
    B -->|渲染页面| A
```

---

## 技术栈详解

### 前端技术栈

| 技术 | 版本 | 用途 | 文件位置 |
|------|------|------|---------|
| Vue 3 | ^3.3.13 | 核心框架，组件化开发 | [package.json](file:///home/yu/Mlai-lab/frontend/package.json#L11) |
| Vue Router | ^4.2.5 | 单页应用路由管理 | [package.json](file:///home/yu/Mlai-lab/frontend/package.json#L12) |
| Element Plus | ^2.3.12 | UI组件库 | [package.json](file:///home/yu/Mlai-lab/frontend/package.json#L13) |
| Vite | ^5.0.8 | 构建工具，开发服务器 | [vite.config.js](file:///home/yu/Mlai-lab/frontend/vite.config.js#L5) |

### 后端技术栈

| 技术 | 用途 | 文件位置 |
|------|------|---------|
| Flask | Web框架，RESTful API | [app.py](file:///home/yu/Mlai-lab/backend/app.py#L8) |
| Flask-CORS | 跨域资源共享 | [app.py](file:///home/yu/Mlai-lab/backend/app.py#L9) |
| MySQL | 关系型数据库 | [init_db.py](file:///home/yu/Mlai-lab/backend/init_db.py) |
| Docker SDK | 容器管理 | [routes/container.py](file:///home/yu/Mlai-lab/backend/routes/container.py) |

### 代理配置

开发环境通过 Vite 代理解决跨域问题：

```javascript
// vite.config.js
server: {
  port: 3000,
  proxy: {
    '/api': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true
    }
  }
}
```

---

## 前后端通信流程

### 完整请求-响应流程

```mermaid
sequenceDiagram
    participant User as 用户
    participant Vue as Vue组件
    participant Store as Vuex Store
    participant Api as API模块
    participant Vite as Vite代理
    participant Flask as Flask后端
    participant DB as MySQL
    participant Docker as Docker容器

    User->>Vue: 用户操作(点击/输入)
    Vue->>Store: 触发 Action
    Store->>Api: 调用 API 函数
    Api->>Vite: HTTP 请求 (JSON)
    
    Vite->>Flask: 代理转发请求
    Flask->>Flask: Flask-CORS 跨域处理
    Flask->>Flask: 路由匹配
    
    alt 数据查询
        Flask->>DB: SQL 查询
        DB-->>Flask: 返回数据
    else 容器操作
        Flask->>Docker: Docker API 调用
        Docker-->>Flask: 返回容器状态
    end
    
    Flask-->>Vite: JSON 响应
    Vite-->>Api: JSON 响应
    Api-->>Store: 解析数据
    Store->>Store: 更新 State
    Store->>Vue: 响应式更新
    Vue->>User: 重新渲染页面
```

### API 数据格式

**请求格式：**
```json
{
  "username": "student1",
  "password": "password123"
}
```

**响应格式：**
```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    "id": 1,
    "username": "student1",
    "role": "student"
  }
}
```

---

## 数据流程图

### 用户登录流程

```mermaid
graph LR
    A[用户访问首页] -->|未登录| B[重定向到登录页]
    B -->|输入用户名密码| C[提交登录表单]
    C --> D{前端验证}
    D -->|验证失败| E[显示错误提示]
    D -->|验证通过| F[发送 POST /api/auth/login]
    F --> G[Flask 接收请求]
    G --> H[查询数据库验证用户]
    H --> I{验证结果}
    I -->|失败| J[返回错误 JSON]
    I -->|成功| K[生成登录状态]
    K --> L[保存用户信息到 localStorage]
    L --> M[更新 Vuex Store]
    M --> N[重定向到首页]
    J --> E
    E --> B
```

### 漏洞实验流程

```mermaid
graph LR
    A[选择漏洞] --> B[检查是否有记录]
    B --> C{是否首次?}
    C -->|是| D[创建实验记录]
    C -->|否| E[使用已有记录]
    D & E --> F[启动实验]
    F --> G[创建 Docker 容器]
    G --> H[分配端口]
    H --> I[保存容器信息]
    I --> J[显示实验环境]
    J --> K[用户完成实验]
    K --> L[提交 Flag]
    L --> M{验证 Flag}
    M -->|正确| N[标记成功<br>更新分数]
    M -->|错误| O[增加尝试次数]
    N --> P[停止容器]
    O --> P
    P --> Q[清理资源]
    Q --> R[返回结果]
```

---

## 部署架构

### 开发环境

```
┌─────────────────────────────────────────────────────────────┐
│                     开发环境 (localhost)                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐         │
│  │  前端            │        │  后端            │         │
│  │  localhost:3000  │◄──────►│  localhost:8000 │         │
│  │  (Vite Dev Server│        │  (Flask)         │         │
│  │   + Proxy)       │        │                  │         │
│  └──────────────────┘        └──────────────────┘         │
│          │                           │                      │
│          └───────────────────────────┴────────────────────┐│
│                                                      MySQL││
│                                              localhost:3306││
│                                                            ││
│  ┌──────────────────────────────────────────────────────┐ │
│  │  Docker Engine                                       │ │
│  │  - 漏洞容器 (动态创建)                                │ │
│  │  - 容器网络隔离                                      │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 生产环境

```mermaid
graph TB
    subgraph "服务器集群"
        Nginx[Nginx<br>反向代理<br>80/443端口]
        Frontend[前端静态资源<br>Vite Build]
        Backend[Flask应用<br>8000端口]
        MySQL[MySQL数据库<br>3306端口]
        Docker[Docker<br>容器运行时]
    end
    
    subgraph "用户端"
        Browser[用户浏览器]
    end
    
    Browser -->|HTTPS| Nginx
    Nginx -->|静态资源| Frontend
    Nginx -->|/api/* 代理| Backend
    Backend -->|读写数据| MySQL
    Backend -->|容器操作| Docker
```

**部署配置文件示例：**

- 启动脚本：[start.sh](file:///home/yu/Mlai-lab/start.sh)
- 后端配置：[config.py](file:///home/yu/Mlai-lab/backend/config.py)
- Gunicorn配置：[gunicorn.conf.py](file:///home/yu/Mlai-lab/backend/gunicorn.conf.py)

---

## 核心优势

| 特性 | 传统B/S架构 | 前后端分离架构 |
|------|------------|--------------|
| 耦合度 | 高耦合 (模板渲染) | 低耦合 (API交互) |
| 开发效率 | 前后端依赖串行 | 前后端并行开发 |
| 技术选型 | 绑定后端模板 | 自由选择前端框架 |
| 扩展性 | 困难 | 易于水平扩展 |
| 复用性 | 低 | 高 (API可服务多端) |
| 用户体验 | 刷新整页 | SPA无刷新 |

---

## 文件结构概览

```
Mlai-Lab/
├── frontend/                    # 前端项目
│   ├── src/
│   │   ├── api/                # API 模块
│   │   ├── components/         # Vue 组件
│   │   ├── views/             # 页面组件
│   │   ├── router/            # 路由配置
│   │   ├── store/             # 状态管理
│   │   └── utils/             # 工具函数
│   └── vite.config.js         # Vite 配置
│
├── backend/                    # 后端项目
│   ├── app.py                 # Flask 应用入口
│   ├── routes/                # 路由模块
│   │   ├── auth.py            # 认证路由
│   │   ├── users.py           # 用户路由
│   │   ├── experiment.py       # 实验路由
│   │   └── container.py        # 容器路由
│   └── utils/                 # 工具模块
│
└── docker/                     # Docker 环境
    └── ...                    # 漏洞容器定义
```
