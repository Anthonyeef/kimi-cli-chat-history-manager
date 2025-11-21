"""Pydantic models for API responses."""

from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field


class Message(BaseModel):
    """A message in a chat session."""

    role: str = Field(description="Message role: user, assistant, tool, or system")
    content: Union[str, List[dict]] = Field(description="Message content (text or structured array)")
    tool_calls: Optional[List[dict]] = Field(default=None, description="Tool calls made by assistant")
    tool_call_id: Optional[str] = Field(default=None, description="ID of the tool call")
    timestamp: Optional[datetime] = Field(default=None, description="Message timestamp")


class Chat(BaseModel):
    """A chat session."""

    id: str = Field(description="Session ID (UUID)")
    name: str = Field(description="Truncated first user message")
    workspace: str = Field(description="Full workspace path")
    workspace_hash: str = Field(description="MD5 hash of workspace path")
    created: datetime = Field(description="Session creation timestamp")
    message_count: int = Field(description="Total messages in session")
    has_subsessions: bool = Field(description="Whether session has sub-sessions")
    sub_sessions: List[str] = Field(default_factory=list, description="List of sub-session IDs")
    file_path: str = Field(description="Path to JSONL file")


class SearchMatch(BaseModel):
    """A matching message in search results."""

    message_index: int = Field(description="Index of message in conversation")
    role: str = Field(description="Message role")
    preview: str = Field(description="Preview of matching message")
    highlighted: str = Field(description="Preview with query highlights")


class SearchResult(BaseModel):
    """Search result containing chat and matching messages."""

    chat: Chat = Field(description="The chat session")
    matches: List[SearchMatch] = Field(default_factory=list, description="List of matching messages")
    match_count: int = Field(description="Number of matching messages")


class Workspace(BaseModel):
    """A workspace (project directory)."""

    name: str = Field(description="Workspace name (directory name)")
    path: str = Field(description="Full workspace path")
    hash: str = Field(description="MD5 hash of path")
    last_session_id: Optional[str] = Field(default=None, description="Last session ID")
    session_count: int = Field(default=0, description="Number of sessions")


class ActivityData(BaseModel):
    """Activity data for heatmap visualization."""

    date: str = Field(description="Date in YYYY-MM-DD format")
    count: int = Field(description="Number of chats on this date")
    chats: List[str] = Field(default_factory=list, description="List of chat IDs")


class Stats(BaseModel):
    """Statistics about chat history."""

    total_chats: int = Field(description="Total number of chat sessions")
    total_messages: int = Field(description="Total number of messages")
    total_workspaces: int = Field(description="Total number of workspaces")
    date_range_start: Optional[datetime] = Field(default=None, description="Earliest chat date")
    date_range_end: Optional[datetime] = Field(default=None, description="Latest chat date")
