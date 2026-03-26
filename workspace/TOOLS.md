# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## XinHaiAgents Project

### Repository Structure
```
XinHaiAgents/
├── backend/           # FastAPI + LangChain
│   ├── src/xinhai/    # Core implementation
│   └── docker/        # Docker configs
├── frontend/          # Vue 3 + Phaser
│   ├── src/           # Vue components
│   └── docker/        # Docker configs
├── skills/            # OpenClaw Skills
│   ├── xinhai-agents/
│   └── suicide-risk-evidence/
└── configs/           # YAML configs
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| Backend API | 8000 | FastAPI server |
| Frontend | 8080 | Vue.js app |
| ChromaDB | 8001 | Vector database |
| Redis | 6379 | Cache |

### Environment Variables

Create `.env` file:
```bash
XINHAI_BACKEND_URL=http://localhost:8000
XINHAI_API_KEY=your_key
OPENAI_API_KEY=optional_for_gpt4
```

## Development Setup

### Backend
```bash
cd backend
pip install -r requirements.txt
python -m src.xinhai
```

### Frontend
```bash
cd frontend
npm install
npm run serve
```

### Docker (Recommended)
```bash
docker-compose up -d
```

## Skills

### Available Skills
- `skills/xinhai-agents/` - Multi-agent simulation
- `skills/suicide-risk-evidence/` - Risk detection

### Using Skills
```python
from skills.xinhai_agents.scripts.xinhai_agents import XinHaiSkill

xinhai = XinHaiSkill(config)
```

## Model Configuration

### XinHai-6B
- Base: ChatGLM3-6B
- Fine-tuned on medical + mental health data
- Location: `models/xinhai-6b/`

### Alternative Models
- GPT-4 (via API)
- Qwen-2.5
- LLaMA-3

## API Endpoints

### Backend
- `POST /simulate` - Start simulation
- `GET /session/{id}` - Get session status
- `WS /ws/{id}` - WebSocket stream

### Skills
- Direct Python API (see skill docs)

## Testing

```bash
# Run skill tests
python -m pytest skills/*/tests/

# Run backend tests
python -m pytest backend/tests/
```

## Deployment

### Docker Hub
```bash
docker build -t xinhai/backend backend/
docker build -t xinhai/frontend frontend/
docker push xinhai/backend
docker push xinhai/frontend
```

### GitHub Actions
- Auto-build on push
- Run tests
- Deploy to staging

## Notes

- Backend images are ~17GB (include PyTorch)
- Frontend uses Phaser for visualization
- ChromaDB persists data in `./chroma_db/`
- Redis used for caching and pub/sub

## Channel-Specific

### Discord Integration
- Bot commands in `skills/xinhai-agents/scripts/`
- Channel: #💬-情感支持对话
- Commands: /simulate, /status, /visualize, /evaluate

---

Add whatever helps you do your job. This is your cheat sheet.
