import os
import streamlit as st

# Make sure the helper can find the docs folder 
os.environ.setdefault("EXPLAIN_DOCS_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "docs"))

# Execute Explain_this.py
import runpy, pathlib
SCRIPT = pathlib.Path(__file__).parents[2] / "Explain_this.py"
runpy.run_path(str(SCRIPT), run_name="__main__")