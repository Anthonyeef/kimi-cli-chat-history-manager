"""Service for discovering and loading chat sessions."""

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

try:
    from ..database.jsonl_reader import read_jsonl, get_first_user_message, extract_searchable_text
    from ..api.models import Chat, SearchResult, SearchMatch
    from ..config import settings
except ImportError:
    from database.jsonl_reader import read_jsonl, get_first_user_message, extract_searchable_text
    from api.models import Chat, SearchResult, SearchMatch
    from config import settings

logger = logging.getLogger(__name__)


class ChatService:
    """Service for managing chat discovery and retrieval."""

    def __init__(self):
        self._discovered_chats: Optional[List[Chat]] = None
        self._chats_by_id: Optional[Dict[str, Chat]] = None
        self._last_refresh: Optional[datetime] = None

    def refresh_cache(self) -> None:
        """Refresh the discovered chats cache."""
        logger.info("Refreshing chat cache...")
        chats = self._discover_chats()
        self._discovered_chats = chats
        self._chats_by_id = {chat.id: chat for chat in chats}
        self._last_refresh = datetime.now()
        logger.info(f"Discovered {len(chats)} chats across {len(set(c.workspace for c in chats))} workspaces")

    def get_all_chats(self, force_refresh: bool = False) -> List[Chat]:
        """
        Get all discovered chats.

        Args:
            force_refresh: Force a refresh of the cache

        Returns:
            List of Chat objects
        """
        if force_refresh or self._discovered_chats is None:
            self.refresh_cache()
        return self._discovered_chats or []

    def get_chat_by_id(self, chat_id: str) -> Optional[Chat]:
        """
        Get a specific chat by ID.

        Args:
            chat_id: Session ID

        Returns:
            Chat object or None if not found
        """
        if self._chats_by_id is None:
            self.refresh_cache()
        return self._chats_by_id.get(chat_id) if self._chats_by_id else None

    def _discover_chats(self) -> List[Chat]:
        """
        Discover all chat sessions from ~/.kimi/.

        Returns:
            List of Chat objects
        """
        chats = []

        # Load metadata to get workspace information
        metadata = self._load_metadata()

        # If no metadata, scan sessions directory
        if not metadata:
            return self._scan_sessions_directly()

        # For each workspace in metadata, discover sessions
        workspace_paths = [wd.get("path", "") for wd in metadata.get("work_dirs", [])]

        for workspace_path in workspace_paths:
            if not workspace_path:
                continue

            workspace_hash = self._hash_workspace_path(workspace_path)
            workspace_chats = self._discover_workspace_chats(workspace_path, workspace_hash)
            chats.extend(workspace_chats)

        return chats

    def _load_metadata(self) -> Optional[Dict[str, Any]]:
        """Load metadata from kimi.json."""
        try:
            if not settings.metadata_file.exists():
                logger.warning(f"Metadata file not found: {settings.metadata_file}")
                return None

            with open(settings.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata: {e}")
            return None

    def _hash_workspace_path(self, path: str) -> str:
        """Generate MD5 hash of workspace path."""
        return hashlib.md5(path.encode('utf-8')).hexdigest()

    def _discover_workspace_chats(self, workspace_path: str, workspace_hash: str) -> List[Chat]:
        """
        Discover all chats for a specific workspace.

        Args:
            workspace_path: Full path to workspace
            workspace_hash: MD5 hash of workspace path

        Returns:
            List of Chat objects
        """
        chats = []
        session_dir = settings.sessions_dir / workspace_hash

        if not session_dir.exists():
            logger.debug(f"Session directory does not exist: {session_dir}")
            return chats

        # Find all JSONL files in the session directory
        jsonl_files = list(session_dir.glob("*.jsonl"))

        for jsonl_file in jsonl_files:
            filename = jsonl_file.name

            # Skip sub-session files for now (handle them separately)
            if "_sub_" in filename:
                continue

            session_id = filename.replace(".jsonl", "")

            try:
                # Read session to get metadata
                messages = read_jsonl(jsonl_file)
                first_message = get_first_user_message(messages)

                # Get sub-sessions
                sub_sessions = self._get_sub_sessions(session_id, session_dir)

                # Create chat object
                chat = Chat(
                    id=session_id,
                    name=self._truncate(first_message, settings.max_chat_name_length),
                    workspace=workspace_path,
                    workspace_hash=workspace_hash,
                    created=datetime.fromtimestamp(jsonl_file.stat().st_ctime),
                    message_count=len([m for m in messages if m.get("role", "").startswith("_") is False]),
                    has_subsessions=len(sub_sessions) > 0,
                    sub_sessions=sub_sessions,
                    file_path=str(jsonl_file)
                )
                chats.append(chat)

            except Exception as e:
                logger.error(f"Error processing session file {jsonl_file}: {e}")
                continue

        return chats

    def _get_sub_sessions(self, session_id: str, session_dir: Path) -> List[str]:
        """
        Get sub-session IDs for a main session.

        Args:
            session_id: Main session ID
            session_dir: Directory containing session files

        Returns:
            List of sub-session IDs
        """
        sub_sessions = []
        pattern = f"{session_id}_sub_*.jsonl"
        for sub_file in session_dir.glob(pattern):
            sub_id = sub_file.name.replace(".jsonl", "")
            sub_sessions.append(sub_id)
        return sub_sessions

    def _scan_sessions_directly(self) -> List[Chat]:
        """
        Scan sessions directory directly when metadata is unavailable.

        Returns:
            List of Chat objects
        """
        chats = []

        if not settings.sessions_dir.exists():
            logger.warning(f"Sessions directory not found: {settings.sessions_dir}")
            return chats

        # Find all session directories (hashed workspace paths)
        for session_subdir in settings.sessions_dir.iterdir():
            if not session_subdir.is_dir():
                continue

            workspace_hash = session_subdir.name

            # Try to find workspace path from history files
            workspace_path = self._guess_workspace_path(workspace_hash)

            # Discover chats in this workspace
            workspace_chats = self._discover_workspace_chats(workspace_path, workspace_hash)
            chats.extend(workspace_chats)

        return chats

    def _guess_workspace_path(self, workspace_hash: str) -> str:
        """
        Guess workspace path from hash (uses actual lookup when possible).

        Args:
            workspace_hash: MD5 hash of workspace path

        Returns:
            Workspace path or "Unknown Workspace" if not found
        """
        metadata = self._load_metadata()
        if metadata:
            for wd in metadata.get("work_dirs", []):
                path = wd.get("path", "")
                if self._hash_workspace_path(path) == workspace_hash:
                    return path

        return f"Unknown Workspace ({workspace_hash[:8]}...)"

    def search_chats(self, query: str, search_messages: bool = False, workspace: Optional[str] = None) -> List[SearchResult]:
        """
        Search chats by query.

        Args:
            query: Search string
            search_messages: If True, search in message content. If False, search only chat names.
            workspace: Optional workspace filter

        Returns:
            List of SearchResult objects
        """
        # Use already imported modules (no local imports needed)

        all_chats = self.get_all_chats()
        results = []

        # Filter by workspace first if specified
        if workspace:
            all_chats = [c for c in all_chats if c.workspace == workspace]

        if not search_messages:
            # Fast path: search only in chat names
            matching_chats = [c for c in all_chats if query.lower() in c.name.lower()]
            for chat in matching_chats:
                results.append(SearchResult(
                    chat=chat,
                    matches=[],
                    match_count=0
                ))
            return results

        # Deep search: scan all session files for message content
        for chat in all_chats:
            try:
                messages = read_jsonl(Path(chat.file_path))
                matches = []

                for idx, msg in enumerate(messages):
                    # Check if query matches in message content
                    content = msg.get("content", "")
                    text = extract_searchable_text(content)

                    if query.lower() in text.lower():
                        # Create preview with truncation
                        preview = text[:100] + "..." if len(text) > 100 else text

                        # Simple highlighting (just for preview)
                        highlighted = preview.replace(query, f"**{query}**")

                        matches.append(SearchMatch(
                            message_index=idx,
                            role=msg.get("role", "unknown"),
                            preview=preview,
                            highlighted=highlighted
                        ))

                if matches:
                    results.append(SearchResult(
                        chat=chat,
                        matches=matches,
                        match_count=len(matches)
                    ))

            except Exception as e:
                logger.warning(f"Error searching in chat {chat.id}: {e}")
                continue

        return results

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."


# Global instance
chat_service = ChatService()
