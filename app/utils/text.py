"""
text.py

Text and string normalization utilities for the Berlin Housing Affordability app.

This module provides helpers for:
- Normalizing German names (handling dashes, umlauts, ß)
- Creating safe filename slugs
- Restoring human-readable German capitalization
- Cleaning and formatting text for Q&A/glossary
"""

# Imports
import re
import string
from typing import Tuple

# Robust dash/whitespace normalization to match keys reliably
_DASHES = "\u2013\u2014\u2012\u2212\u2010\u2011"  # en/em/figure/minus/hyphen variants

# Normalize strings for consistent comparison (dashes, umlauts, ß, whitespace).
def norm(s: str):
    """
    Normalize a string for consistent comparison.

    - Converts dash variants to "-"
    - Normalizes umlauts and ß
    - Strips and lowers case
    - Collapses multiple spaces

    Args:
        s (str): Input string.

    Returns:
        str: Normalized string.
    """
    if not isinstance(s, str):
        s = str(s) if s is not None else ""
    # unify dashes to ASCII '-'
    for d in _DASHES:
        s = s.replace(d, "-")
    # also normalize the commonly used em‑dash like '—' (U+2014)
    s = s.replace("—", "-")
    # normalize German umlauts and ß
    repl = {
        "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss",
        "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"
    }
    for k, v in repl.items():
        s = s.replace(k, v)
    return " ".join(s.strip().split()).lower()

# Normalize strings into safe filename bases (lowercase, replace spaces/underscores, transliterate umlauts).
def normalize_filename_base(s: str) -> str:
    """
    Normalize a string into a safe filename base.

    - Applies dash/unicode normalization like `norm`
    - Converts spaces/underscores to "-"
    - Lowercases

    Args:
        s (str): Input string.

    Returns:
        str: Normalized filename-safe base.
    """
    if not isinstance(s, str):
        s = str(s) if s is not None else ""
    # unify dashes
    for d in _DASHES:
        s = s.replace(d, "-")
    s = s.replace("—", "-")
    # umlauts/ß
    repl = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "Ae", "Ö": "Oe", "Ü": "Ue"}
    for k, v in repl.items():
        s = s.replace(k, v)
    # spaces/underscores
    s = s.replace("_", "-")
    s = " ".join(s.strip().split()).lower().replace(" ", "-")
    return s

# Convert district names into slugs suitable for filenames (Tempelhof-Schöneberg → tempelhof-schoeneberg).
def district_slug(name: str) -> str:
    """
    Convert a district name to a filename-friendly slug.

    Example:
        "Tempelhof-Schöneberg" → "tempelhof-schoeneberg"

    Args:
        name (str): District name.

    Returns:
        str: Slugified district string.
    """
    s = norm(name)
    s = s.replace(" ", "-")  # spaces to dashes
    return s

# Restore human-friendly German capitalization and common umlauts in names.
def de_pretty(s: str) -> str:
    """
    Restore human-friendly German capitalization and umlauts.

    - Capitalizes tokens in hyphenated/space-separated names
    - Replaces transliterations (ae→ä, oe→ö, ue→ü, ss→ß)
    - Safe for already correct strings

    Args:
        s (str): Input string.

    Returns:
        str: Human-friendly German name.
    """
    if not isinstance(s, str):
        return ""
    s = s.strip()
    if not s:
        return ""
    low = s.lower().replace("–", "-")
    parts = []
    for token in low.split("-"):
        token = " ".join(w.capitalize() for w in token.split())
        parts.append(token)
    out = "-".join(parts)
    for a, b in [("Ae", "Ä"), ("Oe", "Ö"), ("Ue", "Ü"), ("ae", "ä"), ("oe", "ö"), ("ue", "ü"), ("ss", "ß")]:
        out = out.replace(a, b)
    return out

#

def normalize_text(s: str) -> str:
    """
    Normalize text for query matching.

    - Lowercases
    - Removes punctuation
    - Strips whitespace

    Args:
        s (str): Input string.

    Returns:
        str: Normalized text.
    """
    s = s.lower()
    return s.translate(str.maketrans('', '', string.punctuation)).strip()

def is_definition_query(q: str) -> Tuple[bool, str]:
    """
    Detect if a query asks for a definition.

    Matches patterns like:
    - "What is X?"
    - "Define X"
    - "Meaning of X"

    Args:
        q (str): User query.

    Returns:
        tuple[bool, str]: (True, term) if definition query, else (False, "").
    """
    q_norm = normalize_text(q)
    patterns = [
        r"^what is (.+)$",
        r"^define (.+)$",
        r"^meaning of (.+)$",
    ]
    for pat in patterns:
        m = re.match(pat, q_norm)
        if m:
            return True, m.group(1).strip()
    return False, ""

def _clean_markdown(s: str) -> str:
    """
    Clean markdown text for display.

    - Removes heading lines
    - Collapses excess blank lines

    Args:
        s (str): Markdown string.

    Returns:
        str: Cleaned markdown string.
    """
    s = re.sub(r"^#{1,6}\s+.*$", "", s, flags=re.MULTILINE)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()

def _as_bullets(text: str, max_bullets: int = 4) -> str:
    """
    Format text as a lead sentence with bullet points.

    Args:
        text (str): Input text.
        max_bullets (int): Maximum number of bullet points.

    Returns:
        str: Formatted text with lead and bullets.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if not sentences:
        return text
    lead = sentences[0].strip()
    bullets = [f"- {s.strip()}" for s in sentences[1:1+max_bullets] if s.strip()]
    return lead + ("\n\n" + "\n".join(bullets) if bullets else "")

# Helper: prettify names with German umlauts and title case
def format_german_title(name: str) -> str:
    if not isinstance(name, str):
        return str(name)
    s = name.replace("ae", "ä").replace("oe", "ö").replace("ue", "ü")
    s = s.replace("Ae", "Ä").replace("Oe", "Ö").replace("Ue", "Ü")
    return s.title()