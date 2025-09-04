"""
content.py

Utilities for the Q&A/Explain page and content lookups used across the app.

This module:
- Loads project documentation (FAQ, glossary, methods) from `docs/`
- Builds a TF–IDF searchable corpus of chunks
- Retrieves the most relevant chunks for a user query and synthesizes a concise answer
- Looks up district/subdistrict cultural blurbs and image credits
"""

# Imports
import os
import re
import glob
import uuid
import pathlib
import streamlit as st
from typing import List, Dict, Tuple
from typing import Dict, Tuple, Any
from utils.data import load_json as _load_json
from utils.text import norm as _norm, district_slug  # district_slug kept for future use

# Data paths
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_DATA_DIR = os.path.join(_BASE_DIR, "data")

DISTRICTS_JSON_PATH = os.environ.get(
    "DISTRICTS_JSON_PATH",
    os.path.join(_DATA_DIR, "districts_cultural_facts.json"),
)

SUBDISTRICTS_JSON_PATH = os.environ.get(
    "SUBDISTRICTS_JSON_PATH",
    os.path.join(_DATA_DIR, "subdistricts_cultural_facts.json"),
)

# Path for image credits JSON
IMAGE_CREDITS_PATH = os.environ.get(
    "IMAGE_CREDITS_PATH",
    os.path.join(_DATA_DIR, "image_credits.json"),
)

_DISTRICT_INDEX: Dict[str, Any] = {}
_SUBDISTRICT_INDEX: Dict[Tuple[str, str], Any] = {}

# Load district and subdistrict cultural facts JSON (either dict or list formats).
_district_facts_raw = _load_json(DISTRICTS_JSON_PATH) or {}
_subdistrict_facts_raw = _load_json(SUBDISTRICTS_JSON_PATH) or {}

# District facts can be a dict {"bezirk": {...}} or a list of dicts with a name key
if isinstance(_district_facts_raw, dict):
    _DISTRICT_INDEX = { _norm(k): v for k, v in _district_facts_raw.items() }
elif isinstance(_district_facts_raw, list):
    for v in _district_facts_raw:
        if not isinstance(v, dict):
            continue
        # try common keys: name/bezirk/title
        name = v.get("name") or v.get("bezirk") or v.get("title") or ""
        if name:
            _DISTRICT_INDEX[_norm(name)] = v

# Subdistrict facts may be dict or list
if isinstance(_subdistrict_facts_raw, dict):
    _iterable = _subdistrict_facts_raw.values()
elif isinstance(_subdistrict_facts_raw, list):
    _iterable = _subdistrict_facts_raw
else:
    _iterable = []

for v in _iterable:
    if not isinstance(v, dict):
        continue
    b = v.get("bezirk") or v.get("district") or ""
    o = v.get("ortsteil") or v.get("subdistrict") or v.get("locality") or ""
    key = (_norm(b), _norm(o))
    if key != ("", ""):
        _SUBDISTRICT_INDEX[key] = v

# Load image credits JSON: maps district slug → list of credit strings.
_IMAGE_CREDITS = _load_json(IMAGE_CREDITS_PATH) or {}

# Public API
def get_district_blurb(bezirk: str) -> dict:
    """
    Get the cultural blurb for a district.

    Args:
        bezirk (str): District name.

    Returns:
        dict: Dict with optional keys {blurb, image_path, source}; empty dict if not found.
    """
    if not bezirk:
        return {}
    return _DISTRICT_INDEX.get(_norm(bezirk), {})

# Lookup subdistrict blurb by normalized district + subdistrict name.
def get_subdistrict_blurb(bezirk: str, ortsteil: str) -> dict:
    """
    Get the cultural blurb for a (district, subdistrict) pair.

    Args:
        bezirk (str): District name.
        ortsteil (str): Subdistrict name.

    Returns:
        dict: Dict with optional keys {blurb, image_path, source, bezirk, ortsteil}; empty if not found.
    """
    if not bezirk or not ortsteil:
        return {}
    return _SUBDISTRICT_INDEX.get((_norm(bezirk), _norm(ortsteil)), {})

# Image credits API
def get_image_credit(bezirk: str, idx: int) -> str:
    """
    Return the credit line for a district image by index.

    Args:
        bezirk (str): District name.
        idx (int): Zero-based image index.

    Returns:
        str: Credit text, or empty string if missing.
    """
    if not bezirk or idx is None or idx < 0:
        return ""
    try:
        slug = district_slug(bezirk)
        credits = _IMAGE_CREDITS.get(slug, [])
        if isinstance(credits, list) and 0 <= idx < len(credits):
            val = credits[idx]
            return val if isinstance(val, str) else ""
    except Exception:
        pass
    return ""

###################

# ---------- file reading / parsing ----------
def read_docs(docs_dir: str) -> List[Tuple[str, str]]:
    """
    Read all `.md` and `.txt` files under a docs directory.

    Args:
        docs_dir (str): Root directory of documentation.

    Returns:
        list[tuple[str,str]]: List of (path, text) pairs.
    """
    paths = glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True) + \
            glob.glob(os.path.join(docs_dir, "**/*.txt"), recursive=True)
    results: List[Tuple[str, str]] = []
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                results.append((p, f.read()))
        except Exception as e:
            if st:
                st.warning(f"Could not read {p}: {e}")
    return results

def extract_glossary_entries(glossary_path: str) -> List[Dict]:
    """
    Parse `**Term**: Definition` lines from `glossary.md` into small chunks.

    Args:
        glossary_path (str): Path to `glossary.md`.

    Returns:
        list[dict]: Glossary entries with id, path, title, content, source.
    """
    entries: List[Dict] = []
    if not os.path.isfile(glossary_path):
        return entries
    try:
        with open(glossary_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        if st:
            st.warning(f"Could not read glossary file {glossary_path}: {e}")
        return entries
    pattern = re.compile(r"^\*\*(.+?)\*\*\s*[:—]\s*(.+)")
    for line in lines:
        m = pattern.match(line.strip())
        if m:
            entries.append({
                "id": str(uuid.uuid4()),
                "path": glossary_path,
                "title": m.group(1).strip(),
                "content": m.group(2).strip(),
                "source": "glossary",
            })
    return entries

def split_into_chunks(path: str, text: str, max_chars: int = 1200) -> List[Dict]:
    """
    Split a document into concise chunks for retrieval.

    - Special handling for `faq.md` (one chunk per `###` question)
    - Otherwise splits by headings and packs paragraphs up to `max_chars`

    Args:
        path (str): Source file path.
        text (str): File contents.
        max_chars (int): Maximum characters per chunk (default 1200).

    Returns:
        list[dict]: Chunks with {id, path, title, content}.
    """
    base = os.path.basename(path).lower()
    chunks: List[Dict] = []

    if base == "faq.md":
        parts = re.split(r"\n(?=### )", text)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            m = re.match(r"^###\s+(.+?)(?:\s*[:\-–—]\s*(.*))?$", part.splitlines()[0])
            if not m:
                continue
            raw_title = m.group(1).strip()
            inline_answer = (m.group(2) or "").strip()

            # body = everything after first line, skipping leading blanks
            lines = part.splitlines()
            body_lines = []
            for ln in lines[1:]:
                if not body_lines and not ln.strip():
                    continue
                body_lines.append(ln)
            content = "\n".join(body_lines).strip()

            if inline_answer:
                content = inline_answer + ("\n\n" + content if content else "")

            content = _clean_markdown(content)
            if len(content) > max_chars:
                content = content[:max_chars] + "..."
            if not content:
                content = "_This FAQ question exists but its answer content is empty. Please add text under the heading in `faq.md`._"

            for t in [t.strip() for t in re.split(r"\s*/\s*", raw_title) if t.strip()]:
                chunks.append({"id": str(uuid.uuid4()), "path": path, "title": t, "content": content})
        return chunks

    # default: split by top-level/second-level headings; then paragraph-pack to <= max_chars
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

# ---------- caching wrapper ----------
if st:
    cache_data = st.cache_data
else:
    def cache_data(**_kwargs):
        def _wrap(fn): return fn
        return _wrap

@cache_data(show_spinner=False)
def build_corpus(docs_dir: str):
    """
    Build a TF–IDF corpus from docs and glossary.

    Args:
        docs_dir (str): Root directory of documentation.

    Returns:
        tuple: (chunks: list[dict], vectorizer: TfidfVectorizer | None, X: scipy.sparse.csr_matrix | None)
    """
    docs = read_docs(docs_dir)
    all_chunks: List[Dict] = []
    for p, t in docs:
        all_chunks.extend(split_into_chunks(p, t, max_chars=1200))
    all_chunks.extend(extract_glossary_entries(os.path.join(docs_dir, 'glossary.md')))
    if not all_chunks:
        return [], None, None

    texts = [c["content"] for c in all_chunks]
    vectorizer = TfidfVectorizer(strip_accents="unicode", ngram_range=(1, 2), max_df=0.9, min_df=1)
    X = vectorizer.fit_transform(texts)
    return all_chunks, vectorizer, X

# ---------- retrieval / synthesis ----------
def retrieve(query: str, chunks: List[Dict], vectorizer, X, top_k: int = 5) -> List[Dict]:
    """
    Retrieve the most relevant chunks for a query.

    Strategy: definition lookup → FAQ exact/fuzzy → TF–IDF ranking with small boosts.

    Args:
        query (str): User query.
        chunks (list[dict]): All chunks built by `build_corpus`.
        vectorizer: Fitted TfidfVectorizer.
        X: TF–IDF matrix.
        top_k (int): Number of results to return.

    Returns:
        list[dict]: Top-ranked chunks (with `score` for TF–IDF phase).
    """
    is_def, term = is_definition_query(query)
    if is_def:
        term_norm = normalize_text(term)
        # exact glossary title
        for c in chunks:
            if c.get("source") == "glossary" and normalize_text(c.get("title","")) == term_norm:
                return [c]
        # containment (handles titles like 'Cold Rent (Kaltmiete)')
        for c in chunks:
            if c.get("source") == "glossary":
                t_norm = normalize_text(c.get("title",""))
                if term_norm in t_norm or t_norm in term_norm:
                    return [c]
        # token-overlap fallback
        q_tokens = set(term_norm.split())
        best_g, best_overlap = None, 0.0
        for c in chunks:
            if c.get("source") != "glossary": continue
            t_norm = normalize_text(c.get("title",""))
            if not t_norm: continue
            t_tokens = set(t_norm.split())
            if not t_tokens: continue
            overlap = len(q_tokens & t_tokens) / max(1, len(q_tokens | t_tokens))
            if overlap > best_overlap:
                best_overlap, best_g = overlap, c
        if best_g and best_overlap >= 0.5:
            return [best_g]

    # FAQ exact and fuzzy
    q_norm = normalize_text(query)
    for c in chunks:
        if str(c.get("path","")).endswith("faq.md") and normalize_text(c.get("title","")) == q_norm:
            return [c]
    for c in chunks:
        if str(c.get("path","")).endswith("faq.md"):
            t_norm = normalize_text(c.get("title",""))
            if t_norm and (t_norm in q_norm or q_norm in t_norm):
                return [c]
    # token-overlap FAQ
    q_tokens = set(q_norm.split())
    best_faq, best_overlap = None, 0.0
    for c in chunks:
        if str(c.get("path","")).endswith("faq.md"):
            t_norm = normalize_text(c.get("title",""))
            if not t_norm: continue
            t_tokens = set(t_norm.split())
            if not t_tokens: continue
            overlap = len(q_tokens & t_tokens) / max(1, len(q_tokens | t_tokens))
            if overlap > best_overlap:
                best_overlap, best_faq = overlap, c
    if best_faq and best_overlap >= 0.5:
        return [best_faq]

    # TF-IDF fallback + boosts
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, X)[0]
    faq_keywords = {"goal", "purpose", "exist", "why", "about", "what is this"}
    is_faq_like = any(k in q_norm for k in faq_keywords)
    for i, c in enumerate(chunks):
        boost = 0.0
        path_str = c.get("path", "")
        if c.get("source") == "glossary" or path_str.endswith("glossary.md"):
            boost += 0.2
        if is_def:
            title_norm = (c.get("title","")).lower()
            if term and normalize_text(term) in normalize_text(title_norm):
                boost += 0.1
        if path_str.endswith("faq.md") and is_faq_like:
            boost += 0.5
        sims[i] += boost
    top_idx = sims.argsort()[::-1][:top_k]
    return [{**chunks[i], "score": float(sims[i])} for i in top_idx]

def synthesize_answer(query: str, hits: List[Dict]) -> str:
    """
    Compose a concise answer from retrieved chunks.

    - Glossary hit → short definition
    - Otherwise → brief lead + bulletized key points (max ~150 words)

    Args:
        query (str): Original user query (unused in composition, for context).
        hits (list[dict]): Retrieved chunks.

    Returns:
        str: Markdown-formatted answer.
    """
    if not hits:
        return ("I couldn't find this in the project documentation yet. "
                "If it's important, we should add it to the Methodology or Glossary.")
    top = hits[0]
    if top.get("source") == "glossary":
        sentences = re.split(r"(?<=[.!?])\s+", top["content"].strip())
        concise = " ".join(sentences[:2]).strip()
        concise = _clean_markdown(concise)
        words = concise.split()
        if len(words) > 80:
            concise = " ".join(words[:80]) + "..."
        return concise + "\n\n*This definition is from the project glossary.*"

    snippets, used, total_words, max_words = [], 0, 0, 150
    for h in hits:
        for sent in re.split(r"(?<=[.!?])\s+", h["content"].strip()):
            if not sent.strip():
                continue
            n = len(sent.split())
            if total_words + n > max_words:
                remaining = max_words - total_words
                if remaining > 0:
                    snippets.append(" ".join(sent.split()[:remaining]) + "...")
                break
            snippets.append(sent.strip())
            total_words += n
        used += 1
        if used >= 3 or total_words >= max_words:
            break

    answer = " ".join(snippets) if snippets else hits[0]["content"][:600]
    answer = _clean_markdown(answer)
    answer = _as_bullets(answer, max_bullets=4)
    return (answer +
            "\n\n*If anything is unclear or seems missing, it may not be documented yet. "
            "I only answer from the local project docs.*")

def citation_line(hits: List[Dict]) -> str:
    """
    Format a compact citation line for the top sources.

    Args:
        hits (list[dict]): Retrieved chunks.

    Returns:
        str: Markdown string like "Sources: Title (file); ..." or empty string.
    """
    if not hits:
        return ""
    items = []
    for h in hits[:3]:
        fname = os.path.basename(h["path"])
        title = h.get("title") or fname
        items.append(f"**{title}** ({fname})")
    return "Sources: " + "; ".join(items)

# utils/content.py
import os
import re
import glob
import uuid
import pathlib
from typing import List, Dict, Tuple

try:
    import streamlit as st
except Exception:
    st = None  # allow importing outside Streamlit

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils.text import normalize_text, _clean_markdown, _as_bullets, is_definition_query

# ---------- file reading / parsing ----------
def read_docs(docs_dir: str) -> List[Tuple[str, str]]:
    """Return list of (path, text) for .md and .txt files in docs_dir."""
    paths = glob.glob(os.path.join(docs_dir, "**/*.md"), recursive=True) + \
            glob.glob(os.path.join(docs_dir, "**/*.txt"), recursive=True)
    results: List[Tuple[str, str]] = []
    for p in paths:
        try:
            with open(p, "r", encoding="utf-8") as f:
                results.append((p, f.read()))
        except Exception as e:
            if st:
                st.warning(f"Could not read {p}: {e}")
    return results

def extract_glossary_entries(glossary_path: str) -> List[Dict]:
    """Parse **Term**: Definition lines into glossary chunks."""
    entries: List[Dict] = []
    if not os.path.isfile(glossary_path):
        return entries
    try:
        with open(glossary_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        if st:
            st.warning(f"Could not read glossary file {glossary_path}: {e}")
        return entries
    pattern = re.compile(r"^\*\*(.+?)\*\*\s*[:—]\s*(.+)")
    for line in lines:
        m = pattern.match(line.strip())
        if m:
            entries.append({
                "id": str(uuid.uuid4()),
                "path": glossary_path,
                "title": m.group(1).strip(),
                "content": m.group(2).strip(),
                "source": "glossary",
            })
    return entries

def split_into_chunks(path: str, text: str, max_chars: int = 1200) -> List[Dict]:
    """
    Chunk by headings/paragraphs; special handling for faq.md (split per '###' question).
    Returns list of dicts with: id, path, title, content.
    """
    base = os.path.basename(path).lower()
    chunks: List[Dict] = []

    if base == "faq.md":
        parts = re.split(r"\n(?=### )", text)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            m = re.match(r"^###\s+(.+?)(?:\s*[:\-–—]\s*(.*))?$", part.splitlines()[0])
            if not m:
                continue
            raw_title = m.group(1).strip()
            inline_answer = (m.group(2) or "").strip()

            # body = everything after first line, skipping leading blanks
            lines = part.splitlines()
            body_lines = []
            for ln in lines[1:]:
                if not body_lines and not ln.strip():
                    continue
                body_lines.append(ln)
            content = "\n".join(body_lines).strip()

            if inline_answer:
                content = inline_answer + ("\n\n" + content if content else "")

            content = _clean_markdown(content)
            if len(content) > max_chars:
                content = content[:max_chars] + "..."
            if not content:
                content = "_This FAQ question exists but its answer content is empty. Please add text under the heading in `faq.md`._"

            for t in [t.strip() for t in re.split(r"\s*/\s*", raw_title) if t.strip()]:
                chunks.append({"id": str(uuid.uuid4()), "path": path, "title": t, "content": content})
        return chunks

    # default: split by top-level/second-level headings; then paragraph-pack to <= max_chars
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

# ---------- caching wrapper ----------
if st:
    cache_data = st.cache_data
else:
    def cache_data(**_kwargs):
        def _wrap(fn): return fn
        return _wrap

@cache_data(show_spinner=False)
def build_corpus(docs_dir: str):
    """Build chunks + TF-IDF matrix from docs and glossary."""
    docs = read_docs(docs_dir)
    all_chunks: List[Dict] = []
    for p, t in docs:
        all_chunks.extend(split_into_chunks(p, t, max_chars=1200))
    all_chunks.extend(extract_glossary_entries(os.path.join(docs_dir, 'glossary.md')))
    if not all_chunks:
        return [], None, None

    texts = [c["content"] for c in all_chunks]
    vectorizer = TfidfVectorizer(strip_accents="unicode", ngram_range=(1, 2), max_df=0.9, min_df=1)
    X = vectorizer.fit_transform(texts)
    return all_chunks, vectorizer, X

# ---------- retrieval / synthesis ----------
def retrieve(query: str, chunks: List[Dict], vectorizer, X, top_k: int = 5) -> List[Dict]:
    """Definition first; then exact/fuzzy FAQ; else TF-IDF ranking with boosts."""
    is_def, term = is_definition_query(query)
    if is_def:
        term_norm = normalize_text(term)
        # exact glossary title
        for c in chunks:
            if c.get("source") == "glossary" and normalize_text(c.get("title","")) == term_norm:
                return [c]
        # containment (handles titles like 'Cold Rent (Kaltmiete)')
        for c in chunks:
            if c.get("source") == "glossary":
                t_norm = normalize_text(c.get("title",""))
                if term_norm in t_norm or t_norm in term_norm:
                    return [c]
        # token-overlap fallback
        q_tokens = set(term_norm.split())
        best_g, best_overlap = None, 0.0
        for c in chunks:
            if c.get("source") != "glossary": continue
            t_norm = normalize_text(c.get("title",""))
            if not t_norm: continue
            t_tokens = set(t_norm.split())
            if not t_tokens: continue
            overlap = len(q_tokens & t_tokens) / max(1, len(q_tokens | t_tokens))
            if overlap > best_overlap:
                best_overlap, best_g = overlap, c
        if best_g and best_overlap >= 0.5:
            return [best_g]

    # FAQ exact and fuzzy
    q_norm = normalize_text(query)
    for c in chunks:
        if str(c.get("path","")).endswith("faq.md") and normalize_text(c.get("title","")) == q_norm:
            return [c]
    for c in chunks:
        if str(c.get("path","")).endswith("faq.md"):
            t_norm = normalize_text(c.get("title",""))
            if t_norm and (t_norm in q_norm or q_norm in t_norm):
                return [c]
    # token-overlap FAQ
    q_tokens = set(q_norm.split())
    best_faq, best_overlap = None, 0.0
    for c in chunks:
        if str(c.get("path","")).endswith("faq.md"):
            t_norm = normalize_text(c.get("title",""))
            if not t_norm: continue
            t_tokens = set(t_norm.split())
            if not t_tokens: continue
            overlap = len(q_tokens & t_tokens) / max(1, len(q_tokens | t_tokens))
            if overlap > best_overlap:
                best_overlap, best_faq = overlap, c
    if best_faq and best_overlap >= 0.5:
        return [best_faq]

    # TF-IDF fallback + boosts
    q_vec = vectorizer.transform([query])
    sims = cosine_similarity(q_vec, X)[0]
    faq_keywords = {"goal", "purpose", "exist", "why", "about", "what is this"}
    is_faq_like = any(k in q_norm for k in faq_keywords)
    for i, c in enumerate(chunks):
        boost = 0.0
        path_str = c.get("path", "")
        if c.get("source") == "glossary" or path_str.endswith("glossary.md"):
            boost += 0.2
        if is_def:
            title_norm = (c.get("title","")).lower()
            if term and normalize_text(term) in normalize_text(title_norm):
                boost += 0.1
        if path_str.endswith("faq.md") and is_faq_like:
            boost += 0.5
        sims[i] += boost
    top_idx = sims.argsort()[::-1][:top_k]
    return [{**chunks[i], "score": float(sims[i])} for i in top_idx]

def synthesize_answer(query: str, hits: List[Dict]) -> str:
    """Concise answer; glossary returns definition, otherwise lead + bullets."""
    if not hits:
        return ("I couldn't find this in the project documentation yet. "
                "If it's important, we should add it to the Methodology or Glossary.")
    top = hits[0]
    if top.get("source") == "glossary":
        sentences = re.split(r"(?<=[.!?])\s+", top["content"].strip())
        concise = " ".join(sentences[:2]).strip()
        concise = _clean_markdown(concise)
        words = concise.split()
        if len(words) > 80:
            concise = " ".join(words[:80]) + "..."
        return concise + "\n\n*This definition is from the project glossary.*"

    snippets, used, total_words, max_words = [], 0, 0, 150
    for h in hits:
        for sent in re.split(r"(?<=[.!?])\s+", h["content"].strip()):
            if not sent.strip():
                continue
            n = len(sent.split())
            if total_words + n > max_words:
                remaining = max_words - total_words
                if remaining > 0:
                    snippets.append(" ".join(sent.split()[:remaining]) + "...")
                break
            snippets.append(sent.strip())
            total_words += n
        used += 1
        if used >= 3 or total_words >= max_words:
            break

    answer = " ".join(snippets) if snippets else hits[0]["content"][:600]
    answer = _clean_markdown(answer)
    answer = _as_bullets(answer, max_bullets=4)
    return (answer +
            "\n\n*If anything is unclear or seems missing, it may not be documented yet. "
            "I only answer from the local project docs.*")

def citation_line(hits: List[Dict]) -> str:
    """Nice inline citation line for top sources."""
    if not hits:
        return ""
    items = []
    for h in hits[:3]:
        fname = os.path.basename(h["path"])
        title = h.get("title") or fname
        items.append(f"**{title}** ({fname})")
    return "Sources: " + "; ".join(items)
