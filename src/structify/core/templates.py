"""
Templates module for Structify (AI-driven, using Gemini API , single-helper-file version).

- No static or per-file templates are generated.
- Instead, a single AI-generated helper file (helper.txt) is created at the project root.
- The helper file gives docstring-style suggestions and, if relevant, example code (in comments)
  for each folder and file in the project (recursively).
"""

from typing import List, Dict
import os

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
    project_structure: Dict[str, List[str]],
    features: List[str],
    description: str
) -> str:
    """
    Generate the content for helper.txt using Gemini.
    Includes docstring-style suggestions and relevant example code (as comments) for each file/folder.
    """
    try:
        from .parser import smart_ai_request
        # Prepare a summary of the structure for the prompt
        structure_str = ""
        for folder, files in project_structure.items():
            prefix = f"{folder}/" if folder else ""
            for file in files:
                structure_str += f"- {prefix}{file}\n"
        prompt = f"""
You are an expert software project architect.

Given a {project_type} project with this description:
{description}

Features requested: {', '.join(features)}

Here is the list of files and folders in the project:

{structure_str}

For each folder and file (recursively), write a docstring-style suggestion (and a short example code as a comment if relevant) describing what should be implemented there.
Use the appropriate comment style for each file type (e.g., triple quotes for Python, // for JS, etc).
Organize your answer clearly by folder.
DO NOT write actual implementation except possibly a short illustrative code snippet inside the docstring/comment if relevant.
Output only the helper file content, suitable for saving as helper.txt.
"""
        _, content = smart_ai_request(prompt, max_tokens=30000)
        if content and len(content.strip()) > 10:
            return content.strip()
    except Exception as e:
        print(f"[⚠️] Gemini helper file generation failed: {e}")

    # Minimal fallback if AI fails
    helper_lines = [
        f"STRUCTIFY PROJECT HELPER",
        f"Project type: {project_type}",
        f"Description: {description}",
        f"Features: {', '.join(features)}",
        "",
        "Project structure and suggestions:"
    ]
    for folder, files in project_structure.items():
        prefix = f"{folder}/" if folder else ""
        for file in files:
            helper_lines.append(f"{prefix}{file}:")
            helper_lines.append(f"  # Suggest what should be implemented here.")
            helper_lines.append("")
    return "\n".join(helper_lines)

def create_helper_file(
    project_type: str,
    root_path: str,
    features: List[str],
    description: str,
    helper_filename: str = "helper.txt"
) -> str:
    """
    Main entry point: generates helper file at project root.
    Returns the path to the helper file.
    """
    project_structure = get_project_structure(root_path)
    content = generate_helper_file_content(project_type, project_structure, features, description)
    helper_path = os.path.join(root_path, helper_filename)
    with open(helper_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"[✅] Helper file written: {helper_path}")
    return helper_path