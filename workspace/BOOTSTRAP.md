# BOOTSTRAP.md - First Run Instructions

Welcome to XinHaiAgents OpenClaw Workspace!

## Initial Setup

### 1. Read Project Identity

First, understand who you are and who you're helping:
- Read `SOUL.md` - Your persona
- Read `USER.md` - Your human collaborator
- Read `IDENTITY.md` - Your name and identity

### 2. Understand the Project

XinHaiAgents is a framework for:
- Multi-agent simulation
- Mental health applications
- Suicide risk detection
- Conversational AI research

### 3. Key Files to Read

```bash
# Essential context
read SOUL.md
read USER.md
read AGENTS.md
read README.md

# Project structure
ls backend/
ls frontend/
ls skills/
```

### 4. Skills Available

Two OpenClaw Skills are available:

```bash
# Multi-agent simulation
read skills/xinhai-agents/SKILL.md

# Suicide risk detection
read skills/suicide-risk-evidence/SKILL.md
```

### 5. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit with your settings
edit .env
```

### 6. Start Services

```bash
# Using Docker
docker-compose up -d

# Or start backend manually
cd backend && python -m src.xinhai
```

## First Tasks

After bootstrap, you should:

1. **Explore the codebase**
   - Understand backend architecture
   - Check frontend components
   - Review skill implementations

2. **Run examples**
   - Try provided examples in `examples/`
   - Test skill functionality

3. **Set up development environment**
   - Install dependencies
   - Configure IDE
   - Set up debugging

## After Bootstrap

Once you've completed the above:

1. Delete this file: `rm BOOTSTRAP.md`
2. Create your first daily note: `memory/$(date +%Y-%m-%d).md`
3. Start working on tasks from `HEARTBEAT.md`

## Getting Help

- Project README: `README.md`
- Architecture docs: `references/architecture.md`
- Integration guide: `references/integration.md`
- GitHub Issues: https://github.com/Vimos/XinHaiAgents/issues

Welcome aboard! 🌊
