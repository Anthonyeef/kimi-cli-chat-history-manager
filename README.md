# Kimi CLI Chat History Dashboard

⚡ A FastAPI-based chat history manager for Kimi CLI conversations

> **Simplify:** View, search, and manage your Kimi CLI conversation history with a beautiful web dashboard

## ✨ Features

- 🔍 **Search conversations** - Find any chat by name or message content
- 📊 **Activity heatmap** - See your conversation patterns over time
- 💬 **Browse all messages** - Read full conversation history
- 🆔 **Get session IDs** - Reference any conversation
- 🗂️ **Filter by workspace** - Organize chats by project
- 📥 **Export to Markdown** - Save conversations for later

## 🏗️ Architecture

This project consists of:

**1. FastAPI Backend** - Indexes and serves your chat history
- Scans `~/.kimi/sessions/` for JSONL files
- Provides REST API endpoints for querying
- Auto-refreshes chat index

**2. Web Dashboard** - Beautiful UI to explore your chats
- GitHub-style activity heatmap
- Real-time search and filtering
- Full conversation viewer
- Export conversations to Markdown

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd server
pip install -r requirements.txt
```

### Step 2: Start the API Server

```bash
./run_server.sh
```

The server will automatically:
- Index all your chats from `~/.kimi/`
- Provide REST API endpoints
- Run on http://127.0.0.1:8001

### Step 3: Test the API

Open your browser and visit http://127.0.0.1:8001/docs

Try these endpoints:

```bash
# List your chats
curl http://127.0.0.1:8001/api/v1/chats?limit=10

# Get a specific chat
curl http://127.0.0.1:8001/api/v1/chats/{session-id}

# List workspaces
curl http://127.0.0.1:8001/api/v1/workspaces

# Refresh the index
curl -X POST http://127.0.0.1:8001/api/v1/refresh
```

## 📁 Project Structure

```
kimi-chat-history/
├── server/                     # FastAPI Backend
│   ├── main.py                # FastAPI application
│   ├── config.py              # Configuration settings
│   ├── requirements.txt       # Python dependencies
│   ├── api/
│   │   ├── models.py         # Pydantic models
│   │   └── __init__.py
│   ├── services/
│   │   ├── chat_service.py   # Chat discovery logic
│   │   └── __init__.py
│   ├── database/
│   │   ├── jsonl_reader.py   # JSONL file parser
│   │   └── __init__.py
│   └── tests/
│       ├── test_api.py       # API tests
│       └── test_jsonl_reader.py
├── dashboard/                 # Web Frontend (coming soon)
├── run_server.sh             # Server startup script
├── .env.example              # Environment configuration
└── README.md                # This file
```

## 📖 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/chats` | List chats (with filters) |
| GET | `/api/v1/chats/:id` | Get specific chat |
| GET | `/api/v1/workspaces` | List workspaces |
| POST | `/api/v1/refresh` | Refresh chat index |

## 🔧 Configuration

Copy the environment template:

```bash
cp .env.example .env
```

Edit `.env` to customize:

```bash
# Server port
PORT=8001

# CORS origins (for dashboard)
CORS_ORIGINS=["http://localhost:8001", "null", "file://"]

# Kimi data directory
KIMI_BASE_DIR=~/.kimi

# Cache settings
CACHE_TTL=300
```

## 📦 Requirements

- Python 3.8+
- Kimi CLI installed (generates data in `~/.kimi/`)

## 🤝 Contributing

Phase 1 (Backend API) - ✅ **COMPLETE**
Phase 2 (Search & Filtering) - 🔛 **IN PROGRESS**
Phase 3 (Activity & Analytics) - 🔛 Planned
Phase 4 (Frontend Dashboard) - 🔛 Planned
Phase 5 (Polish & Optimization) - 🔛 Planned
Phase 6 (Advanced Features) - 🔛 Planned

## 📄 License

MIT License

---

Built for Kimi CLI users ❤️
