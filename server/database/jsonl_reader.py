"""Read and parse Kimi CLI JSONL session files."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Union
import logging

logger = logging.getLogger(__name__)


def read_jsonl(file_path: Path) -> List[Dict[str, Any]]:
    """
    Read and parse a Kimi CLI JSONL file.

    Args:
        file_path: Path to the JSONL file

    Returns:
        List of message dictionaries
    """
    messages = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)

                    # Skip internal roles that start with underscore
                    role = data.get("role", "")
                    if isinstance(role, str) and role.startswith("_"):
                        continue

                    messages.append(data)

                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON on line {line_num} in {file_path}: {e}")
                    continue

    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise

    return messages


def normalize_content(content: Union[str, List[Dict[str, Any]]]) -> Union[str, List[Dict[str, Any]]]:
    """
    Normalize message content to consistent format.

    Args:
        content: Content as string or list of content parts

    Returns:
        Normalized content
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        # Handle structured content array
        # Convert to consistent format: [{"type": "text", "text": "..."}]
        normalized = []
        for part in content:
            if isinstance(part, dict):
                part_type = part.get("type", "text")
                if "text" in part:
                    normalized.append({"type": part_type, "text": part["text"]})
                elif "think" in part:
                    normalized.append({"type": "think", "text": part["think"]})  # Convert think to text for simplicity
                else:
                    # Fallback: convert to string representation
                    normalized.append({"type": part_type, "text": str(part)})
        return normalized if normalized else content

    return str(content)


def get_first_user_message(messages: List[Dict[str, Any]]) -> str:
    """
    Extract the first user message to use as chat name.

    Args:
        messages: List of message dictionaries

    Returns:
        First user message content or "Untitled Chat"
    """
    for msg in messages:
        if msg.get("role") == "user":
            content = msg.get("content", "")
            if isinstance(content, str):
                return content
            elif isinstance(content, list) and content:
                # For structured content, extract text parts
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        return part.get("text", "Untitled Chat")
    return "Untitled Chat"


def extract_searchable_text(content: Union[str, List[Dict[str, Any]]]) -> str:
    """
    Extract searchable text from message content.

    Args:
        content: Message content (string or list)

    Returns:
        Plain text string for searching
    """
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        texts = []
        for part in content:
            if isinstance(part, dict):
                if "text" in part:
                    texts.append(part["text"])
                elif "think" in part:
                    texts.append(part["think"])
                else:
                    texts.append(str(part))
        return " ".join(texts)

    return str(content)


def count_messages(file_path: Path) -> int:
    """
    Count the number of messages in a JSONL file (excluding internal roles).

    Args:
        file_path: Path to JSONL file

    Returns:
        Message count
    """
    try:
        count = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    role = data.get("role", "")
                    if isinstance(role, str) and not role.startswith("_"):
                        count += 1
                except json.JSONDecodeError:
                    continue
        return count
    except Exception as e:
        logger.error(f"Error counting messages in {file_path}: {e}")
        return 0
