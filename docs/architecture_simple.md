# Mlai-Lab B/S 架构图

## 一、系统架构

```mermaid
graph LR
    subgraph "客户端"
        A[浏览器]
    end
    
    subgraph "前端"
        B[Vue 3 SPA]
        C[Element Plus]
        D[Vue Router]
        E[Vuex]
    end
    
    subgraph "后端"
        F[Flask API]
        G[业务逻辑]
    end
    
    subgraph "数据层"
        H[(MySQL)]
        I[Docker]
    end
    
    A --> B
    B --> C
    B --> D
    B --> E
    E -->|HTTP/JSON| F
    F --> G
    G --> H
    G --> I
```

## 二、核心流程

### 用户登录流程
```mermaid
sequenceDiagram
    用户->>Vue: 登录表单
    Vue->>Flask: POST /api/auth/login
    Flask->>MySQL: 查询用户
    MySQL-->>Flask: 返回结果
    Flask-->>Vue: JSON响应
    Vue->>Vue: 保存登录状态
```

### 漏洞实验流程
```mermaid
flowchart TD
    A[选择漏洞] --> B[启动实验]
    B --> C[创建Docker容器]
    C --> D[分配端口]
    D --> E[访问实验环境]
    E --> F[提交Flag]
    F --> G{验证正确?}
    G -->|是| H[标记成功]
    G -->|否| I[增加尝试次数]
    H --> J[停止容器]
    I --> J
    J --> K[返回结果]
```

## 三、技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vue 3 + Element Plus | UI展示与交互 |
| 路由 | Vue Router | 页面导航 |
| 状态 | Vuex | 数据管理 |
| 后端 | Flask | RESTful API |
| 跨域 | Flask-CORS | 解决跨域问题 |
| 数据库 | MySQL | 数据存储 |
| 容器 | Docker | 漏洞环境隔离 |

## 四、部署架构

```
用户浏览器
    │
    ▼
┌─────────────────────────────────────┐
│          Nginx (80/443)           │  ← 反向代理
├─────────────────────────────────────┤
│   Frontend (静态资源)  Backend     │  ← 前后端分离
├─────────────────────────────────────┤
│         MySQL + Docker             │  ← 数据与容器
└─────────────────────────────────────┘
```

## 五、前后端通信

**请求格式：**
```json
{"username": "user", "password": "pass"}
```

**响应格式：**
```json
{"success": true, "message": "OK", "data": {...}}
```

---

*文档位置：* [architecture_simple.md](file:///home/yu/Mlai-lab/docs/architecture_simple.md)
