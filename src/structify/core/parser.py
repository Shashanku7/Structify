import os
import requests
import time
from typing import List, Tuple
from pathlib import Path

def get_gemini_api_keys() -> List[str]:
    """
    Get all available Gemini API keys from environment variables.
    Supports GOOGLE_GEMINI_API_KEY, GOOGLE_GEMINI_API_KEY_1, _2, _3, etc.
    """
    keys = []
    
    # Check for single key
    if os.getenv("GOOGLE_GEMINI_API_KEY"):
        keys.append(os.getenv("GOOGLE_GEMINI_API_KEY"))
    
    # Check for numbered keys (1-5)
    for i in range(1,6):
        key = os.getenv(f"GOOGLE_GEMINI_API_KEY_{i}")
        if key and key not in keys:  # Avoid duplicates
            keys.append(key)
    
    if not keys:
        raise ValueError("No GOOGLE_GEMINI_API_KEY found in environment")
    
    print(f"[🔑] Found {len(keys)} Gemini API key(s) available")
    return keys

def google_gemini_with_rotation(prompt: str, max_tokens: int = 4096, max_retries: int = 3) -> str:
    """
    Try multiple Gemini API keys with rotation.
    If one hits quota, automatically try the next one.
    """
    api_keys = get_gemini_api_keys()
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    for key_index, api_key in enumerate(api_keys):
        print(f"[🔑] Trying API key #{key_index + 1}/{len(api_keys)}")
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": api_key,
        }
        payload = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens
            }
        }
        
        for attempt in range(max_retries):
            try:
                print(f"[DEBUG] Sending request to Gemini API (Key #{key_index + 1}, Attempt {attempt + 1})...")
                response = requests.post(url, headers=headers, json=payload, timeout=120)
                print(f"[DEBUG] Gemini API HTTP status: {response.status_code}")
                
                data = response.json()
                
                # Handle errors
                if "error" in data:
                    error = data["error"]
                    print(f"[ERROR] Gemini API error (Key #{key_index + 1}):", error.get('message', 'Unknown'))
                    
                    # If quota exceeded, try next key
                    if error.get("code") == 429 or error.get("status") == "RESOURCE_EXHAUSTED":
                        print(f"[⚠️] Key #{key_index + 1} quota exceeded. Moving to next key...")
                        break  # Break retry loop, move to next key
                    
                    # Other errors, retry with same key
                    if attempt < max_retries - 1:
                        print(f"[WARN] Retrying with same key in 5 seconds...")
                        time.sleep(5)
                        continue
                    else:
                        break  # Move to next key
                
                # Success!
                result = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                print(f"[✅] Success with API key #{key_index + 1}")
                return result
                
            except Exception as e:
                print(f"[ERROR] Exception with key #{key_index + 1}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                else:
                    break  # Move to next key
    
    # All keys exhausted
    raise RuntimeError(f"All {len(api_keys)} Gemini API keys exhausted!")

def smart_ai_request(prompt: str, max_tokens: int = 4096) -> Tuple[str, str]:
    """Request with multi-key rotation."""
    print("[DEBUG] Using Gemini with key rotation...")
    try:
        content = google_gemini_with_rotation(prompt, max_tokens)
        return "google/gemini-2.5-flash-multi-key", content
    except Exception as e:
        print(f"[ERROR] All Gemini keys failed: {str(e)}")
        raise

def extract_parent_directories(files: List[str]) -> List[str]:
    """Extract all parent directories from file paths."""
    parent_dirs = set()
    for file_path in files:
        parts = Path(file_path).parts
        for i in range(len(parts) - 1):
            parent = str(Path(*parts[:i+1]))
            parent_dirs.add(parent)
    return sorted(list(parent_dirs))

def normalize_folder_path(folder: str) -> str:
    """Remove trailing slashes from folder names."""
    folder = folder.replace("\\", "/")
    return folder.rstrip('/\\')

def validate_and_fix_structure(folders: List[str], files: List[str]) -> Tuple[List[str], List[str]]:
    """Validate and fix the project structure to prevent conflicts."""
    print("[🔧] Validating and fixing project structure...")
    
    folders = [normalize_folder_path(f) for f in folders]
    implicit_parents = [ p.replace("\\", "/") for p in extract_parent_directories(files) ]
    print(f"[DEBUG] Found {len(implicit_parents)} implicit parent directories from files")
    
    all_folders = set(folders) | set(implicit_parents)
    files_set = set(files)
    conflicts = all_folders & files_set
    
    if conflicts:
        print(f"[WARN] Found {len(conflicts)} path conflicts - removing from files list:")
        for conflict in sorted(conflicts):
            print(f"   - {conflict} (appears in both folders and files)")
        files = [f for f in files if f not in conflicts]
    
    folders = sorted(list(all_folders))
    print(f"[✅] Structure validated: {len(folders)} folders, {len(files)} files")
    return folders, files

def parse(description: str):
    prompt = f"""
You are an AI project scaffolding assistant.
Given the following project description, output the full project structure intelligently.

Project Description: {description}

Instructions:
1. Provide Project Name on a single line: Project Name: <name>
2. Provide Project Type on a single line: Project Type: <type>
3. List Features (technologies, APIs, auth, DBs, etc.) with '- ' per feature
4. List Folders hierarchically with '- ' per folder, use '/' for nested folders
5. List Files with '- ' per file, use folder paths if needed (e.g., app/src/main.py)
6. Output in plain text exactly like this format:

Project Name: ...
Project Type: ...
Features:
- ...
- ...
Folders:
- folder1/
- folder2/subfolder/
Files:
- folder1/file1.ext
- folder2/subfolder/file2.ext

7. For EACH file, also provide a high level and detailed explanation of its purpose. (1 line per file)

Format helper explanations like this:

Helper:
- path/to/file.py :: Explanation of what belongs in this file
- path/to/other.py :: Explanation

CRITICAL: 1) The Helper section is MANDATORY. Provide explanations for ALL files.
          2) Keep the project structure minimal and practical,avoid creating excessive files or folders.
          3) Use common best practices without over-engineering.
          4) Generate the complete Files list BEFORE generating the Helper section.
IMPORTANT: When listing files in nested folders, ONLY list the file path (e.g., app/build.gradle), 
NOT the parent folder separately as a file. Parent folders will be created automatically.
"""
    print("[DEBUG] Parsing project description with AI...")
    try:
        used_model, text = smart_ai_request(prompt)
        print("[DEBUG] AI response received.")
        print("[DEBUG] Full AI response text:")
        print(text)
        print("[DEBUG] End of AI response")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        project_name = ""
        project_type = "generic"
        features: List[str] = []
        folders: List[str] = []
        files: List[str] = []
        helpers: dict[str, str] = {}
        section = None
        
        for line in lines:
            if line.lower().startswith("project name:"):
                project_name = line.split(":", 1)[1].strip()
                section = None
            elif line.lower().startswith("project type:"):
                project_type = line.split(":", 1)[1].strip()
                section = None
            elif line.lower() == "features:":
                section = "features"
            elif line.lower() == "folders:":
                section = "folders"
            elif line.lower() == "files:":
                section = "files"
            elif line.lower() == "helper:" or line.lower() == "helpers:":
                section = "helper"
                print(f"[DEBUG] Found Helper section!")
            elif line.startswith("-"):
                item = line[1:].strip()
                if section == "features":
                    features.append(item)
                elif section == "folders":
                    folders.append(item)
                elif section == "files":
                    files.append(item)
                elif section == "helper":
                    if "::" in item:
                        path, explanation = item.split("::", 1)
                        helpers[path.strip()] = explanation.strip()
                        print(f"[DEBUG] Added helper: {path.strip()}")
                    else:
                        print(f"[WARN] Helper line missing '::' separator: {item}")
        
        
        # fix:Validate and auto-fix the structure
        files = [f.replace("\\", "/") for f in files]
        folders = [f.replace("\\", "/") for f in folders]

        print(f"[DEBUG] Raw parse results: {len(folders)} folders, {len(files)} files")
        print(f"[DEBUG] Parsed {len(helpers)} helper entries")
        
        folders, files = validate_and_fix_structure(folders, files)
        
        if not folders:
            print("[WARN] No folders after validation, using fallback.")
            folders = ["src"]
        if not files:
            print("[WARN] No files after validation, using fallback.")
            files = ["README.md", "main.py"]

        result = {
            "project_name": project_name,
            "project_type": project_type,
            "features": features,
            "folders": folders,
            "files": files,
            "helpers": helpers,
            "used_model": used_model,
            "description": description
        }
        print("[DEBUG] Final parsed structure:", result)
        return result

    except Exception as e:
        print("[ERROR] All AI providers failed, using static fallback. Exception:", e)
        return {
            "project_name": "",
            "project_type": "generic",
            "features": [],
            "folders": ["src"],
            "files": ["README.md", "main.py"],
            "helpers": {},
            "used_model": "fallback-static",
            "description": description
        }

if __name__ == "__main__":
    description = "An Android e-commerce app with user authentication, shopping cart, and Firebase backend"
    structure = parse(description)
    for k, v in structure.items():
        print(f"{k}: {v}")