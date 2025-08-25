import os
import streamlit as st

# Make sure the helper can find your docs no matter where you launch the app
os.environ.setdefault("EXPLAIN_DOCS_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "docs"))

# Option A: import your existing app as a module if you refactor
# from utils.explain import run_explain_app
# run_explain_app()

# Option B: just exec your existing Explain_this.py
import runpy, pathlib
SCRIPT = pathlib.Path(__file__).parents[2] / "Explain_this.py"
runpy.run_path(str(SCRIPT), run_name="__main__")