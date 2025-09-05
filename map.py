import geopandas as gpd
from pathlib import Path

SRC = Path("data/raw/berlin_ortsteil_boundaries.geojson")  # rich source (has attributes)
OUT = Path("data/static/berlin_ortsteil_boundaries.parquet")
OUT.parent.mkdir(parents=True, exist_ok=True)

gdf = gpd.read_file(SRC).to_crs(4326)

# pick a name column that exists in your source (includes your file's fields)
CANDIDATES = [
    "OTEIL",           # Ortsteil name (seen in your file)
    "spatial_alias",   # human-readable alias (also seen)
    "Ortsteil",
    "GEN",
    "name",
    "BEZIRK",         # district name (fallback; not ideal for Ortsteil)
    "BEZ",
]

name_col = None
for cand in CANDIDATES:
    if cand in gdf.columns:
        name_col = cand
        break

if name_col is None:
    print("Available columns:", list(gdf.columns))
    raise ValueError("No suitable name column found. Update CANDIDATES with one of the columns above.")

# create a normalized slug column to match df['ortsteil']
_UMLAUT = str.maketrans({"ä":"ae","ö":"oe","ü":"ue","ß":"ss","Ä":"Ae","Ö":"Oe","Ü":"Ue"})
_DASHES = {"\u2013": "-", "\u2014": "-", "\u2212": "-"}

def norm_slug(x):
    t = (str(x) or "").strip().lower().translate(_UMLAUT)
    for a, b in _DASHES.items():
        t = t.replace(a, b)
    return " ".join(t.split())  # collapse spaces

# Prefer OTEIL/spatial_alias as display name if present
if "OTEIL" in gdf.columns:
    display_col = "OTEIL"
elif "spatial_alias" in gdf.columns:
    display_col = "spatial_alias"
else:
    display_col = name_col

gdf["ortsteil_slug"] = gdf[name_col].astype(str).map(norm_slug)

# Keep only what the app needs (slug + a human-readable display name)
keep = ["ortsteil_slug", display_col, "geometry"]
# If display_col duplicates slug source but has another good label, it's fine
keep = list(dict.fromkeys(keep))  # dedupe

gdf[keep].to_parquet(OUT)
print("Saved:", OUT, "with columns:", keep)