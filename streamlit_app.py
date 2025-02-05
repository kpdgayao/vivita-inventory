"""Entry point for Streamlit Share deployment."""
import os
import sys
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))
os.environ['PYTHONPATH'] = str(project_root)

# Import and run the main app
from app.main import main

if __name__ == "__main__":
    main()
