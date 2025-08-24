# structify/core/utils.py

"""
Utility functions for Structify.
Handles path setup, file/directory creation, and file writing.
"""

import os
from pathlib import Path


def ensure_dir(path: str) -> None:
    """
    Ensure a directory exists (create if missing).
    
    Args:
        path (str): Path of the directory
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def write_file(path: str, content: str) -> None:
    """
    Write content to a file, creating directories if needed.
    
    Args:
        path (str): File path
        content (str): File content
    """
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def safe_join(base: str, *paths: str) -> str:
    """
    Safely join paths to avoid escaping outside the project root.
    
    Args:
        base (str): Base directory
        *paths: Additional path components
    
    Returns:
        str: Safe joined path
    """
    base_path = Path(base).resolve()
    final_path = (base_path.joinpath(*paths)).resolve()

    if not str(final_path).startswith(str(base_path)):
        raise ValueError("Attempted to write outside of project root")

    return final_path


def file_exists(path: str) -> bool:
    """Check if a file exists."""
    return Path(path).exists()


def read_file(path: str) -> str:
    """Read a file’s content (if exists)."""
    if not file_exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
