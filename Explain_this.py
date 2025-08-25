import os
import re
import glob
import uuid
import pathlib
from typing import List, Dict, Tuple
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import string

def normalize_text(s: str) -> str:
    s = s.lower()
    return s.translate(str.maketrans('', '', string.punctuation)).strip()

def is_definition_query(q: str) -> Tuple[bool, str]:
    q_norm = normalize_text(q)
    patterns = [
        r"^what is (.+)$",
        r"^define (.+)$",
        r"^meaning of (.+)$"
    ]
    for pat in patterns:
        m = re.match(pat, q_norm)
        if m:
            term = m.group(1).strip()
            return True, term
    return False, ""

import textwrap

def _clean_markdown(s: str) -> str:
    # remove markdown headings and collapse extra whitespace
    s = re.sub(r"^#{1,6}\s+.*$", "", s, flags=re.MULTILINE)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def _as_bullets(text: str, max_bullets: int = 4) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if not sentences:
        return text
    lead = sentences[0].strip()
    bullets = [f"- {s.strip()}" for s in sentences[1:1+max_bullets] if s.strip()]
    if bullets:
        return lead + "\n\n" + "\n".join(bullets)
    return lead

# Config
DOCS_DIR = os.environ.get('EXPLAIN_DOCS_DIR')
if not DOCS_DIR or not os.path.isdir(DOCS_DIR):
    DOCS_DIR = os.path.join(os.path.dirname(__file__), 'docs')

st.set_page_config(page_title="Berlin Housing - Q&A", page_icon="💬", layout="wide")

# Utilities
def read_docs(docs_dir: str) -> List[Tuple[str, str]]:
    """Return list of (path, text) for .md and .txt files in docs_dir."""
    paths = glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True) +             glob.glob(os.path.join(docs_dir, "**/*.txt"), recursive=True)
    results = []
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                results.append((p, f.read()))
        except Exception as e:
            st.warning(f"Could not read {p}: {e}")
    return results

def extract_glossary_entries(glossary_path: str) -> List[Dict]:
    entries = []
    if not os.path.isfile(glossary_path):
        return entries
    try:
        with open(glossary_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        st.warning(f"Could not read glossary file {glossary_path}: {e}")
        return entries
    pattern = re.compile(r"^\*\*(.+?)\*\*\s*[:—]\s*(.+)")
    for line in lines:
        m = pattern.match(line.strip())
        if m:
            term = m.group(1).strip()
            definition = m.group(2).strip()
            entries.append({
                "id": str(uuid.uuid4()),
                "path": glossary_path,
                "title": term,
                "content": definition,
                "source": "glossary"
            })
    return entries

def split_into_chunks(path: str, text: str, max_chars: int = 1200) -> List[Dict]:
    """
    Chunk by headings and paragraphs; ensure chunks are not too long.
    Returns list of dicts with: id, path, title, content.
    Special case: faq.md is split into individual Q&A chunks per `###` question.
    """
    base = os.path.basename(path).lower()
    chunks: List[Dict] = []

    # Special case for FAQ: split into single Q/A items
    if base == "faq.md":
        # Split each FAQ item by "###"
        parts = re.split(r"\n(?=### )", text)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            # Ensure the part starts with a "###" question
            m = re.match(r"^###\s+(.+?)(?:\s*[:\-–—]\s*(.*))?$", part.splitlines()[0])
            if not m:
                continue
            raw_title = m.group(1).strip()
            inline_answer = (m.group(2) or "").strip()

            # Extract body lines robustly: everything after the first header line,
            # skipping leading blank lines. This avoids accidental removal by markdown cleaning.
            lines = part.splitlines()
            body_lines = []
            # Skip the first line (the "### ..." header)
            for ln in lines[1:]:
                if not body_lines and not ln.strip():
                    # still skipping leading blanks
                    continue
                body_lines.append(ln)
            content = "\n".join(body_lines).strip()

            if inline_answer:
                if content:
                    content = inline_answer + "\n\n" + content
                else:
                    content = inline_answer

            # Clean and truncate
            content = _clean_markdown(content)
            if len(content) > max_chars:
                content = content[:max_chars] + "..."

            if not content:
                # If for some reason the body was empty, keep a placeholder so the user knows to fill it.
                content = "_This FAQ question exists but its answer content is empty. Please add text under the heading in `faq.md`._"

            # Split alternative phrasings separated by slashes into individual titles
            alt_titles = [t.strip() for t in re.split(r"\s*/\s*", raw_title) if t.strip()]
            for t in alt_titles:
                chunks.append({
                    "id": str(uuid.uuid4()),
                    "path": path,
                    "title": t,
                    "content": content
                })
        return chunks

    # Default behavior for other docs
    sections = re.split(r"\n(?=# )", text)
    for sec in sections:
        if not sec.strip():
            continue
        m = re.match(r"^#\s+(.+)", sec.strip())
        title = m.group(1).strip() if m else pathlib.Path(path).name
        parts = re.split(r"\n(?=## )", sec)
        for part in parts:
            content = part.strip()
            if not content:
                continue
            if len(content) > max_chars:
                paras = re.split(r"\n\s*\n", content)
                buf = ""
                for para in paras:
                    if len(buf) + len(para) + 2 <= max_chars:
                        buf += (("\n\n" if buf else "") + para)
                    else:
                        chunks.append({"id": str(uuid.uuid4()), "path": path, "title": title, "content": buf.strip()})
                        buf = para
                if buf.strip():
                    chunks.append({"id": str(uuid.uuid4()), "path": path, "title": title, "content": buf.strip()})
            else:
                chunks.append({"id": str(uuid.uuid4()), "path": path, "title": title, "content": content})
    return chunks

@st.cache_data(show_spinner=False)
def build_corpus(docs_dir: str):
    docs = read_docs(docs_dir)
    all_chunks = []
    for p, t in docs:
        all_chunks.extend(split_into_chunks(p, t, max_chars=1200))
    glossary_entries = extract_glossary_entries(os.path.join(docs_dir, 'glossary.md'))
    all_chunks.extend(glossary_entries)
    if not all_chunks:
        return [], None, None

    texts = [c["content"] for c in all_chunks]
    vectorizer = TfidfVectorizer(
        strip_accents="unicode",
        ngram_range=(1,2),
        max_df=0.9,
        min_df=1
    )
    X = vectorizer.fit_transform(texts)
    return all_chunks, vectorizer, X

def retrieve(query: str, chunks: List[Dict], vectorizer, X, top_k: int = 5) -> List[Dict]:
    is_def, term = is_definition_query(query)
    if is_def:
        term_norm = normalize_text(term)
        # 1) Exact glossary title match
        for c in chunks:
            if c.get("source") == "glossary" and normalize_text(c.get("title","")) == term_norm:
                return [c]
        # 2) Containment match (handles titles with parentheses, e.g., "Cold Rent (Kaltmiete)")
        for c in chunks:
            if c.get("source") == "glossary":
                t_norm = normalize_text(c.get("title",""))
                if term_norm in t_norm or t_norm in term_norm:
                    return [c]
        # 3) Token-overlap match (robust to minor phrasing differences)
        q_tokens = set(term_norm.split())
        best_g = None
        best_overlap = 0.0
        for c in chunks:
            if c.get("source") != "glossary":
                continue
            t_norm = normalize_text(c.get("title",""))
            if not t_norm:
                continue
            t_tokens = set(t_norm.split())
            if not t_tokens:
                continue
            overlap = len(q_tokens & t_tokens) / max(1, len(q_tokens | t_tokens))
            if overlap > best_overlap:
                best_overlap = overlap
                best_g = c
        if best_g and best_overlap >= 0.5:
            return [best_g]

    # NEW: exact and fuzzy FAQ matching
    q_norm = normalize_text(query)
    # 1) Exact title match against FAQ entries
    for c in chunks:
        if str(c.get("path","" )).endswith("faq.md") and normalize_text(c.get("title","")) == q_norm:
            return [c]
    # 2) Fuzzy containment: title inside query OR query inside title
    for c in chunks:
        if str(c.get("path","" )).endswith("faq.md"):
            t_norm = normalize_text(c.get("title",""))
            if t_norm and (t_norm in q_norm or q_norm in t_norm):
                return [c]

    # 2b) Token-overlap fuzzy match (helps with paraphrases)
    q_tokens = set(q_norm.split())
    best_faq = None
    best_overlap = 0.0
    for c in chunks:
        if str(c.get("path","")).endswith("faq.md"):
            t_norm = normalize_text(c.get("title",""))
            if not t_norm:
                continue
            t_tokens = set(t_norm.split())
            if not t_tokens:
                continue
            overlap = len(q_tokens & t_tokens) / max(1, len(q_tokens | t_tokens))
            if overlap > best_overlap:
                best_overlap = overlap
                best_faq = c
    # If there is strong token overlap, return that FAQ chunk
    if best_faq and best_overlap >= 0.5:
        return [best_faq]

    # Fall back to TF‑IDF ranking
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, X)[0]
    # boost for glossary and filename matches
    faq_keywords = {"goal", "purpose", "exist", "why", "about", "what is this"}
    is_faq_like = any(k in q_norm for k in faq_keywords)
    for i, c in enumerate(chunks):
        boost = 0.0
        path_str = c.get("path", "")
        if c.get("source") == "glossary" or path_str.endswith("glossary.md"):
            boost += 0.2
        title_norm = c.get("title", "").lower()
        if term and normalize_text(term) in normalize_text(title_norm):
            boost += 0.1
        # Stronger nudge for FAQ when the query looks like a purpose/goal/why question
        if path_str.endswith("faq.md") and is_faq_like:
            boost += 0.5
        sims[i] += boost
    top_idx = sims.argsort()[::-1][:top_k]
    results = []
    for i in top_idx:
        c = chunks[i].copy()
        c["score"] = float(sims[i])
        results.append(c)
    return results

def synthesize_answer(query: str, hits: List[Dict]) -> str:
    """
    Build a concise answer from the most relevant chunks. For glossary items, 
    return the definition; otherwise, format as lead sentence + bullets.
    """
    if not hits:
        return "I couldn't find this in the project documentation yet. If it's important, we should add it to the Methodology or Glossary."

    top_hit = hits[0]
    if top_hit.get("source") == "glossary":
        sentences = re.split(r"(?<=[.!?])\s+", top_hit["content"].strip())
        concise = " ".join(sentences[:2]).strip()
        concise = _clean_markdown(concise)
        words = concise.split()
        if len(words) > 80:
            concise = " ".join(words[:80]) + "..."
        return concise + "\n\n*This definition is from the project glossary.*"

    # Stitch a few top chunks, then clean and bulletize
    snippets = []
    used = 0
    total_words = 0
    max_words = 150
    for h in hits:
        sentences = re.split(r"(?<=[.!?])\s+", h["content"].strip())
        for sent in sentences:
            if not sent.strip():
                continue
            sent_words = sent.split()
            if total_words + len(sent_words) > max_words:
                remaining = max_words - total_words
                if remaining > 0:
                    snippets.append(" ".join(sent_words[:remaining]) + "...")
                break
            snippets.append(sent.strip())
            total_words += len(sent_words)
        used += 1
        if used >= 3 or total_words >= max_words:
            break

    answer = " ".join(snippets) if snippets else hits[0]["content"][:600]
    answer = _clean_markdown(answer)
    answer = _as_bullets(answer, max_bullets=4)
    answer += "\n\n*If anything is unclear or seems missing, it may not be documented yet. I only answer from the local project docs.*"
    return answer

def citation_line(hits: List[Dict]) -> str:
    if not hits:
        return ""
    items = []
    for h in hits[:3]:  # cite top 3
        fname = os.path.basename(h["path"])
        title = h.get("title") or fname
        items.append(f"**{title}** ({fname})")
    return "Sources: " + "; ".join(items)

# ----------------------
# UI
# ----------------------
st.markdown(
    """
    <div style='border: 3px solid #A50034; background-color: #A50034; padding: 15px; text-align: center; border-radius: 6px;'>
        <h1 style='color: white; margin: 0;'>Project Assistant - Q&A</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)

st.markdown(
    """
    Ask your questions about the **Berlin Housing Affordability Project** and web app here!  
    
    Type a question in the chat box below - Ask in natural language; multiple phrasings work.
    For definitions, start with **“What is …”** (e.g., *What is Mietspiegel?*).
    """
)

st.markdown("<div style='margin-bottom:40px;'></div>", unsafe_allow_html=True)

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
