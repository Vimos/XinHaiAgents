# AGENTS.md - XinHaiAgents Workspace

This folder is home for AI agents collaborating on the XinHaiAgents project.

## About This Workspace

This is the OpenClaw workspace for **XinHaiAgents** - Sea of Minds Framework for Multimodal Multi-agent Simulation and Evolution.

## Project Structure

```
XinHaiAgents/
├── backend/           # FastAPI backend services
├── frontend/          # Vue 3 + Phaser frontend
├── skills/            # OpenClaw Skills
│   ├── xinhai-agents/         # Multi-agent simulation skill
│   └── suicide-risk-evidence/ # Suicide risk detection skill
├── configs/           # Configuration files
├── examples/          # Usage examples
├── instructions/      # Agent instructions
└── preprocessing/     # Data preprocessing
```

## Skills

### 1. xinhai-agents
Multi-agent simulation framework with:
- Dynamic agent orchestration
- Topology management
- Scenario templates
- Visualization support

### 2. suicide-risk-evidence
CLPsych 2024 implementation:
- Evidence highlighting from suicide-related posts
- 6-dimension risk assessment
- Bilingual support (EN/ZH)

## Memory

- Daily notes: `memory/YYYY-MM-DD.md`
- Long-term: `MEMORY.md`
- Project docs: `docs/`

## External Tools

- LLM: XinHai-6B (ChatGLM3-6B fine-tuned)
- Vector DB: ChromaDB
- Frontend: Vue 3 + Phaser
- Backend: FastAPI + LangChain

## Collaboration

When working on this project:
1. Check existing skills in `skills/` directory
2. Follow the project's coding standards
3. Update documentation when adding features
4. Test with provided examples

## Safety

- Don't commit sensitive data (API keys, tokens)
- Use environment variables for configuration
- Test thoroughly before pushing to main branch

## Contact

Project: https://github.com/Vimos/XinHaiAgents
Authors: Ancheng Xu, Jingwei Zhu, Minghuan Tan, Min Yang
Institution: Shenzhen Institutes of Advanced Technology, Chinese Academy of Sciences
