# 📦 Structify

**Beginner-friendly Python tool to generate clean project structures from natural language descriptions.**

Structify lets you create a ready-to-start codebase layout—just by describing your project in plain English. It uses AI to interpret your intent and generates folders, files, and a comprehensive `helper.txt` file with implementation suggestions and docstrings for each part of your codebase.

---

## 🚀 Features

- **Natural Language to Structure**: Describe your project in English (e.g. `"Flask app with PostgreSQL and Docker"`) and Structify builds the skeleton.
- **AI-powered Guidance**: A single `helper.txt` is generated with docstring-style suggestions and example snippets for every file and folder.
- **Supports Modern Stacks**: Works for Python, JS, web, data, ML, and more.
- **CLI, Python API, and Web UI**: Use Structify from the terminal, as a library, or via the included Streamlit app.
- **Zero config**: No YAML or boilerplate files to define structure up front.

---

## ⚡️ Quickstart

### 1. Create and Activate a Virtual Environment (Recommended)

It's best practice to isolate your Python dependencies in a virtual environment:

**On macOS/Linux:**
```sh
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```sh
python -m venv .venv
.venv\Scripts\activate
```

### 2. Install dependencies

```sh
pip install -r requirements.txt
# For development:
pip install -r requirements-dev.txt
```

> **Important:**  
> If you plan to use Structify as a CLI, Python module, or with Streamlit, and your folder structure includes `src/structify`,  
> **you must install Structify in editable mode** from your project root before running commands or launching the app:
>
> ```sh
> pip install -e .
> ```
>
> This ensures that imports like `from structify.core.parser import parse` work correctly, and avoids `ModuleNotFoundError`.  
> (You only need to do this once per environment.)

### 2.1. Configure your `.env` file

Structify uses a `.env` file at the project root for secrets and configuration (loaded with `python-dotenv`).

**Example `.env` format:**
```
GOOGLE_GEMINI_API_KEY=api-key-here
```
Replace `api-key-here` with your actual Gemini API key.

You can obtain a Gemini API key from the official Google AI Studio:  
https://aistudio.google.com/app/apikey

### 3. As a Python Library

```python
from structify import generate_project

generate_project("Flask app with PostgreSQL and Docker")
```

### 4. As a Command-Line Tool

```sh
python -m structify "Flask app with PostgreSQL and Docker"
# Optionally specify output directory:
python -m structify "FastAPI backend + React frontend" my_project
```

### 5. As a Web App

```sh
streamlit run src/structify/app.py
```
- Visit [http://localhost:8501](http://localhost:8501), enter your project description, and get the structure!

---

## 📝 What gets generated?

- **Folders & files**: Clean, AI-inferred project skeleton based on your description.
- **`helper.txt`**: At the project root, with docstring-style implementation notes and code snippets for every file/folder (no actual code, just guidance!).
- **No boilerplate code**: Only empty files & folders, plus the helper file.

---

## 🛠 Example

**Input:**
```sh
python -m structify "Flask app with user registration, PostgreSQL, Docker"
```

**Output:**
```
/generated_project/Flask_app_with_user_registration_20250824153613/
    ├── app/
    │   ├── __init__.py
    │   ├── models.py
    │   ├── routes.py
    ├── requirements.txt
    ├── Dockerfile
    ├── helper.txt   # ← AI-generated docstring and code guidance!
    └── ...
```

Open `helper.txt` for guidance on what to put in each file.

---

## 🧑‍💻 Why use Structify?

- **For beginners**: No more “what files go where?” confusion—just describe your app and learn from the suggestions.
- **For pros**: Rapidly bootstrap new projects, or use as a teaching aid.
- **Consistent, modern, and flexible**: Supports web, data, ML, backend, and more.

---

## 🧩 Configuration

- Structify uses `.env` for any API keys or configuration (load with `python-dotenv`).
- Default project structure fallbacks are in YAML (see `config.yaml`), but AI is used by default.

---

## 📝 Development

- Code: See the `src/structify` directory.
- Test: `pytest`
- Format: `black`, `isort`

---

## ⚠️ Troubleshooting: ModuleNotFoundError

If you see an error like:
```
ModuleNotFoundError: No module named 'structify.core'
```
or similar import errors when running:
```sh
streamlit run src/structify/app.py
# or
python -m structify ...
```
**This means Python can't find your package because it hasn't been installed in editable mode.**

**Solution:**  
From your project root directory, run:
```sh
pip install -e .
```
Then try your command again.  
This will make sure `streamlit run src/structify/app.py` works and finds all your modules.

---

## 📜 License

MIT

---

## 👨🏼‍💻 Author

Shashank U

---

## 🤖 How does it work?

- Parses your description using AI (e.g., Gemini, OpenRouter, etc).
- Recursively builds the project skeleton.
- Calls AI again to generate a single, detailed `helper.txt` at the root, with docstring-style instructions and code snippets for each file/folder.

No code is implemented for you—just the structure and expert guidance!

---

Enjoy structuring your projects the smart way! 🚀