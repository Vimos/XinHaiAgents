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
import sys
import os
import tempfile
import asyncio
from datetime import datetime, timedelta

# 添加 xinhai 包路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# ============ 配置 ============
SECRET_KEY = "change-this-in-production"
DB_PATH = "xinhai_auth.db"
XINHAI_AGENT_URL = "https://chat.xinhai.co"  # XinHai 智能体服务地址

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
            sidebar TEXT DEFAULT 'chat',
            title TEXT,
            messages JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
    """)
    
    # 尝试添加 sidebar 列（已有表的情况）
    try:
        cursor.execute("ALTER TABLE chat_histories ADD COLUMN sidebar TEXT DEFAULT 'chat'")
    except:
        pass
    
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
    message: str | None = None  # 旧版兼容
    messages: list | None = None  # 新版支持数组
    image_base64: str | None = None
    system_prompt: str = ""
    sidebar: str = "chat"
    session_key: str | None = None

class SaveChatRequest(BaseModel):
    session_key: str
    sidebar: str = "chat"
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

def get_or_create_session_key(user_id: int, sidebar: str = "chat") -> str:
    """获取或创建用户的 session key，按 sidebar 区分"""
    # 每个用户 + 每个边栏 = 独立的 session_key
    return f"xinhai_user_{user_id}_{sidebar}"

# ============ 认证 API ============

@app.post("/api/auth/register")
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

@app.post("/api/auth/login")
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

@app.get("/api/auth/me")
def get_me(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "user_id": current_user['user_id'],
        "username": current_user['username']
    }

# ============ 对话历史 API ============

@app.get("/api/chat/history")
def get_chat_history(sidebar: str = None, current_user: dict = Depends(get_current_user)):
    """获取用户的对话历史，可按 sidebar 过滤"""
    conn = get_db()
    cursor = conn.cursor()
    
    if sidebar:
        cursor.execute("""
            SELECT id, session_key, sidebar, title, created_at, updated_at,
                   json_array_length(messages) as message_count
            FROM chat_histories 
            WHERE user_id = ? AND is_active = 1 AND sidebar = ?
            ORDER BY updated_at DESC
        """, (current_user['user_id'], sidebar))
    else:
        cursor.execute("""
            SELECT id, session_key, sidebar, title, created_at, updated_at,
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
            "sidebar": row['sidebar'] if 'sidebar' in row.keys() else 'chat',
            "title": row['title'] or f"对话 {row['created_at'][:10]}",
            "createdAt": row['created_at'],
            "updatedAt": row['updated_at'],
            "messageCount": row['message_count']
        })
    
    conn.close()
    return {"sessions": sessions}

@app.get("/api/chat/history/{session_key}")
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

@app.post("/api/chat/history")
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
            SET messages = ?, updated_at = ?, title = COALESCE(?, title), sidebar = COALESCE(?, sidebar)
            WHERE id = ?
        """, (json.dumps(request.messages), datetime.now(), request.title, request.sidebar, existing['id']))
    else:
        cursor.execute("""
            INSERT INTO chat_histories (user_id, session_key, sidebar, title, messages)
            VALUES (?, ?, ?, ?, ?)
        """, (current_user['user_id'], request.session_key, 
              request.sidebar, request.title or "新对话", json.dumps(request.messages)))
    
    conn.commit()
    conn.close()
    return {"message": "Saved"}

@app.delete("/api/chat/history/{session_key}")
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

@app.patch("/api/chat/history/{session_key}/title")
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

@app.post("/api/chat")
async def chat(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """代理到 XinHai 智能体的聊天接口"""
    user_id = current_user['user_id']
    session_key = get_or_create_session_key(user_id, request.sidebar)
    
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
                f"{XINHAI_AGENT_URL}/v1/chat/completions",
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

@app.post("/api/chat/stream")
async def chat_stream(request: ChatRequest, current_user: dict = Depends(get_current_user)):
    """流式聊天接口（SSE）"""
    user_id = current_user['user_id']
    session_key = request.session_key or get_or_create_session_key(user_id, request.sidebar)
    
    # 支持两种消息格式
    if request.messages:
        # 新版：直接使用 messages 数组
        messages = request.messages
        if request.system_prompt:
            messages = [{"role": "system", "content": request.system_prompt}] + messages
    else:
        # 旧版：从 message 构建
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
            messages.append({"role": "user", "content": request.message or ""})
    
    async def generate():
        async with httpx.AsyncClient(timeout=300.0) as client:
            async with client.stream(
                "POST",
                f"{XINHAI_AGENT_URL}/v1/chat/completions",
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
                # 直接透传 OpenClaw 的 SSE 数据，不再包装
                async for chunk in response.aiter_bytes():
                    yield chunk
    
    return StreamingResponse(generate(), media_type="text/event-stream")

# ============ 健康检查 ============
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# ============ Simulation API ============

# 用户模拟实例管理（内存中）
user_simulations = {}

class SimulationCreateRequest(BaseModel):
    config_yaml: str  # YAML 配置内容

class SimulationNextRequest(BaseModel):
    input_messages: list = []  # 用户输入（proxy agent 场景）

@app.post("/api/simulation/create")
def create_simulation(
    request: SimulationCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """上传 YAML 配置，创建模拟实例"""
    user_id = current_user['user_id']
    
    try:
        from xinhai.arena.simulation import Simulation
        print(f"[Simulation] Imported Simulation class successfully")
    except ImportError as e:
        print(f"[Simulation] Import error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"xinhai arena not available: {e}")
    
    # 写入临时文件
    tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8')
    tmp.write(request.config_yaml)
    tmp.flush()
    tmp.close()
    print(f"[Simulation] Config written to {tmp.name}")
    print(f"[Simulation] Config content preview: {request.config_yaml[:200]}...")
    
    try:
        env_id = f"sim_user_{user_id}_{uuid.uuid4().hex[:8]}"
        print(f"[Simulation] Creating simulation with env_id: {env_id}")
        
        # 验证 YAML 格式
        import yaml
        with open(tmp.name, 'r', encoding='utf-8') as f:
            test_config = yaml.safe_load(f)
        print(f"[Simulation] YAML parsed, type: {type(test_config)}")
        if isinstance(test_config, dict):
            print(f"[Simulation] YAML keys: {list(test_config.keys())}")
        else:
            print(f"[Simulation] YAML content: {test_config}")
        
        sim = Simulation.from_config(tmp.name, environment_id=env_id)
        print(f"[Simulation] Simulation created, agents: {len(sim.agents)}")
        
        sim.reset()
        print(f"[Simulation] Simulation reset completed")
        
        user_simulations[user_id] = sim
        
        # 返回 agent 列表供前端渲染
        agents_info = []
        for agent in sim.agents:
            agents_info.append({
                "id": agent.agent_id,
                "name": agent.name,
                "role": agent.role_description,
                "type": str(agent.agent_type),
            })
        
        # 提取拓扑信息
        topologies_info = []
        for topo in sim.environment.topologies:
            edges = list(topo.digraph.edges())
            topologies_info.append({
                "name": topo.name,
                "maxTurns": topo.max_turns,
                "edges": [{"from": e[0], "to": e[1]} for e in edges]
            })
        
        return {
            "status": "created",
            "environmentId": env_id,
            "agents": agents_info,
            "topologies": topologies_info
        }
    except Exception as e:
        print(f"[Simulation] Error creating simulation: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(400, f"Failed to create simulation: {e}")
    finally:
        os.unlink(tmp.name)

@app.post("/api/simulation/next")
async def simulation_next(
    request: SimulationNextRequest,
    current_user: dict = Depends(get_current_user)
):
    """执行一步模拟，返回 agent 发言"""
    user_id = current_user['user_id']
    sim = user_simulations.get(user_id)
    
    if not sim:
        raise HTTPException(404, "No active simulation. Create one first.")
    
    if sim.environment.is_done():
        return {"status": "done", "message": "模拟已结束"}
    
    try:
        # 在线程池中执行（避免阻塞事件循环）
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: sim.next(input_messages=request.input_messages)
        )
        
        if result:
            return {
                "status": "ok",
                "message": {
                    "senderId": result.senderId,
                    "username": result.username,
                    "content": result.content,
                    "receiverIds": result.receiverIds,
                    "timestamp": result.timestamp,
                    "date": getattr(result, 'date', ''),
                }
            }
        
        return {"status": "done", "message": "模拟已结束"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Simulation step failed: {e}")

@app.post("/api/simulation/reset")
def reset_simulation(current_user: dict = Depends(get_current_user)):
    """重置模拟"""
    user_id = current_user['user_id']
    sim = user_simulations.get(user_id)
    
    if not sim:
        raise HTTPException(404, "No active simulation")
    
    sim.reset()
    return {"status": "reset"}

@app.get("/api/simulation/status")
def simulation_status(current_user: dict = Depends(get_current_user)):
    """获取当前模拟状态"""
    user_id = current_user['user_id']
    sim = user_simulations.get(user_id)
    
    if not sim:
        return {"status": "none"}
    
    return {
        "status": "active" if not sim.environment.is_done() else "done",
        "agents": [
            {
                "id": a.agent_id,
                "name": a.name,
                "role": a.role_description,
                "type": str(a.agent_type),
                "messageCount": len(a.memory.short_term_memory.messages) if hasattr(a.memory, 'short_term_memory') and a.memory else 0
            }
            for a in sim.agents
        ]
    }

# ============ Controller Storage API (Embedded) ============
# 模拟 Controller 的 storage API，消除外部 controller 依赖

from xinhai.types.storage import XinHaiStorageErrorCode
from xinhai.types.memory import XinHaiMemory, XinHaiShortTermMemory, XinHaiLongTermMemory

class FetchMemoryRequest(BaseModel):
    storage_key: str

class StoreMemoryRequest(BaseModel):
    storage_key: str
    memory: dict  # XinHaiMemory as dict

# In-memory storage for simulation (per storage_key)
simulation_memory = {}

@app.post("/api/storage/fetch-memory")
def fetch_memory(request: FetchMemoryRequest):
    """获取 agent 记忆（模拟 controller 的 storage API）"""
    key = request.storage_key
    data = simulation_memory.get(key, {
        "storage_key": key,
        "short_term_memory": {"messages": []},
        "long_term_memory": {"summaries": []}
    })
    return {
        "memory": data,
        "error_code": 0  # XinHaiStorageErrorCode.OK = 0
    }

@app.post("/api/storage/store-memory")
def store_memory(request: StoreMemoryRequest):
    """存储 agent 记忆（模拟 controller 的 storage API）"""
    simulation_memory[request.storage_key] = request.memory
    short_term_count = len(request.memory.get("short_term_memory", {}).get("messages", []))
    long_term_count = len(request.memory.get("long_term_memory", {}).get("summaries", []))
    return {
        "storage_key": request.storage_key,
        "short_term_messages_count": short_term_count,
        "long_term_summaries_count": long_term_count,
        "error_code": 0  # XinHaiStorageErrorCode.OK = 0
    }

@app.get("/api/storage/capacity")
def storage_capacity():
    """检查存储容量"""
    return {"status": "success", "capacity": 1000000}

@app.get("/api/storage/models")
def storage_models():
    """获取可用模型列表"""
    return {
        "models": ["gpt-4o", "gpt-4", "gpt-3.5-turbo", "Qwen2.5-7B-Instruct"]
    }


# ============ LLM API Proxy ============
# 代理到 XinHai/OpenAI 服务，供 Arena Agent 使用

class ChatCompletionRequest(BaseModel):
    model: str
    messages: list
    temperature: float = 0.7
    max_tokens: int = 2000
    stream: bool = False


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    """代理 LLM 请求到 XinHai 服务"""
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{XINHAI_AGENT_URL}/v1/chat/completions",
                json={
                    "model": request.model,
                    "messages": request.messages,
                    "temperature": request.temperature,
                    "max_tokens": request.max_tokens,
                    "stream": request.stream
                },
                headers={
                    "Content-Type": "application/json",
                    "Authorization": "Bearer 171f137313b83a6df17ee17a63060830fbba5901ecf09dec"
                }
            )
            return response.json()
    except Exception as e:
        raise HTTPException(503, f"LLM service unavailable: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
