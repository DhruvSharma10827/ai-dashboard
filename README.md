# 🤖 AI Dashboard - Enterprise Edition

<div align="center">

**Enterprise-Grade AI Orchestration System**

A powerful, professional, production-ready TUI application for managing AI models,
agents, and autonomous workflows with enterprise security.

</div>

---

## ✨ Features

### 🎯 Core Capabilities

- **Multi-Provider AI Support**
  - Local: Ollama, Llama.cpp, LocalAI, TensorFlow
  - Cloud: OpenAI, Claude, Gemini, Groq, OpenRouter
  - Intelligent routing between providers

- **Multi-Modal Processing**
  - Text: Chat, completion, embeddings
  - Audio: Speech-to-text, text-to-speech
  - Image: Vision models, image generation
  - Video: Analysis and processing

- **Multi-Agent Orchestration**
  - Specialized agents (Code, Research, Task, Chat)
  - Parallel task execution
  - Agent communication protocol

- **MCP (Model Context Protocol)**
  - Tools: Filesystem, Database, Shell, Web Search
  - Custom tool creation

### 🔒 Enterprise Security

- **Authentication**: Argon2id password hashing
- **Encryption**: AGE encryption for secrets
- **SSH Server**: Remote access on port 2222
- **Session Management**: Secure tokens

### 🖥️ World-Class TUI

- Modern Textual framework
- Multiple screens: Dashboard, Models, Agents, Chat, Tasks, Settings
- Keyboard-driven navigation

---

## 📦 Installation

### Requirements

- Python 3.11+
- pip or pipx

### Quick Install

```bash
# Clone repository
git clone https://github.com/DhruvSharma10827/ai-dashboard.git
cd ai-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run
python dashboard.py
```

### Create Desktop Entry (Linux)

```bash
cat > ~/.local/share/applications/ai-dashboard.desktop << EOF
[Desktop Entry]
Name=AI Dashboard
Comment=Enterprise AI Orchestration System
Exec=/home/$(whoami)/ai-dashboard/run.sh
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=System;ConsoleOnly;
EOF
```

---

## 🚀 Quick Start

### First Time Setup

1. Run the dashboard:
```bash
python dashboard.py
```

2. Create admin password when prompted

3. Configure AI providers:
   - Press `6` for Settings
   - Navigate to API Keys tab
   - Add your API keys

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `1` | Dashboard |
| `2` | Models |
| `3` | Agents |
| `4` | Chat |
| `5` | Tasks |
| `6` | Settings |
| `?` | Help |
| `q` | Quit |
| `Esc` | Back |

---

## 🌐 Configuration

Configuration is stored in `~/.ai-dashboard/config.json`

### Adding API Keys

```bash
# Via TUI: Settings → API Keys
# Or via config file:
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
```

---

## 🔧 Project Structure

```
ai-dashboard/
├── dashboard.py           # Main TUI application
├── requirements.txt       # Python dependencies
├── internal/
│   ├── python/
│   │   ├── engine.py      # AI Engine
│   │   ├── modules/
│   │   │   └── mcp_server.py  # MCP Server
│   │   └── requirements.txt
│   ├── security/          # Security modules (Go)
│   ├── storage/           # Database operations (Go)
│   └── config/            # Configuration (Go)
├── cmd/ai-dashboard/      # Entry point (Go)
└── pkg/                   # Public packages
```

---

## 📝 License

MIT License
