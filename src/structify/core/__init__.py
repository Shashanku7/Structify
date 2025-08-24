"""
Core module of Structify.
Exposes the main parsing and project generation APIs.
"""

from .parser import parse
from .generator import generate_project

__all__ = [
    "parse",
    "generate_project",
]