"""Entry point for the Vivita Inventory Management System."""
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

os.environ['PYTHONPATH'] = str(project_root)

# Run the Streamlit app
if __name__ == "__main__":
    import streamlit.web.cli as stcli
    sys.argv = ["streamlit", "run", str(project_root / "main.py"), "--logger.level=debug"]
    sys.exit(stcli.main())
