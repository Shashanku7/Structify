"""
Structify: A beginner-friendly Python tool to generate clean project structures
from natural language descriptions.

Usage:

1. As a library:
   >>> from structify import generate_project
   >>> generate_project("Flask app with PostgreSQL and Docker")

2. As a command-line tool:
   $ python -m structify "Flask app with PostgreSQL and Docker"
"""

from dotenv import load_dotenv
load_dotenv()
import sys
from pathlib import Path
from .core.parser import parse
from .core.generator import generate_project as _generate_project

def generate_project(description: str, output_dir: str = "generated_project") -> None:
    """
    Generate a project structure based on the given description.

    Args:
        description (str): Natural language description of the project.
        output_dir (str): Directory where the project will be created.

    Example:
        >>> generate_project("Flask app with PostgreSQL", "my_flask_app")
    """
    base = Path(output_dir)
    base.mkdir(parents=True, exist_ok=True)

    # 1. Parse description into a structured definition (OpenRouter-powered parsing)
    project_spec = parse(description)

    # 2. Generate project scaffold from the parsed spec
    _generate_project(project_spec, str(base))

    print(f"[✅] Project generated at: {base.resolve()}")

def _main():
    """
    Allow Structify to run directly from the command line.

    Example:
        $ python -m structify "Flask app with PostgreSQL"
    """
    if len(sys.argv) < 2:
        print('Usage: python -m structify "<project description>" [output_dir]')
        sys.exit(1)

    description = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "generated_project"

    generate_project(description, output_dir)

# Run CLI only if executed directly
if __name__ == "__main__":
    _main()