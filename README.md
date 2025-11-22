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
# Install Python dependencies
cd server
pip install -r requirements.txt

# Install Node.js dependencies for the frontend
cd ../web
npm install
cd ..
```

### Step 2: Start the Application

```bash
./start_app.sh
```

This starts both the API server and the SvelteKit dashboard:
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8001/docs

The application will automatically:
- Index all your chats from `~/.kimi/`
- Provide REST API endpoints
- Launch the modern web dashboard

### Step 3: Explore Your Chats

Open http://localhost:5173 in your browser to see your conversation history!

**Features available:**
- Real-time search across all conversations
- GitHub-style activity heatmap
- Filter by workspace
- Click any chat to view full conversation
- Export to Markdown
- Copy session IDs

### Alternative: Run Separately

If you prefer running the servers separately:

**Terminal 1 - API Server:**
```bash
cd server
python3 -m uvicorn main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd web
npm run dev
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
├── web/                        # SvelteKit Frontend
│   ├── src/
│   │   ├── lib/               # Reusable components & utilities
│   │   │   ├── api/           # Type-safe API client
│   │   │   ├── components/    # UI components
│   │   │   ├── stores/        # Reactive state management
│   │   │   └── types.ts       # TypeScript type definitions
│   │   ├── routes/            # File-based routing
│   │   └── app.html           # HTML template
│   ├── static/                # Static assets
│   ├── package.json           # Node.js dependencies
│   ├── svelte.config.js       # SvelteKit configuration
│   └── vite.config.js         # Vite build configuration
├── start_app.sh               # Combined startup script
├── SVELTEKIT_REFACTORING.md   # Technical documentation
├── .env.example               # Environment configuration
└── README.md                  # This file
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
Phase 2 (Search & Filtering) - ✅ **COMPLETE**
Phase 3 (Activity & Analytics) - ✅ **COMPLETE**
Phase 4 (Frontend Dashboard - SvelteKit) - ✅ **COMPLETE**
Phase 5 (Polish & Optimization) - 🔛 Planned
Phase 6 (Advanced Features) - 🔛 Planned

### Development Notes

The dashboard has been completely refactored from a single HTML file to a modern SvelteKit application. See `SVELTEKIT_REFACTORING.md` for technical details.

**Key improvements:**
- ✅ TypeScript for type safety
- ✅ Component-based architecture
- ✅ File-based routing with clean URLs
- ✅ Reactive state management
- ✅ Same-origin API (no CORS issues)
- ✅ Modern developer experience

## 📄 License

MIT License

---

Built for Kimi CLI users ❤️
