from dotenv import load_dotenv
load_dotenv()

import os
import requests
import time
from typing import List, Tuple

def google_gemini_2_5_flash_request(prompt: str, max_tokens: int = 4096, retries: int = 3) -> str:
    api_key = os.getenv("GOOGLE_GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_GEMINI_API_KEY is not set in environment variables or .env file")
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
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
    for attempt in range(retries):
        print(f"[DEBUG] Sending request to Gemini 2.5 Flash API... Attempt {attempt+1}")
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        print(f"[DEBUG] Gemini API HTTP status: {response.status_code}")
        try:
            data = response.json()
        except Exception as e:
            print("[ERROR] Could not decode Gemini response as JSON:", response.text)
            raise

        print("[DEBUG] Gemini API response:", data)
        # Handle API error response
        if "error" in data:
            error = data["error"]
            print("[ERROR] Gemini API error details:", error)
            # Handle quota/rate limit exceeded
            if error.get("code") == 429 or error.get("status") == "RESOURCE_EXHAUSTED":
                retry_delay = 10  # Default retry delay
                # Try to get retryDelay from details
                for detail in error.get("details", []):
                    if (
                        isinstance(detail, dict)
                        and detail.get("@type", "").endswith("RetryInfo")
                        and "retryDelay" in detail
                    ):
                        # retryDelay is like '10s'
                        retry_str = detail["retryDelay"]
                        try:
                            retry_delay = int(retry_str.rstrip("s"))
                        except Exception:
                            pass
                        break
                print(f"[WARN] Quota exceeded. Retrying after {retry_delay} seconds...")
                time.sleep(retry_delay)
                continue  # Retry
            # Any other error, raise
            raise RuntimeError(f"Gemini API error: {error.get('message', 'Unknown error')}")
        # Handle expected response
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError, TypeError) as e:
            print("[ERROR] Unexpected Gemini response format.")
            # If not a quota error, raise
            raise RuntimeError(f"Unexpected Gemini API response format: {data}") from e

    # If we exhausted retries, fallback
    raise RuntimeError("Gemini API quota exceeded - retries exhausted.")

def smart_ai_request(prompt: str, max_tokens: int = 4096) -> Tuple[str, str]:
    print("[DEBUG] Trying Google Gemini 2.5 Flash API...")
    try:
        content = google_gemini_2_5_flash_request(prompt, max_tokens)
        print("[DEBUG] Google Gemini 2.5 Flash succeeded.")
        return "google/gemini-2.5-flash", content
    except Exception as e:
        print(f"[ERROR] Gemini AI failed after retries. {str(e)}")
        raise

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
5. List Files with '- ' per file, use folder paths if needed
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
"""
    print("[DEBUG] Parsing project description with AI...")
    try:
        used_model, text = smart_ai_request(prompt)
        print("[DEBUG] AI response received.")
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        project_name = ""
        project_type = "generic"
        features: List[str] = []
        folders: List[str] = []
        files: List[str] = []

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
            elif line.startswith("-"):
                item = line[1:].strip()
                if section == "features":
                    features.append(item)
                elif section == "folders":
                    folders.append(item)
                elif section == "files":
                    files.append(item)

        if not folders:
            print("[WARN] No folders parsed from AI output, using fallback.")
            folders = ["src"]
        if not files:
            print("[WARN] No files parsed from AI output, using fallback.")
            files = ["README.md", "main.py"]

        result = {
            "project_name": project_name,
            "project_type": project_type,
            "features": features,
            "folders": folders,
            "files": files,
            "used_model": used_model,
            "description": description
        }
        print("[DEBUG] Parsed structure:", result)
        return result

    except Exception as e:
        print("[ERROR] Gemini AI failed, using static fallback. Exception:", e)
        return {
            "project_name": "",
            "project_type": "generic",
            "features": [],
            "folders": ["src"],
            "files": ["README.md", "main.py"],
            "used_model": "fallback-static",
            "description": description
        }

if __name__ == "__main__":
    description = "An Android e-commerce app with user authentication, shopping cart, and Firebase backend"
    structure = parse(description)
    for k, v in structure.items():
        print(f"{k}: {v}")