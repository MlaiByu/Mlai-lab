# 开发日志 / Changelog

## v1.0.0 - 初始版本 (2024-01-01)

### 项目初始化

- 创建Mlai-Lab网络安全培训平台
- 搭建前后端项目结构

### 后端开发

| 文件 | 描述 | 日期 |
|------|------|------|
| `backend/app.py` | Flask应用入口，配置CORS和路由注册 | 2024-01-01 |
| `backend/config.py` | 应用配置文件 | 2024-01-01 |
| `backend/init_db.py` | 数据库初始化脚本 | 2024-01-01 |
| `backend/routes/__init__.py` | 路由模块初始化 | 2024-01-01 |
| `backend/routes/auth.py` | 用户认证（注册、登录、JWT） | 2024-01-01 |
| `backend/routes/container.py` | Docker容器管理（创建、删除、端口分配） | 2024-01-01 |
| `backend/routes/experiment.py` | 实验会话管理（开始、完成、停止） | 2024-01-01 |
| `backend/routes/health.py` | 健康检查接口 | 2024-01-01 |
| `backend/routes/users.py` | 用户管理（列表、统计） | 2024-01-01 |
| `backend/utils/db.py` | 数据库操作工具类 | 2024-01-01 |

### 前端开发

| 文件 | 描述 | 日期 |
|------|------|------|
| `frontend/src/main.js` | Vue应用入口 | 2024-01-01 |
| `frontend/src/App.vue` | 根组件 | 2024-01-01 |
| `frontend/src/router/index.js` | Vue Router配置 | 2024-01-01 |
| `frontend/src/api/index.js` | API调用封装 | 2024-01-01 |
| `frontend/src/store/index.js` | 状态管理 | 2024-01-01 |
| `frontend/src/components/Navbar.vue` | 导航栏组件 | 2024-01-01 |
| `frontend/src/views/Home.vue` | 首页 | 2024-01-01 |
| `frontend/src/views/Login.vue` | 登录页 | 2024-01-01 |
| `frontend/src/views/Register.vue` | 注册页 | 2024-01-01 |
| `frontend/src/views/Vulnerabilities.vue` | 漏洞环境列表 | 2024-01-01 |
| `frontend/src/views/Progress.vue` | 个人进度页 | 2024-01-01 |
| `frontend/src/views/Users.vue` | 用户管理页（教师） | 2024-01-01 |

### Docker漏洞环境

| 环境 | 描述 | 技术栈 |
|------|------|--------|
| `sqli-easy` | SQL注入-入门 | PHP + MySQL |
| `sqli-medium` | SQL注入-中级 | PHP + MySQL |
| `sqli-hard` | SQL注入-高级 | PHP + MySQL |
| `xss-reflected` | 反射型XSS | PHP |
| `xss-stored` | 存储型XSS | PHP |
| `xss-dom` | DOM型XSS | HTML + JavaScript |
| `php-deserialization` | PHP反序列化 | PHP |
| `python-deserialization` | Python反序列化 | Python |
| `file-upload` | 文件上传 | PHP |

### 部署配置

| 文件 | 描述 |
|------|------|
| `requirements.txt` | Python依赖清单 |
| `docker-compose.yml` | Docker Compose配置 |
| `backend/Dockerfile` | 后端Docker镜像 |
| `frontend/Dockerfile` | 前端Docker镜像 |
| `run-services.sh` | 服务管理脚本 |
| `start-services.sh` | 持久化服务脚本 |
| `mlai-backend.service` | Systemd服务文件 |

### 问题修复记录

1. **端口冲突问题** - 解决多个漏洞容器端口分配冲突
2. **Docker启动慢** - 通过预构建镜像优化（20-30s → 3-5s）
3. **服务后台运行** - 使用screen实现持久化
4. **CORS跨域** - 配置Flask-CORS支持跨域请求
5. **JWT认证** - 实现用户登录状态保持

### 配置变更

| 日期 | 变更内容 |
|------|----------|
| 2024-01-01 | 初始版本创建 |
| 2024-01-01 | 后端端口从8001改为8000 |
| 2024-01-01 | 前端端口固定为3000 |
| 2024-01-01 | Docker端口范围限制为10000-13000 |
| 2024-01-01 | 添加端口缓存提高分配效率 |

---

## 版本规划

### v1.1.0 (计划中)

- [ ] 添加更多漏洞环境
- [ ] 实现实时排行榜
- [ ] 添加题目提示系统
- [ ] 支持在线代码编辑器

### v1.2.0 (计划中)

- [ ] 容器资源限制优化
- [ ] 添加容器监控面板
- [ ] 实现容器自动续期
- [ ] 添加操作日志审计