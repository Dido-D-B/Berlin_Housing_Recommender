# Imports
import os
import sys
import pathlib
import streamlit as st

# Ensure the *repository root* (the parent of the `app/` folder) is on sys.path so `import app...` works
REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]  # .../Berlin_Housing_Affordability
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app.utils.content import build_corpus, retrieve, synthesize_answer, citation_line

# Page Configurations
DOCS_DIR = os.environ.get('EXPLAIN_DOCS_DIR')
if not DOCS_DIR or not os.path.isdir(DOCS_DIR):
    # Default to the repo-level ./docs folder
    DOCS_DIR = os.path.join(str(REPO_ROOT), 'docs')

st.set_page_config(
    page_title="Berlin Housing - Q&A",
    page_icon="💬",
    layout="wide")    

# UI
st.markdown(
    """
    <div style='border: 3px solid #A50034; background-color: #A50034; padding: 15px; text-align: center; border-radius: 6px;'>
        <h1 style='color: white; margin: 0;'>Project Assistant - Q&A</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.divider()
st.markdown("""**Ask your questions!** - The project assistant can answer (most of) your questions about this project and the web. Type a question in the chat box below.""")
st.caption("Ask in natural language; multiple phrasings work. For definitions, start with “What is …” (e.g. What is Mietspiegel?).")
st.divider()

with st.expander("About this assistant", expanded=False):
    st.markdown(
        "- **Purpose:** This assistant helps you navigate and understand the Berlin Housing Affordability project.  \n"
        "- **Scope:** It can explain glossary terms, methods, preprocessing, cultural facts, images, dashboards, and recommendations documented in your `./docs`.  \n"
        "- **Sources:** Answers are built only from local project files (`faq.md`, `glossary.md`, `methodology.md`, etc.).  \n"
        "- **Limitations:** If something isn’t documented, the assistant will tell you. Add it to the docs and it becomes available automatically.  \n"
    )

chunks, vectorizer, X = build_corpus(DOCS_DIR)

if not chunks:
    st.warning("No documents found in `./docs`.")
else:
    st.success(f"Loaded {len(chunks)} knowledge chunks from {len(set([c['path'] for c in chunks]))} files.")

user_q = st.chat_input("Ask questions about this project (e.g., 'What is Mietspiegel?')")
if "history" not in st.session_state:
    st.session_state.history = []

if user_q:
    with st.spinner("Thinking..."):
        hits = retrieve(user_q, chunks, vectorizer, X, top_k=5)
        answer = synthesize_answer(user_q, hits)
        cites = citation_line(hits)
    st.session_state.history.append(("user", user_q))
    st.session_state.history.append(("assistant", answer, cites))

for entry in st.session_state.history:
    role = entry[0]
    if role == "user":
        with st.chat_message("user"):
            st.write(entry[1])
    else:
        with st.chat_message("assistant"):
            st.write(entry[1])
            if entry[2]:
                with st.expander("Sources"):
                    st.caption(entry[2])

st.divider()
