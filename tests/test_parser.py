import pytest
from structify.core.parser import parse

def test_parse_generic():
    """
    Test that parse returns expected keys for a generic Python project description.
    """
    desc = "A generic Python project"
    result = parse(desc, use_gemini=False)
    assert "folders" in result
    assert "files" in result