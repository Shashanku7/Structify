import tempfile
from pathlib import Path
from structify.core.generator import generate_project

def test_generate_project_creates_files():
    """
    Test that generate_project creates the specified files and folders.
    """
    desc = "Generic Python project"
    with tempfile.TemporaryDirectory() as tmpdir:
        generate_project(
            {
                "project_type": "generic",
                "folders": ["src"],
                "files": ["main.py"]
            },
            tmpdir
        )
        assert Path(tmpdir, "main.py").exists()
        assert Path(tmpdir, "src").exists()