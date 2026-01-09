import tempfile
from pathlib import Path
from structify.core.generator import generate_project

def test_generate_project_creates_files():
    """
    Test that generate_project creates the specified files and folders.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        generate_project(
            {
                "project_type": "generic",
                "folders": ["src"],
                "files": ["main.py"]
            },
            tmpdir
        )

        # Generator creates ONE timestamped project directory
        project_dirs = list(Path(tmpdir).iterdir())
        assert len(project_dirs) == 1

        project_root = project_dirs[0]

        assert (project_root / "src").exists()
        assert (project_root / "main.py").exists()
        assert (project_root / "helper.txt").exists()