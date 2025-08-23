# streamlit_app/utils/bookmarks.py
from __future__ import annotations
import json
from typing import Dict, Any, List, Optional

import streamlit as st

# ---- Session state helpers ----
def _ensure_state():
    if "bookmarks" not in st.session_state:
        # store as dict: {key: {"bezirk":..., "subdistrict":..., "meta": {...}}}
        st.session_state.bookmarks = {}

def _make_key(bezirk: str, subdistrict: str) -> str:
    # Single source of truth for the key format
    return f"{bezirk}—{subdistrict}"

# ---- Public API ----
def add_bookmark(*, bezirk: str, subdistrict: str, meta: Optional[Dict[str, Any]] = None) -> str:
    _ensure_state()
    key = _make_key(bezirk, subdistrict)
    st.session_state.bookmarks[key] = {
        "bezirk": bezirk,
        "subdistrict": subdistrict,
        "meta": meta or {},
    }
    return key

def remove_bookmark(key: str) -> None:
    _ensure_state()
    st.session_state.bookmarks.pop(key, None)

def clear_bookmarks() -> None:
    _ensure_state()
    st.session_state.bookmarks.clear()

def is_bookmarked(key: str) -> bool:
    _ensure_state()
    return key in st.session_state.bookmarks

def list_bookmarks() -> List[Dict[str, Any]]:
    _ensure_state()
    # Return a stable list of entries (sorted by key)
    items = []
    for key in sorted(st.session_state.bookmarks.keys()):
        entry = st.session_state.bookmarks[key].copy()
        entry["key"] = key
        items.append(entry)
    return items

def to_json() -> str:
    _ensure_state()
    return json.dumps(st.session_state.bookmarks, indent=2, ensure_ascii=False)