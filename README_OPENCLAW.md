# XinHaiAgents OpenClaw Workspace

This repository contains the XinHaiAgents project with OpenClaw integration.

## Quick Navigation

- **Workspace Config**: [`workspace/`](workspace/)
  - [`SOUL.md`](workspace/SOUL.md) - AI personality
  - [`AGENTS.md`](workspace/AGENTS.md) - Workspace guide
  - [`USER.md`](workspace/USER.md) - Team information
  - [`BOOTSTRAP.md`](workspace/BOOTSTRAP.md) - First run instructions
  - [`HEARTBEAT.md`](workspace/HEARTBEAT.md) - Periodic tasks
  - [`IDENTITY.md`](workspace/IDENTITY.md) - AI identity
  - [`TOOLS.md`](workspace/TOOLS.md) - Tool configurations

- **Backend**: [`backend/`](backend/) - FastAPI services
- **Frontend**: [`frontend/`](frontend/) - Vue 3 + Phaser
- **Skills**: [`skills/`](skills/) - OpenClaw skills
  - `xinhai-agents/` - Multi-agent simulation
  - `suicide-risk-evidence/` - Risk detection

## Getting Started

```bash
# Read bootstrap instructions
cat workspace/BOOTSTRAP.md

# Start services
docker-compose up -d

# Run a skill example
python skills/xinhai-agents/scripts/xinhai_agents.py
```

## Project Structure

```
XinHaiAgents/
├── workspace/           # OpenClaw workspace configs
├── backend/             # Backend services
├── frontend/            # Frontend application
├── skills/              # OpenClaw skills
├── configs/             # Configuration files
├── examples/            # Usage examples
└── README.md            # This file
```

## Links

- **Repository**: https://github.com/Vimos/XinHaiAgents
- **Documentation**: See `workspace/` and `skills/*/SKILL.md`
