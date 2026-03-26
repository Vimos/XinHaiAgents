# User Authentication System for XinHaiAgents

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3)                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ LoginView   │  │ AuthStore   │  │ Axios Interceptor   │ │
│  │ RegisterView│  │ (Pinia)     │  │ (JWT auto-refresh)  │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS
┌───────────────────────────▼─────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │ Auth Router │  │ JWT Handler │  │ User CRUD           │ │
│  │ /auth/*     │  │ (python-jose)│  │ (SQLAlchemy)       │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Database (PostgreSQL)                   │
│  - users table                                               │
│  - refresh_tokens table (optional)                           │
└─────────────────────────────────────────────────────────────┘
```

## 安全特性

1. **JWT Token**
   - Access Token: 15分钟有效期
   - Refresh Token: 7天有效期
   - HttpOnly cookie (防 XSS)
   - Secure flag (HTTPS only)

2. **密码安全**
   - bcrypt 哈希
   - 最小长度 8 位
   - 复杂度要求

3. **防护机制**
   - 登录失败限制 (5次/15分钟)
   - CSRF 保护
   - Rate Limiting

## API 端点

| 方法 | 路径 | 描述 | 认证 |
|-----|------|------|------|
| POST | /auth/register | 用户注册 | 否 |
| POST | /auth/login | 用户登录 | 否 |
| POST | /auth/refresh | 刷新 Token | 否 (需 refresh token) |
| POST | /auth/logout | 用户登出 | 是 |
| GET | /auth/me | 获取当前用户 | 是 |
| PUT | /auth/me | 更新用户信息 | 是 |
| POST | /auth/change-password | 修改密码 | 是 |

## 快速开始

```bash
# 1. 安装依赖
# Backend
pip install python-jose[cryptography] passlib[bcrypt] python-multipart

# Frontend
npm install pinia @vueuse/core axios

# 2. 配置环境变量
cp .env.example .env

# 3. 启动服务
docker-compose up -d
```

## 使用说明

### 前端

```javascript
// 登录
const auth = useAuthStore()
await auth.login({ username: 'user', password: 'pass' })

// 访问受保护路由
// 自动携带 JWT token
```

### 后端

```python
# 保护路由
from auth.dependencies import get_current_user

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.username}"}
```

---

## 文件清单

### Backend
- `backend/src/xinhai/auth/` - 认证模块
- `backend/src/xinhai/models/user.py` - 用户模型
- `backend/src/xinhai/schemas/auth.py` - Pydantic schemas

### Frontend
- `frontend/src/views/LoginView.vue` - 登录页面
- `frontend/src/views/RegisterView.vue` - 注册页面
- `frontend/src/stores/auth.js` - Pinia store
- `frontend/src/router/guards.js` - 路由守卫
- `frontend/src/services/api.js` - Axios 配置

---

## 详细实现见各文件
