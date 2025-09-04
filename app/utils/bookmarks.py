"""
bookmarks.py

Session state utilities for managing user bookmarks in the Berlin Housing Affordability app.

Bookmarks are stored in st.session_state as a dictionary keyed by "bezirk—subdistrict".
Each entry stores district, subdistrict, and optional metadata.
"""

# Imports
from __future__ import annotations
import json
from typing import Dict, Any, List, Optional
import streamlit as st

# Session state helpers
def _ensure_state():
    """Ensure that st.session_state has a bookmarks dict initialized."""
    if "bookmarks" not in st.session_state:
        # store as dict: {key: {"bezirk":..., "subdistrict":..., "meta": {...}}}
        st.session_state.bookmarks = {}

# Generate a unique bookmark key from district + subdistrict (single source of truth).
def _make_key(bezirk: str, subdistrict: str) -> str:
    """
    Create a stable key from district and subdistrict.

    Args:
        bezirk (str): District name.
        subdistrict (str): Subdistrict name.

    Returns:
        str: Unique bookmark key in format "bezirk—subdistrict".
    """
    # Single source of truth for the key format
    return f"{bezirk}—{subdistrict}"

# Public API
def add_bookmark(*, bezirk: str, subdistrict: str, meta: Optional[Dict[str, Any]] = None) -> str:
    """
    Add a bookmark entry to session_state.

    Args:
        bezirk (str): District name.
        subdistrict (str): Subdistrict name.
        meta (dict, optional): Additional metadata.

    Returns:
        str: The bookmark key.
    """
    _ensure_state()
    key = _make_key(bezirk, subdistrict)
    st.session_state.bookmarks[key] = {
        "bezirk": bezirk,
        "subdistrict": subdistrict,
        "meta": meta or {},
    }
    return key

# Remove a bookmark entry by its key (if present).
def remove_bookmark(key: str) -> None:
    """
    Remove a bookmark entry by key if it exists.

    Args:
        key (str): Bookmark key.
    """
    _ensure_state()
    st.session_state.bookmarks.pop(key, None)

# Clear all stored bookmarks from session_state.
def clear_bookmarks() -> None:
    """Remove all bookmarks from session_state."""
    _ensure_state()
    st.session_state.bookmarks.clear()

# Check whether a given key is already bookmarked.
def is_bookmarked(key: str) -> bool:
    """
    Check if a key is already bookmarked.

    Args:
        key (str): Bookmark key.

    Returns:
        bool: True if bookmarked, False otherwise.
    """
    _ensure_state()
    return key in st.session_state.bookmarks

# Return a stable sorted list of bookmark entries (each with key, bezirk, subdistrict, meta).
def list_bookmarks() -> List[Dict[str, Any]]:
    """
    Get a stable sorted list of all bookmark entries.

    Returns:
        list[dict]: List of bookmark dicts including 'key', 'bezirk', 'subdistrict', and 'meta'.
    """
    _ensure_state()
    # Return a stable list of entries (sorted by key)
    items = []
    for key in sorted(st.session_state.bookmarks.keys()):
        entry = st.session_state.bookmarks[key].copy()
        entry["key"] = key
        items.append(entry)
    return items

# Export all bookmarks to a formatted JSON string (UTF-8 safe).
def to_json() -> str:
    """
    Export all bookmarks as a formatted JSON string.

    Returns:
        str: JSON string with all bookmarks.
    """
    _ensure_state()
    return json.dumps(st.session_state.bookmarks, indent=2, ensure_ascii=False)