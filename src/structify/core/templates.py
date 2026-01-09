"""
Templates module for Structify (AI-driven, using Gemini API , single-helper-file version).

- No static or per-file templates are generated.
- Instead, a single AI-generated helper file (helper.txt) is created at the project root.
- The helper file gives docstring-style suggestions and, if relevant, example code (in comments)
  for each folder and file in the project (recursively).
"""

from typing import List, Dict
import os

SCAFFOLD_NOTE = """NOTE:
This project is a scaffold.
All files are intentionally created empty.
The folder structure is the primary output.
Code, configurations, and implementations are left to the developer by design.

---
"""

def get_project_structure(root_path: str) -> Dict[str, List[str]]:
    """
    Recursively walk the project directory, returning a mapping:
    {folder_path: [file1, file2, ...], ...}
    Folder paths are relative to root_path.
    """
    structure = {}
    for dirpath, dirnames, filenames in os.walk(root_path):
        rel_dir = os.path.relpath(dirpath, root_path)
        rel_dir = "" if rel_dir == "." else rel_dir
        structure[rel_dir] = sorted(filenames)
    return structure

def generate_helper_file_content(
    project_type: str,
    features: List[str],
    helpers: Dict[str, str]
) -> str:
    """
    Generates the content for helper.txt.
    - All generated explanations are expected to be present in `helpers` (produced by parser module).
    - This function is responsible ONLY for formatting helper.txt.
    """

    lines: List[str] = []
    lines.append(SCAFFOLD_NOTE.rstrip())
    lines.append("STRUCTIFY PROJECT HELPER")
    lines.append(f"Project type: {project_type}")
    lines.append(f"Features: {', '.join(features)}")
    lines.append("")
    lines.append("File guidance:")

    if not helpers:
        lines.append("")
        lines.append("⚠️ AI helper content unavailable.")
        lines.append("The project structure was generated successfully,")
        lines.append("but detailed file-level guidance could not be retrieved.")
        return "\n".join(lines)

    for path, explanation in helpers.items():
        lines.append("")
        lines.append(f"{path}:")
        lines.append(f"  {explanation}")

    return "\n".join(lines)

def create_helper_file(
    project_type: str,
    root_path: str,
    features: List[str],
    description: str,
    helpers: Dict[str, str] = {},
    helper_filename: str = "helper.txt"
) -> str:
    """
    Main entry point: generates helper file at project root.
    Returns the path to the helper file.
    """
    project_structure = get_project_structure(root_path)
    content = generate_helper_file_content(project_type,features, helpers)
    helper_path = os.path.join(root_path, helper_filename)
    with open(helper_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[✅] Helper file written: {helper_path}")
    return helper_path