import sys
from structify import generate_project

def test_cli_simulation(monkeypatch, tmp_path):
    """
    Test that generate_project runs without error for a simple Flask app description.
    This simulates CLI usage by patching sys.argv and uses a temporary directory.
    """
    monkeypatch.setattr(sys, "argv", ["structify", "Flask app"])
    outdir = tmp_path / "tmp_project"
    generate_project("Flask app", str(outdir))
    # Optionally check that the directory was created
    assert outdir.exists()