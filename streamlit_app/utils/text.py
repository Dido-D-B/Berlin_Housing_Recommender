# Robust dash/whitespace normalization to match keys reliably
_DASHES = "\u2013\u2014\u2012\u2212\u2010\u2011"  # en/em/figure/minus/hyphen variants

# Normalize strings for consistent comparison (dashes, umlauts, ß, whitespace).
def norm(s: str):
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
    """Apply the same normalization as _norm, plus turn spaces/underscores to '-'."""
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
    """Normalize a district name to a filename-friendly slug used by images.
    Example: "Tempelhof‑Schöneberg" -> "tempelhof-schoeneberg".
    """
    s = norm(name)
    s = s.replace(" ", "-")  # spaces to dashes
    return s

# Restore human-friendly German capitalization and common umlauts in names.
def de_pretty(s: str) -> str:
    """
    Return a human-friendly German-capitalized name (restores ä/ö/ü/ß where common
    transliterations appear and applies Title-Case across hyphenated and spaced tokens).
    Safe for already-correct strings.
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