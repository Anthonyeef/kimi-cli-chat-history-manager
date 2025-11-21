"""FastAPI application for Kimi CLI Chat History API."""

import logging
from typing import List, Optional, Dict
from pathlib import Path
import json
from datetime import datetime, timedelta

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

try:
    from .api.models import Chat, Message, SearchResult, Workspace, ActivityData, Stats
    from .database.jsonl_reader import read_jsonl
    from .services.chat_service import chat_service
    from .config import settings
except ImportError:
    from api.models import Chat, Message, SearchResult, Workspace, ActivityData, Stats
    from database.jsonl_reader import read_jsonl
    from services.chat_service import chat_service
    from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Kimi CLI Chat History API",
    description="API for searching and managing Kimi CLI conversation history",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Kimi CLI Chat History API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "health": "/api/v1/health",
            "chats": "/api/v1/chats",
            "chat_detail": "/api/v1/chats/{id}",
            "workspaces": "/api/v1/workspaces",
            "search": "/api/v1/search",
            "refresh": "/api/v1/refresh"
        }
    }


@app.get("/api/v1/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "service": "kimi-chat-history-api"}


@app.get("/api/v1/chats", response_model=List[Chat])
async def list_chats(
    workspace: Optional[str] = Query(None, description="Filter by workspace path"),
    limit: int = Query(20, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    refresh: bool = Query(False, description="Force refresh of chat index")
):
    """
    List chat sessions with optional filtering.

    Args:
        workspace: Filter by workspace path
        limit: Maximum number of results to return
        offset: Number of results to skip (for pagination)
        refresh: Force refresh the chat index

    Returns:
        List of Chat objects
    """
    try:
        chats = chat_service.get_all_chats(force_refresh=refresh)

        # Filter by workspace if specified
        if workspace:
            chats = [c for c in chats if c.workspace == workspace]

        # Apply pagination
        total = len(chats)
        chats = chats[offset:offset + limit]

        logger.info(f"Returned {len(chats)} chats (total: {total}, offset: {offset}, limit: {limit})")
        return chats

    except Exception as e:
        logger.error(f"Error listing chats: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/chats/{chat_id}", response_model=List[Message])
async def get_chat_detail(chat_id: str):
    """
    Get details of a specific chat session.

    Args:
        chat_id: Session ID (from Chat.id)

    Returns:
        List of Message objects in the conversation
    """
    try:
        # First verify the chat exists
        chat = chat_service.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(status_code=404, detail=f"Chat not found: {chat_id}")

        # Read messages from JSONL file
        messages = read_jsonl(Path(chat.file_path))

        # Convert to Message objects
        result = []
        for msg in messages:
            # Handle null/empty content gracefully
            content = msg.get("content")
            if content is None:
                content = ""
            
            result.append(Message(
                role=msg.get("role", "unknown"),
                content=content,
                tool_calls=msg.get("tool_calls"),
                tool_call_id=msg.get("tool_call_id"),
                timestamp=None  # We don't have timestamps in JSONL
            ))

        logger.info(f"Returned {len(result)} messages for chat {chat_id}")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting chat detail for {chat_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/workspaces", response_model=List[Workspace])
async def list_workspaces(refresh: bool = Query(False, description="Force refresh of chat index")):
    """
    List all workspaces with session counts.

    Args:
        refresh: Force refresh the chat index

    Returns:
        List of Workspace objects
    """
    try:
        chats = chat_service.get_all_chats(force_refresh=refresh)

        # Group chats by workspace
        workspace_dict = {}
        for chat in chats:
            if chat.workspace not in workspace_dict:
                workspace_dict[chat.workspace] = {
                    "path": chat.workspace,
                    "hash": chat.workspace_hash,
                    "sessions": []
                }
            workspace_dict[chat.workspace]["sessions"].append(chat.id)

        # Convert to Workspace objects
        workspaces = []
        for path, data in workspace_dict.items():
            # Get last session from metadata if possible
            last_session = None
            name = Path(path).name

            workspaces.append(Workspace(
                name=name,
                path=path,
                hash=data["hash"],
                last_session_id=last_session,
                session_count=len(data["sessions"])
            ))

        logger.info(f"Returned {len(workspaces)} workspaces")
        return workspaces

    except Exception as e:
        logger.error(f"Error listing workspaces: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/activity", response_model=Dict[str, List[dict]])
async def get_activity(
    days: int = Query(365, ge=1, le=1095, description="Number of days to include")
):
    """
    Get activity heatmap data for GitHub-style contribution graph.
    
    Args:
        days: Number of days to look back (default: 365 days = 1 year)
    
    Returns:
        Dictionary with activity data by date and workspace
    """
    try:
        chats = chat_service.get_all_chats()
        
        # Generate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Initialize activity data structure
        activity_by_date = {}
        
        # Process all chats
        for chat in chats:
            chat_date = chat.created.date()
            
            # Skip chats outside the date range
            if chat_date < start_date.date() or chat_date > end_date.date():
                continue
            
            date_key = chat_date.isoformat()
            
            if date_key not in activity_by_date:
                activity_by_date[date_key] = {
                    'date': date_key,
                    'count': 0,
                    'chats': []
                }
            
            activity_by_date[date_key]['count'] += 1
            activity_by_date[date_key]['chats'].append({
                'id': chat.id,
                'name': chat.name,
                'workspace': chat.workspace.split('/').pop()
            })
        
        # Fill in missing dates with zeros
        current_date = start_date.date()
        while current_date <= end_date.date():
            date_key = current_date.isoformat()
            if date_key not in activity_by_date:
                activity_by_date[date_key] = {
                    'date': date_key,
                    'count': 0,
                    'chats': []
                }
            current_date += timedelta(days=1)
        
        # Convert to sorted list
        sorted_activity = sorted(
            activity_by_date.values(),
            key=lambda x: x['date']
        )
        
        logger.info(f"Generated activity data for {len(sorted_activity)} days")
        return {'activity': sorted_activity}
    
    except Exception as e:
        logger.error(f"Error generating activity data: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/search", response_model=List[SearchResult])
async def search_chats(
    q: str = Query(..., description="Search query"),
    search_messages: bool = Query(False, description="Search in message content, not just chat names"),
    workspace: Optional[str] = Query(None, description="Filter by workspace path")
):
    """
    Search chat sessions by query.

    Args:
        q: Search query string
        search_messages: If True, search in full message content. If False, search only in chat names.
        workspace: Optional workspace filter

    Returns:
        List of SearchResult objects
    """
    try:
        results = chat_service.search_chats(q, search_messages=search_messages, workspace=workspace)
        logger.info(f"Search for '{q}' (search_messages={search_messages}) returned {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error searching chats: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/v1/stats", response_model=Stats)
async def get_stats():
    """
    Get overall statistics about the chat history.
    
    Returns:
        Stats object with totals and date ranges
    """
    try:
        chats = chat_service.get_all_chats()
        
        if not chats:
            return Stats(
                total_chats=0,
                total_messages=0,
                total_workspaces=0,
                date_range_start=None,
                date_range_end=None
            )
        
        total_chats = len(chats)
        total_messages = sum(chat.message_count for chat in chats)
        total_workspaces = len({chat.workspace for chat in chats})
        
        dates = [chat.created for chat in chats]
        date_range_start = min(dates) if dates else None
        date_range_end = max(dates) if dates else None
        
        return Stats(
            total_chats=total_chats,
            total_messages=total_messages,
            total_workspaces=total_workspaces,
            date_range_start=date_range_start,
            date_range_end=date_range_end
        )
    
    except Exception as e:
        logger.error(f"Error generating stats: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/v1/refresh")
async def refresh_chats():
    """Force refresh the chat index."""
    try:
        chat_service.refresh_cache()
        return {"status": "ok", "message": "Chat index refreshed successfully"}
    except Exception as e:
        logger.error(f"Error refreshing chat index: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Add startup event to initialize the cache
@app.on_event("startup")
async def startup_event():
    """Initialize the chat cache on startup."""
    logger.info("Starting Kimi Chat History API...")
    logger.info(f"Kimi data directory: {settings.kimi_base_dir}")
    chat_service.refresh_cache()
    logger.info("Application started successfully")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=str(settings.host),
        port=int(settings.port),
        reload=True,
        log_level="info"
    )
