# Technical Specification: Kimi CLI Chat History Dashboard

## Project Overview

Build a chat history search and management dashboard for Kimi CLI that mirrors the architecture and UI of cursor-chat-history, but adapts to Kimi's JSONL-based data structure.

## Reference Architecture

Based on: `/Users/yifen/Workspace/cursor-chat-history` (FastAPI + Vanilla JS dashboard)

## Kimi CLI Data Architecture

### Storage Structure

```
~/.kimi/
├── kimi.json                    # Metadata: work_dirs list, thinking mode
├── sessions/
│   └── {workspace_hash}/        # MD5 hash of workspace path
│       ├── {session_id}.jsonl   # Main session (full messages)
│       ├── {session_id}_sub_1.jsonl  # Sub-sessions (sub-tasks)
│       └── {session_id}_sub_2.jsonl
└── user-history/
    └── {workspace_hash}.jsonl   # User message summaries only
```

### Data Format

**Session JSONL Format** (`~/.kimi/sessions/{hash}/{session}.jsonl`):
```json
{"role": "user", "content": "Check this repository"}
{"role": "assistant", "content": [{"type": "think", "think": "..."}, {"type": "text", "text": "..."}], "tool_calls": [...]}
{"role": "tool", "content": "...", "tool_call_id": "..."}
{"role": "user", "content": "Another user message"}
{"role": "_usage", "token_count": 5444}
{"role": "_checkpoint", "id": 1}
```

**User History JSONL Format** (`~/.kimi/user-history/{hash}.jsonl`):
```json
{"content": "Check this repository"}
{"content": "How do I deploy this?"}
{"content": "Fix the bug in authentication"}
```

**Metadata Format** (`~/.kimi/kimi.json`):
```json
{
  "work_dirs": [
    {
      "path": "/Users/yifen/Workspace/kimi-cli",
      "last_session_id": "59233f8f-59b7-4d79-919c-a1225300c7e2"
    }
  ],
  "thinking": false
}
```

## Component Architecture

### 1. Backend API Server (FastAPI)

**File Structure:**
```
kimi-chat-history/
├── server/
│   ├── main.py                    # FastAPI app entry point
│   ├── config.py                  # Configuration settings
│   ├── requirements.txt           # Python dependencies
│   ├── api/
│   │   ├── __init__.py
│   │   └── models.py             # Pydantic models (Chat, Message, SearchResult)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── chat_service.py       # Business logic for parsing/loading chats
│   │   └── workspace_service.py  # Workspace discovery and mapping
│   ├── database/
│   │   ├── __init__.py
│   │   └── jsonl_reader.py       # Read and parse JSONL files
│   └── tests/
│       └── test_api.py           # API tests
```

**Key Differences from Cursor Implementation:**

1. **No SQLite indexing** - Direct JSONL file reading
2. **Metadata-based discovery** - Parse `kimi.json` for workspace list
3. **Directory scanning** - List `~/.kimi/sessions/{hash}/` for sessions
4. **Sub-session support** - Include `*_sub_*.jsonl` files as related chats
5. **On-demand file reading** - Read JSONL files when accessed (no pre-indexing)

**API Endpoints:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/chats` | List chats with filters |
| GET | `/api/v1/chats/:id` | Get specific chat by session ID |
| POST | `/api/v1/search` | Search chats (name + content) |
| GET | `/api/v1/activity` | Get GitHub-style activity data |
| GET | `/api/v1/workspaces` | List all workspaces |
| POST | `/api/v1/refresh` | Refresh index (re-scan directories) |

**Data Models:**

```python
# api/models.py
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class Chat(BaseModel):
    id: str                          # Session ID (UUID)
    name: str                        # First N chars of first user message
    workspace: str                   # Workspace path
    workspace_hash: str              # MD5 hash of workspace path
    created: datetime                # From file creation time
    message_count: int               # Total messages in session
    has_subsessions: bool            # Has sub-session files
    sub_sessions: List[str]          # List of sub-session IDs
    file_path: str                   # Path to JSONL file

class Message(BaseModel):
    role: str                        # user, assistant, tool, system
    content: str | List[dict]        # Text or structured content parts
    tool_calls: Optional[List[dict]] = None
    tool_call_id: Optional[str] = None
    timestamp: Optional[datetime] = None

class SearchResult(BaseModel):
    chat: Chat
    matches: List[dict]              # List of matching messages with highlights
    match_count: int                 # Number of matching messages
```

### 2. Frontend Dashboard (HTML/CSS/JS)

**File Structure:**
```
kimi-chat-history/
├── dashboard/
│   └── index.html                 # Single file with embedded CSS/JS
└── docs/
    ├── dashboard-screenshot.png
    └── README.md
```

**Key UI Components (reusing cursor-chat-history design):**

1. **Activity Heatmap** (Top)
   - GitHub-style contribution graph
   - Shows conversation frequency over time
   - Click date to filter chats by day

2. **Search & Filter Panel** (Left Sidebar)
   - Search box (searches both chat names and message content)
   - Filter by workspace (dropdown from `/api/v1/workspaces`)
   - Sort options: recent, message count, name
   - "Search in messages" toggle (searches full content vs just names)

3. **Chat List** (Main Area)
   - Scrollable list of conversation cards
   - Each card shows:
     - Chat name (truncated first message)
     - Timestamp (e.g., "2 hours ago")
     - Workspace name
     - Message count
     - Session ID (small, copy button)
   - Pagination: 20 chats per page

4. **Chat Detail Modal** (Overlay)
   - Click chat card to open
   - Full conversation viewer
   - Shows all messages with:
     - User messages (highlighted)
     - Assistant responses (with "think" blocks expandable)
     - Tool calls and results
   - Export to Markdown button
   - Copy session ID button

**Key Adaptations for Kimi:**
- Handle structured content arrays (not just plain text)
- Support "think" blocks (collapsible)
- Show tool calls in formatted way
- Link sub-sessions to main sessions

### 3. Data Processing Pipeline

**Chat Discovery (on server start):**
```python
# services/chat_service.py

def discover_chats() -> List[Chat]:
    """Discover all chat sessions from ~/.kimi/"""
    chats = []

    # 1. Load metadata to get workspace list
    metadata = load_metadata("~/.kimi/kimi.json")

    # 2. For each workspace, scan sessions directory
    for work_dir in metadata.work_dirs:
        ws_hash = md5(work_dir.path.encode()).hexdigest()
        sessions_dir = Path("~/.kimi/sessions") / ws_hash

        # 3. Find all JSONL files (including sub-sessions)
        for jsonl_file in sessions_dir.glob("*.jsonl"):
            session_id = jsonl_file.stem  # Remove .jsonl

            # Parse session file to extract metadata
            messages = read_jsonl(jsonl_file)
            first_message = get_first_user_message(messages)

            chat = Chat(
                id=session_id,
                name=truncate(first_message, 50),
                workspace=work_dir.path,
                workspace_hash=ws_hash,
                created=datetime.fromtimestamp(jsonl_file.stat().st_ctime),
                message_count=len(messages),
                has_subsessions=has_subsessions(session_id, sessions_dir),
                sub_sessions=get_subsessions(session_id, sessions_dir),
                file_path=str(jsonl_file)
            )
            chats.append(chat)

    return chats
```

**Message Parsing:**
```python
# database/jsonl_reader.py

def read_jsonl(file_path: Path) -> List[Message]:
    """Read and parse a JSONL file"""
    messages = []

    with open(file_path, 'r') as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line)

                # Skip internal roles (_usage, _checkpoint, _subtask, etc.)
                if data.get("role", "").startswith("_"):
                    continue

                message = Message(
                    role=data["role"],
                    content=normalize_content(data["content"]),
                    tool_calls=data.get("tool_calls"),
                    tool_call_id=data.get("tool_call_id"),
                    timestamp=estimate_timestamp(file_path, line_num)
                )
                messages.append(message)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON on line {line_num}")
                continue

    return messages

def normalize_content(content: str | list) -> str | list:
    """Normalize content to consistent format"""
    if isinstance(content, str):
        return content

    # Handle structured content array
    # [{"type": "text", "text": "..."}, {"type": "think", "think": "..."}]
    return [
        {
            "type": part.get("type", "text"),
            "text": part.get("text", part.get("think", ""))
        }
        for part in content
    ]
```

**Search Implementation:**
```python
# services/chat_service.py

def search_chats(query: str, search_messages: bool = False) -> List[SearchResult]:
    """
    Search chats by name or message content

    - If search_messages=False: Search only in chat names (metadata)
    - If search_messages=True: Search in full message content from JSONL files
    """
    results = []

    if not search_messages:
        # Fast path: Search in chat name only
        chats = get_all_chats()
        matching_chats = [c for c in chats if query.lower() in c.name.lower()]
        return [SearchResult(chat=c, matches=[], match_count=0) for c in matching_chats]

    # Deep search: Scan all session files
    for chat in get_all_chats():
        matches = []
        messages = read_jsonl(chat.file_path)

        for idx, msg in enumerate(messages):
            # Check if query matches in message content
            text = extract_searchable_text(msg.content)
            if query.lower() in text.lower():
                matches.append({
                    "message_index": idx,
                    "role": msg.role,
                    "preview": truncate(text, 100),
                    "highlighted": highlight_matches(text, query)
                })

        if matches:
            results.append(SearchResult(
                chat=chat,
                matches=matches,
                match_count=len(matches)
            ))

    return results
```

### 4. Caching Strategy

**Server-Side Caching:**
```python
# config.py
CACHE_TTL = 300  # 5 minutes

discovered_chats_cache = {
    "data": [],
    "last_updated": None,
    "lock": threading.Lock()
}

def get_cached_chats():
    """Get cached chat list or refresh if expired"""
    global discovered_chats_cache

    with discovered_chats_cache["lock"]:
        if discovered_chats_cache["last_updated"] is None or \
           time.time() - discovered_chats_cache["last_updated"] > CACHE_TTL:
            # Cache expired or empty, refresh
            discovered_chats_cache["data"] = discover_chats()
            discovered_chats_cache["last_updated"] = time.time()

        return discovered_chats_cache["data"]
```

**Client-Side Caching:**
- Browser caches API responses
- Stale-while-revalidate pattern for smooth UI

### 5. Auto-Refresh Mechanism

**Background Refresh:**
```python
# main.py

@app.on_event("startup")
async def start_background_refresh():
    """Start background task to refresh chat index periodically"""
    async def refresh_task():
        while True:
            await asyncio.sleep(AUTO_REFRESH_INTERVAL)  # Default: 300s
            logger.info("Auto-refreshing chat index...")
            await refresh_chats()

    asyncio.create_task(refresh_task())
```

**Manual Refresh Endpoint:**
- `POST /api/v1/refresh` - Force immediate refresh
- Called by dashboard on page load or when user clicks refresh button

## Implementation Phases

### Phase 1: Core Backend API (Day 1-2)
- [ ] Set up FastAPI project structure
- [ ] Create JSONL reader module
- [ ] Implement chat discovery from `~/.kimi/sessions/`
- [ ] Create API models (Chat, Message, SearchResult)
- [ ] Implement `/api/v1/chats` endpoint (list chats)
- [ ] Implement `/api/v1/chats/:id` endpoint (get chat details)
- [ ] Add basic error handling and logging

### Phase 2: Search & Filtering (Day 3)
- [ ] Implement metadata search (chat names only)
- [ ] Implement full-text message search (scan JSONL files)
- [ ] Add workspace filter support
- [ ] Implement `/api/v1/search` endpoint
- [ ] Implement `/api/v1/workspaces` endpoint

### Phase 3: Activity & Analytics (Day 4)
- [ ] Parse timestamps from file metadata
- [ ] Implement activity heatmap data generation
- [ ] Create `/api/v1/activity` endpoint
- [ ] Add statistics endpoint (`/api/v1/stats`)
- [ ] Implement caching mechanism

### Phase 4: Frontend Dashboard (Day 5-6)
- [ ] Copy and adapt cursor-chat-history dashboard HTML/CSS/JS
- [ ] Connect to new API endpoints
- [ ] Modify UI for Kimi-specific features:
  - Handle structured content arrays
  - Support "think" blocks
  - Show tool call information
- [ ] Test chat detail modal
- [ ] Add export to Markdown functionality

### Phase 5: Polish & Optimization (Day 7)
- [ ] Implement auto-refresh mechanism
- [ ] Add loading states and error messages
- [ ] Optimize search performance
- [ ] Add truncate limits for large messages
- [ ] Add syntax highlighting for code blocks
- [ ] Test with large session files (>10MB)
- [ ] Write README and documentation

### Phase 6: Advanced Features (Day 8-9)
- [ ] Link sub-sessions to main sessions in UI
- [ ] Add session ID copy button
- [ ] Add "Resume Session" instructions
- [ ] Add dark mode toggle
- [ ] Add keyboard shortcuts
- [ ] Improve mobile responsiveness
- [ ] Add API client examples (Python, curl)

## Technical Considerations

### Performance Optimizations

1. **Lazy Loading**: Don't load full session files until viewing chat details
2. **File Size Handling**: For large JSONL files (>10MB):
   - Show only first N messages in list view
   - Paginate detail view
   - Add warning for very large files
3. **Search Performance**: For deep search:
   - Use `ripgrep` for faster file scanning
   - Parallelize search across session files
   - Implement result streaming for large datasets

### Data Consistency

1. **File Watching**: Monitor `~/.kimi/` directory for new sessions
2. **Inotify/FSEvents**: Use OS file system events to detect changes
3. **Graceful Degradation**: Handle malformed JSON gracefully

### Error Handling

1. **Missing Files**: Handle deleted/moved session files
2. **Malformatted JSON**: Skip invalid lines, log warnings
3. **Permission Errors**: Check file permissions, show user-friendly errors
4. **Missing Workspaces**: Handle workspaces from metadata that no longer exist

## Configuration

**Environment Variables (`.env`):**
```bash
# FastAPI Server
HOST=127.0.0.1
PORT=8001

# CORS (allow local file access)
CORS_ORIGINS=["http://localhost:8001", "null"]

# Caching
CACHE_TTL=300  # 5 minutes

# Auto-refresh
AUTO_REFRESH_INTERVAL=300  # 5 minutes

# Paths
KIMI_DATA_DIR=~/.kimi/
```

**Runtime Configuration:**
```python
# server/config.py
from pathlib import Path

class Config:
    KIMI_BASE_DIR = Path.home() / ".kimi"
    METADATA_FILE = KIMI_BASE_DIR / "kimi.json"
    SESSIONS_DIR = KIMI_BASE_DIR / "sessions"
    USER_HISTORY_DIR = KIMI_BASE_DIR / "user-history"

    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # Truncation
    MAX_CHAT_NAME_LENGTH = 50
    MAX_MESSAGE_PREVIEW = 100
    MAX_DETAIL_MESSAGES = 1000  # Limit for detail view
```

## UI Features Reuse from cursor-chat-history

### Features to Keep:
- ✅ GitHub-style activity heatmap
- ✅ Real-time search and filtering
- ✅ Chat list cards with preview
- ✅ Full conversation viewer modal
- ✅ Export to Markdown
- ✅ Copy session ID button
- ✅ Syntax highlighting for code blocks
- ✅ Responsive design

### Features to Adapt:
- 🔧 Handle Kimi's structured content format (vs Cursor's simpler format)
- 🔧 Show "think" blocks with expand/collapse
- 🔧 Link sub-sessions to main sessions
- 🔧 Show tool call information

### Optional Enhancements:
- 🎯 Dark mode toggle
- 🎯 Search within conversation
- 🎯 Copy individual messages
- 🎯 Message role icons/labels
- 🎯 Tool usage stats per chat

## Testing Strategy

### Unit Tests
```python
# tests/test_jsonl_reader.py
def test_read_valid_jsonl():
def test_skip_internal_roles():
def test_normalize_content():

# tests/test_chat_service.py
def test_discover_chats():
def test_search_messages():
def test_activity_data_generation():
```

### Integration Tests
```python
# tests/test_api.py
def test_list_chats_endpoint(client):
def test_search_endpoint(client):
def test_chat_detail_endpoint(client):
```

### Manual Testing Checklist
- [ ] Start server, verify it discovers all chats
- [ ] Open dashboard, check activity heatmap
- [ ] Search by chat name
- [ ] Enable "search in messages", verify deep search works
- [ ] Click chat card, verify detail modal opens
- [ ] View conversation with tool calls
- [ ] Export chat to Markdown
- [ ] Create new Kimi session, verify auto-refresh
- [ ] Test with large session file (>10MB)
- [ ] Test with malformed JSON in session file

## Deployment

### Development
```bash
cd server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

### Production
```bash
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8001
```

Or use systemd service:
```ini
[Unit]
Description=Kimi Chat History API
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/kimi-chat-history/server
Environment=PATH=/path/to/venv/bin
ExecStart=/path/to/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Future Enhancements

### Potential Features
- [ ] WebSocket for real-time chat updates (watch file system)
- [ ] Authentication system (multiple users)
- [ ] Browser extension (access dashboard from browser)
- [ ] Advanced analytics (token usage, tool usage patterns)
- [ ] Conversation summaries (AI-generated)
- [ ] Chat tagging and categorization
- [ ] Shared workspaces (team mode)
- [ ] MCP server integration (expose chat history as MCP tool)

### Performance Improvements
- [ ] Full-text search with SQLite FTS5
- [ ] Background indexing of large files
- [ ] Message compression for storage
- [ ] CDN for static assets
- [ ] Redis for caching

## Appendix

### Example JSONL File Structure

```json
{"role": "_checkpoint", "id": 0}
{"role":"user","content":"check this repository"}
{"role": "_usage", "token_count": 5444}
{"role":"assistant","content":[{"type":"think","think":"The user wants me to check this repository..."},{"type":"text","text":"I'll explore the repository to understand its structure and purpose."}],"tool_calls":[{"type":"function","function":{"name":"ReadFile","arguments":"{\"path\": \"/Users/yifen/Workspace/cursor-as-bridge/README.md\"}"}}]}
{"role":"tool","content":[{"type":"text","text":"<README.md content>"}],"tool_call_id":"tool_auqUFDMYKO0rpeo8DUO6O1Q3"}
{"role":"assistant","content":"I can see this is a JetBrains plugin that..."}
{"role": "_checkpoint", "id": 1}
{"role":"user","content":"great! now explain the architecture"}
```

### Workspace Hash Mapping

The MD5 hash of workspace paths allows Kimi to:
- Avoid storing full paths in multiple places
- Handle special characters in paths
- Enable workspace-level organization
- Keep metadata lightweight

Example:
- Path: `/Users/yifen/Workspace/kimi-cli`
- Hash: `0731649bc3652654589520d4901c0d8c`
- Sessions: `~/.kimi/sessions/0731649bc3652654589520d4901c0d8c/`

---

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Status:** Ready for Implementation
