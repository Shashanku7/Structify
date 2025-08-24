from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from pathlib import Path
from structify.core.parser import parse
from structify.core.generator import generate_project

st.set_page_config(page_title="Structify", page_icon="📦", layout="wide")

st.title("📦 Structify")
st.write("Generate project structures from natural language descriptions!")

def render_tree(base: Path, structure: dict):
    """
    Recursively render the project structure as a tree in Streamlit.

    Args:
        base (Path): The base path of the tree.
        structure (dict): The structure dictionary containing 'folders' and 'files'.
    """
    folders = structure.get("folders", [])
    files = structure.get("files", [])

    with st.expander(f"📂 {base.name}", expanded=True):
        # Render folders
        for folder in sorted(folders):
            folder_path = Path(folder)
            if "/" in folder:  # nested path
                top, rest = folder.split("/", 1)
                sub = {"folders": [rest], "files": []}
                render_tree(base / top, sub)
            else:
                st.markdown(f"📁 **{folder}**")

        # Render files
        for file in sorted(files):
            file_path = Path(file)
            if "/" in str(file_path):  # nested
                top, rest = str(file_path).split("/", 1)
                sub = {"folders": [], "files": [rest]}
                render_tree(base / top, sub)
            else:
                st.markdown(f"📄 {file}")

# --------------------------------
# Input widgets
# --------------------------------
description = st.text_area("Project Description", "", height=150)
output_dir = st.text_input("Output Directory", "generated_project")

# --------------------------------
# Live Preview
# --------------------------------
if description.strip():
    try:
        project_spec = parse(description)

        st.subheader("🔍 Project Preview")
        st.write(f"**Project Type:** {project_spec.get('project_type', 'generic')}")

        render_tree(Path("Project Root"), project_spec)

    except Exception as e:
        st.error(f"❌ Failed to parse description: {e}")

# --------------------------------
# Generate button
# --------------------------------
if st.button("Generate Project"):
    if not description.strip():
        st.warning("Please enter a project description.")
    else:
        try:
            base = Path(output_dir)
            base.mkdir(parents=True, exist_ok=True)

            project_spec = parse(description)
            generate_project(project_spec, str(base))

            st.success(f"✅ Project generated at: {base.resolve()}")
        except Exception as e:
            st.error(f"❌ Failed to generate project: {e}")