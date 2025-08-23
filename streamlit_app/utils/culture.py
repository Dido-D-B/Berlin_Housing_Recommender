from __future__ import annotations
import json
import os
from typing import Optional, Dict, Any, Tuple

import requests
import streamlit as st

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CACHE_PATH = os.path.join(DATA_DIR, "cultural_facts.json")

# Ensure data dir exists
os.makedirs(DATA_DIR, exist_ok=True)

# ------------------------------
# Wikipedia helpers
# ------------------------------
WIKI_REST_SUMMARY = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"

CANDIDATE_PATTERNS = (
    # Prefer explicit locality/Ortsteil pages first
    "{ortsteil} (Ortsteil)",        # de
    "{ortsteil} (locality)",        # en
    "{ortsteil}, Berlin",           # generic disambiguation often points to locality
    "{ortsteil} (Berlin)",
    "{ortsteil}",
)

LANGS = ("en", "de")


def _is_locality(payload: Dict[str, Any]) -> bool:
    desc = (payload.get("description") or "").lower()
    title = (payload.get("title") or "").lower()
    return (
        "ortsteil" in desc
        or "locality" in desc
        or ("quarter" in desc and "berlin" in desc)
        or "ortsteil" in title
        or "locality" in title
    )


def _is_borough(payload: Dict[str, Any]) -> bool:
    desc = (payload.get("description") or "").lower()
    title = (payload.get("title") or "").lower()
    return (
        "borough" in desc
        or "bezirk" in desc
        or "borough" in title
        or "bezirk" in title
    )


# Helper to get English Wikipedia title from Wikidata, given a QID
from typing import Optional

def _get_en_title_from_wikidata(qid: str) -> Optional[str]:
    """Return the English Wikipedia title for a Wikidata item, if it exists."""
    url = f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"
    try:
        r = requests.get(url, timeout=6)
        if r.status_code != 200:
            return None
        data = r.json()
        ent = data.get("entities", {}).get(qid, {})
        sitelinks = ent.get("sitelinks", {})
        enwiki = sitelinks.get("enwiki")
        if enwiki and enwiki.get("title"):
            return enwiki["title"]
    except Exception:
        pass
    return None

# ------------------------------
# District (Bezirk) resolver — prefer borough pages in EN, then DE
# ------------------------------
DISTRICT_PATTERNS = (
    "{bezirk} (borough)",   # en
    "{bezirk} (Bezirk)",    # de
    "{bezirk}, Berlin",
    "{bezirk} (Berlin)",
    "{bezirk}",
)


def _best_wiki_hit_district(bezirk: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (extract, url) for a *district/borough* page, preferring English."""
    for lang in ("en", "de"):
        for pattern in DISTRICT_PATTERNS:
            title = pattern.format(bezirk=bezirk)
            payload = _request_summary(title, lang)
            if not payload:
                continue
            if payload.get("type") == "https://mediawiki.org/wiki/HyperSwitch/errors/not_found":
                continue
            # For district mode, *prefer* borough pages (Bezirk)
            if not _is_borough(payload):
                # Allow non-borough only as a fallback if nothing else exists in this lang
                pass
            extract = payload.get("extract")
            url = payload.get("content_urls", {}).get("desktop", {}).get("page")
            if extract and url:
                return extract, url
    return None, None


def _request_summary(title: str, lang: str) -> Optional[Dict[str, Any]]:
    url = WIKI_REST_SUMMARY.format(lang=lang, title=title.replace(" ", "%20"))
    try:
        r = requests.get(url, timeout=6)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None




def _best_wiki_hit(ortsteil: str, bezirk: str) -> Tuple[Optional[str], Optional[str]]:
    """Return (extract, url) preferring English locality pages; fall back to German locality pages.
    Skip borough pages when names collide. If only a German locality is found, try to
    find its English counterpart via Wikidata sitelinks; otherwise return the German extract.
    """
    best_de: Optional[Dict[str, Any]] = None
    best_en: Optional[Dict[str, Any]] = None

    # Search both languages and store the best locality candidates
    for lang in ("de", "en"):
        for pattern in CANDIDATE_PATTERNS:
            title = pattern.format(ortsteil=ortsteil, bezirk=bezirk)
            payload = _request_summary(title, lang)
            if not payload:
                continue
            if payload.get("type") == "https://mediawiki.org/wiki/HyperSwitch/errors/not_found":
                continue
            # Skip borough pages unless they are clearly also marked as locality
            if _is_borough(payload) and not _is_locality(payload):
                continue
            # Keep only locality-leaning pages
            if not _is_locality(payload):
                continue
            if lang == "en" and best_en is None:
                best_en = payload
            elif lang == "de" and best_de is None:
                best_de = payload

    # Prefer an English locality directly if found
    if best_en:
        extract = best_en.get("extract")
        url = best_en.get("content_urls", {}).get("desktop", {}).get("page")
        if extract and url:
            return extract, url

    # Otherwise try to map the German locality to an English page via Wikidata
    if best_de:
        qid = best_de.get("wikibase_item")
        if qid:
            en_title = _get_en_title_from_wikidata(qid)
            if en_title:
                en_payload = _request_summary(en_title, "en")
                if en_payload and en_payload.get("type") != "https://mediawiki.org/wiki/HyperSwitch/errors/not_found":
                    if not (_is_borough(en_payload) and not _is_locality(en_payload)):
                        extract = en_payload.get("extract")
                        url = en_payload.get("content_urls", {}).get("desktop", {}).get("page")
                        if extract and url:
                            return extract, url
        # Fall back to German extract if no English sitelink
        extract = best_de.get("extract")
        url = best_de.get("content_urls", {}).get("desktop", {}).get("page")
        if extract and url:
            return extract, url

    return None, None


@st.cache_data(show_spinner=False, ttl=60 * 60 * 24 * 30)
def get_cultural_blurb(bezirk: str, ortsteil: str) -> Dict[str, Any]:
    """
    TEMPORARY (phase 1): Return a cultural blurb for the *district* (Bezirk) only.
    We ignore the Ortsteil for now. Results are cached under a district key.
    Later, we'll re-introduce Ortsteil (subdistrict) manual content with images.
    """
    cache_key = f"district:{bezirk}"

    # Load local cache (district namespace)
    store: Dict[str, Any] = {}
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH, "r", encoding="utf-8") as f:
                store = json.load(f)
        except Exception:
            store = {}

    if cache_key in store:
        return store[cache_key]

    # Resolve district wiki page (EN preferred, DE fallback)
    extract, url = _best_wiki_hit_district(bezirk)
    item = {
        "bezirk": bezirk,
        "ortsteil": None,  # intentionally None during district-only phase
        "blurb": extract,
        "url": url,
        "source": "wikipedia-district",
        "mode": "district",
    }

    # Persist to cache using district key
    store[cache_key] = item
    try:
        with open(CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

    return item