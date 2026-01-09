import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import tempfile
import zipfile
from io import BytesIO
from pathlib import Path

from structify.core.parser import parse
from structify.core.generator import generate_project


# --------------------------------
# Page config
# --------------------------------
st.set_page_config(
    page_title="Structify",
    page_icon="📦",
    layout="wide"
)

st.title("📦 Structify")
st.caption("Describe your project. Get a clean folder structure. Download as ZIP.")


# --------------------------------
# Styling (tree background)
# --------------------------------
st.markdown(
    """
    <style>
    .stCodeBlock {
        background-color: #0f172a;
        border-radius: 8px;
        font-size: 14px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------
# Session state
# --------------------------------
if "project_spec" not in st.session_state:
    st.session_state.project_spec = None
if "last_description" not in st.session_state:
    st.session_state.last_description = ""
if "last_project_name" not in st.session_state:
    st.session_state.last_project_name = ""


# --------------------------------
# Helpers
# --------------------------------
def build_tree_text(root_name: str, folders: list[str], files: list[str]) -> str:
    lines = ["Directory structure:", f"└── {root_name}/"]

    items = sorted(
        [(f, "dir") for f in folders] +
        [(f, "file") for f in files]
    )

    for i, (name, kind) in enumerate(items):
        connector = "└── " if i == len(items) - 1 else "├── "
        suffix = "/" if kind == "dir" else ""
        lines.append(f"    {connector}{name}{suffix}")

    return "\n".join(lines)


# --------------------------------
# Inputs
# --------------------------------
project_name = st.text_input(
    "Project root folder name",
    placeholder="e.g. campus-event-backend",
)

description = st.text_area(
    "Project description",
    placeholder="Describe what you want to build...",
    height=260
)

# Reset cache if inputs change
if (
    description.strip() != st.session_state.last_description
    or project_name.strip() != st.session_state.last_project_name
):
    st.session_state.project_spec = None
    st.session_state.last_description = description.strip()
    st.session_state.last_project_name = project_name.strip()


# --------------------------------
# Preview
# --------------------------------
if description.strip():
    try:
        if st.session_state.project_spec is None:
            # Use stage-based status widget for honest progress tracking
            # This shows actual stages instead of fake percentages
            status = st.status("🧠 Analyzing project description...", expanded=True)
            
            # Stage 1: AI Analysis (slowest part, unpredictable timing)
            status.write("⏱️ Waiting for AI response (this may take 10-30 seconds)...")
            st.session_state.project_spec = parse(description)
            
            # Mark as complete once AI responds
            status.update(label="✅ Analysis complete!", state="complete")

        spec = st.session_state.project_spec

        st.subheader("🔍 Preview")
        st.write(f"**Project type:** {spec.get('project_type', 'generic')}")

        tree_text = build_tree_text(
            root_name=project_name or "project",
            folders=spec.get("folders", []),
            files=spec.get("files", [])
        )

        st.code(tree_text, language="text")

    except Exception as e:
        st.error(f"Parse failed: {e}")


# --------------------------------
# Generate ZIP
# --------------------------------
st.divider()

if st.button("🚀 Generate ZIP"):
    if not description.strip():
        st.warning("Project description cannot be empty.")
    elif not project_name.strip():
        st.warning("Please provide a project root name.")
    elif st.session_state.project_spec is None:
        st.error("No project spec available.")
    else:
        try:
            # Use stage-based status tracking for honest progress feedback
            # Each stage updates only after actual completion
            status = st.status("Generating project...", expanded=True)

            with tempfile.TemporaryDirectory() as tmpdir:
                # Stage 1: File system operations (fast, predictable)
                status.write("📁 Creating folder structure and files...")
                out = Path(tmpdir) / project_name
                generate_project(st.session_state.project_spec, str(out))

                # Stage 2: ZIP compression (fast, predictable)
                status.write("📦 Packaging into ZIP archive...")
                buf = BytesIO()
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zipf:
                    for f in out.rglob("*"):
                        zipf.write(f, f.relative_to(out))
                buf.seek(0)

            # Mark entire process as complete
            status.update(label="✅ Project generated successfully!", state="complete")

            st.success("Your project scaffold is ready for download!")
            st.download_button(
                "⬇️ Download ZIP",
                buf,
                file_name=f"{project_name}.zip",
                mime="application/zip"
            )

        except Exception as e:
            st.error(f"Generation failed: {e}")