from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import bcrypt
import jwt
import sqlite3
import httpx
import json
import uuid
from datetime import datetime, timedelta

# ============ 配置 ============
SECRET_KEY = "change-this-in-production"
DB_PATH = "xinhai_auth.db"
XINHAI_AGENT_URL = "http://localhost:18789"  # XinHai 智能体服务地址

# ============ 数据库初始化 ============
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 用户表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)
    
    # 对话历史表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_histories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER REFERENCES users(id),
            session_key TEXT NOT NULL,
            title TEXT,
            messages JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    # 索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_user ON chat_histories(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_chat_session ON chat_histories(session_key)")
    
    conn.commit()
    conn.close()

init_db()

# ============ FastAPI App ============
app = FastAPI(title="XinHai Auth Service")
security = HTTPBearer()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 数据模型 ============
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str
    image_base64: str | None = None
    system_prompt: str = ""

class SaveChatRequest(BaseModel):
    session_key: str
    title: str | None = None
    messages: list

class UpdateTitleRequest(BaseModel):
    title: str

# ============ 数据库工具 ============
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: int, username: str) -> str:
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(days=7),
        'type': 'access'
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=['HS256'])
        if payload.get('type') != 'access':
            raise HTTPException(401, "Invalid token type")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")

def get_or_create_session_key(user_id: int) -> str:
    """获取或创建用户的 session key"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT session_key FROM chat_histories WHERE user_id=? AND is_active=1 ORDER BY updated_at DESC LIMIT 1",
        (user_id,)
    )
    row = cursor.fetchone()
    
    if row:
        session_key = row['session_key']
        cursor.execute(
            "UPDATE chat_histories SET updated_at=? WHERE session_key=?",
            (datetime.now(), session_key)
        )
    else:
        session_key = f"xinhai_user_{user_id}_{uuid.uuid4().hex[:8]}"
    
    conn.commit()
    conn.close()
    return session_key

# ============ 认证 API ============

@app.post("/auth/register")
def register(user: UserRegister):
    """用户注册"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT 1 FROM users WHERE username=? OR email=?", 
                   (user.username, user.email))
    if cursor.fetchone():
        raise HTTPException(400, "Username or email already exists")
    
    password_hash = hash_password(user.password)
    cursor.execute(
        "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
        (user.username, user.email, password_hash)
    )
    conn.commit()
    user_id = cursor.lastrowid
    
    token = create_token(user_id, user.username)
    
    return {"token": token, "user_id": user_id, "username": user.username}

@app.post("/auth/login")
def login(credentials: UserLogin):
    """用户登录"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username=?", (credentials.username,))
    user = cursor.fetchone()
    
    if not user or not verify_password(credentials.password, user['password_hash']):
        raise HTTPException(401, "Invalid username or password")
    
    cursor.execute("UPDATE users SET last_login=? WHERE id=?", 
                   (datetime.now(), user['id']))
    conn.commit()
    
    token = create_token(user['id'], user['username'])
    
    return {"token": token, "user_id": user['id'], "username": user['username']}

@app.get("/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "user_id": current_user['user_id'],
        "username": current_user['username']
    }

# ============ 对话历史 API ============

@app.get("/chat/history")
def get_chat_history(current_user: dict = Depends(get_current_user)):
    """获取用户的所有对话历史"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, session_key, title, created_at, updated_at,
               json_array_length(messages) as message_count
        FROM chat_histories 
        WHERE user_id = ? AND is_active = 1
        ORDER BY updated_at DESC
    """, (current_user['user_id'],))
    
    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            "id": row['id'],
            "sessionKey": row['session_key'],
            "title": row['title'] or f"\u5bf9\u8bdd {row['created_at'][:10]}",
            "createdAt": row['created_at'],
            "updatedAt": row['updated_at'],
            "messageCount": row['message_count']
        })
    
    conn.close()
    return {"sessions": sessions}

@app.get("/chat/history/{session_key}")
def get_chat_session(session_key: str, current_user: dict = Depends(get_current_user)):
    """获取特定会话的完整对话内容"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM chat_histories 
        WHERE session_key = ? AND user_id = ? AND is_active = 1
    """, (session_key, current_user['user_id']))
    
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        raise HTTPException(404, "Session not found")
    
    return {
        "sessionKey": row['session_key'],
        "title": row['title'],
        "messages": json.loads(row['messages']),
        "createdAt": row['created_at'],
        "updatedAt": row['updated_at']
    }

@app.post("/chat/history")
def save_chat_history(request: SaveChatRequest, current_user: dict = Depends(get_current_user)):
    """保存或更新对话历史"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT id FROM chat_histories WHERE session_key = ? AND user_id = ?",
        (request.session_key, current_user['user_id'])
    )
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("""
            UPDATE chat_histories 
            SET messages = ?, updated_at = ?, title = COALESCE(?, title)
            WHERE id = ?
        """, (json.dumps(request.messages), datetime.now(), request.title, existing['id']))
    else:
        cursor.execute("""
            INSERT INTO chat_histories (user_id, session_key, title, messages)
            VALUES (?, ?, ?, ?)
        """, (current_user['user_id'], request.session_key, 
              request.title or "\u65b0\u5bf9\u8bdd", json.dumps(request.messages)))
    
    conn.commit()
    conn.close()
    return {"message": "Saved"}

@app.delete("/chat/history/{session_key}")
def delete_chat_session(session_key: str, current_user: dict = Depends(get_current_user)):
    """软删除对话历史"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE chat_histories SET is_active = 0 
        WHERE session_key = ? AND user_id = ?
    """, (session_key, current_user['user_id']))
    
    conn.commit()
    conn.close()
    return {"message": "Deleted"}

@app.patch("/chat/history/{session_key}/title")
def update_chat_title(session_key: str, request: UpdateTitleRequest,
                     current_user: dict = Depends(get_current_user)):
    """修改对话标题"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE chat_histories SET title = ?, updated_at = ?
        WHERE session_key = ? AND user_id = ?
    """, (request.title, datetime.now(), session_key, current_user['user_id']))
    
    conn.commit()
    conn.close()
    return {"message": "Title updated"}

# ============ XinHai 智能体代理 ============

@app.post("/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """代理到 XinHai 智能体的聊天接口"""
    user_id = current_user['user_id']
    session_key = get_or_create_session_key(user_id)
    
    messages = []
    if request.system_prompt:
        messages.append({"role": "system", "content": request.system_prompt})
    
    if request.image_base64 and request.image_base64.startswith("data:image"):
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": request.message},
                {"type": "image_url", "image_url": {"url": request.image_base64}}
            ]
        })
    else:
        messages.append({"role": "user", "content": request.message})
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            response = await client.post(
                f"{XINHAI_AGENT_URL}/openclaw/v1/chat/completions",
                json={
                    "model": "openclaw:main",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "user": session_key
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer 171f137313b83a6df17ee17a63060830fbba5901ecf09dec"
                }
            )
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(503, f"XinHai agent unavailable: {str(e)}")

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """流式聊天接口（SSE）"""
    user_id = current_user['user_id']
    session_key = get_or_create_session_key(user_id)
    
    messages = []
    if request.system_prompt:
        messages.append({"role": "system", "content": request.system_prompt})
    
    if request.image_base64 and request.image_base64.startswith("data:image"):
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": request.message},
                {"type": "image_url", "image_url": {"url": request.image_base64}}
            ]
        })
    else:
        messages.append({"role": "user", "content": request.message})
    
    async def generate():
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                f"{XINHAI_AGENT_URL}/openclaw/v1/chat/completions",
                json={
                    "model": "openclaw:main",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2000,
                    "stream": True,
                    "user": session_key
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer 171f137313b83a6df17ee17a63060830fbba5901ecf09dec"
                }
            ) as response:
                async for chunk in response.aiter_text():
                    yield f"data: {chunk}\n\n"
                yield "data: [DONE]\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# ============ 健康检查 ============
@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
