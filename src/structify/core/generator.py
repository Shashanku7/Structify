"""
Generator module for Structify (AI-driven, helper-file only).

Creates project folders and files based on structured project definitions
produced by parser.py, with all files created empty.
After all files/folders are created, generates a single AI-powered helper file via create_helper_file.
"""

from pathlib import Path
import yaml
import re
from datetime import datetime

from ..config import CONFIG_PATH
from .utils import ensure_dir, write_file, safe_join
from .templates import create_helper_file  # <-- NEW

def load_defaults(project_type: str) -> dict:
    """Load default project structure from YAML. Used only as fallback if AI fails."""
    try:
        with open(CONFIG_PATH, "r") as f:
            defaults = yaml.safe_load(f)
        return defaults.get(project_type, defaults.get("generic", {}))
    except Exception as e:
        print(f"[⚠️] Failed to load defaults: {e}")
        return {"folders": ["src"], "files": ["README.md", "main.py"]}

def merge_structures(defaults: dict, custom: dict) -> dict:
    """Merge AI-driven custom structure with defaults."""
    merged = {}
    merged["folders"] = sorted(set(str(f).rstrip("/") for f in defaults.get("folders", []) + custom.get("folders", [])))
    merged["files"] = sorted(set(custom.get("files", []) + defaults.get("files", [])))
    merged["project_type"] = custom.get("project_type", "generic")
    merged["description"] = custom.get("description", "Structify Project")
    merged["features"] = custom.get("features", [])
    merged["project_name"] = custom.get("project_name", None)
    return merged

MAX_FOLDERNAME_LENGTH = 35

def sanitize_folder_name(name: str) -> str:
    """
    Helper to sanitize a string for use as a folder name.
    Removes invalid characters, trims whitespace, replaces spaces with underscores,
    and limits the length. Adds a timestamp for uniqueness.
    """
    name = name or "Project"
    name = re.sub(r'[^a-zA-Z0-9_\- ]+', '', name)
    name = name.strip().replace(' ', '_')
    name = name[:MAX_FOLDERNAME_LENGTH]
    suffix = datetime.now().strftime("%Y%m%d%H%M%S")
    folder_name = f"{name}_{suffix}"
    return folder_name or f"Project_{suffix}"

def clean_paths(paths):
    """
    Remove leading/trailing slashes, dots, spaces from all paths.
    Ensures all paths are relative and safe for use within the project subfolder.
    """
    cleaned = []
    for p in paths:
        p = p.strip().lstrip("/.\\ ").rstrip("/\\ ")
        if p and p != '.':
            cleaned.append(p)
    return cleaned

def generate_project(structure: dict, output_dir: str = "generated_project") -> None:
    """Generate folders and files from AI-driven project structure, each project in its own subfolder."""
    defaults = load_defaults(structure.get("project_type", "generic"))
    merged_structure = merge_structures(defaults, structure)

    # Use project_name if present, otherwise use sanitized description, else 'Project'
    project_name = (
        merged_structure.get("project_name")
        or merged_structure.get("description")
        or "Project"
    )
    project_folder = sanitize_folder_name(project_name)
    base = Path(output_dir) / project_folder
    ensure_dir(base)

    # Sanitize folder and file paths to prevent absolute/wrong paths
    merged_structure["folders"] = clean_paths(merged_structure.get("folders", []))
    merged_structure["files"] = clean_paths(merged_structure.get("files", []))

    for folder in merged_structure["folders"]:
        folder_path = safe_join(base, folder)
        ensure_dir(folder_path)
    for file in merged_structure["files"]:
        file_path = safe_join(base, file)
        ensure_dir(file_path.parent)
        write_file(file_path, "")  # Create empty file

    # After structure is created, generate the AI helper file
    create_helper_file(
        project_type=merged_structure["project_type"],
        root_path=base,
        features=merged_structure.get("features", []),
        description=merged_structure.get("description", "")
    )
    print(f"[✅] AI-driven project generated at: {base.resolve()}")