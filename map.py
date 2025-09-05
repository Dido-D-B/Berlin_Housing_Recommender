import geopandas as gpd
from pathlib import Path

SRC = Path("data/raw/berlin_ortsteil_boundaries.geojson")   # your current big file
OUT_DIR = Path("data/static"); OUT_DIR.mkdir(parents=True, exist_ok=True)

# Load & standardize
gdf = gpd.read_file(SRC).to_crs(4326)

# Keep only columns the app needs (adjust names to your schema)
keep_cols = ["ortsteil_id", "ortsteil_name", "bezirk_name", "geometry"]
gdf = gdf[[c for c in keep_cols if c in gdf.columns]]

# Simplify geometry (≈ 30–50m). Increase tolerance if still too big.
gdf["geometry"] = gdf.geometry.simplify(tolerance=0.0004, preserve_topology=True)

# Fix any invalid polygons after simplify
gdf["geometry"] = gdf.buffer(0)

# Save as GeoParquet (best for the app)
parquet_path = OUT_DIR / "berlin_ortsteil_boundaries.parquet"
gdf.to_parquet(parquet_path)

# Also export a lighter GeoJSON if you need it for other tools
geojson_path = OUT_DIR / "berlin_ortsteil_boundaries_light.geojson"
gdf.to_file(geojson_path, driver="GeoJSON")

print("Saved:", parquet_path, geojson_path)