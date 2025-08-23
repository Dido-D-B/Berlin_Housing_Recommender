from pathlib import Path
import typer
import geopandas as gpd
from berlin_housing.io import load_table, save_table
from berlin_housing.cleaning import clean_ortsteil_tables
from berlin_housing.poi import merge_poi_to_master

@app.command()
def scrape_poi_all(
    boundaries_path: Path = typer.Option(..., help="GeoJSON of Ortsteil polygons"),
    ortsteil_col: str = typer.Option("OTEIL"),
    out_raw: Path = typer.Option("data/interim/berlin_pois.geojson"),
    out_counts: Path = typer.Option("data/interim/berlin_poi_counts_per_ortsteil.csv"),
    rate_limit_s: float = typer.Option(1.5),
    verbose: int = typer.Option(1),
):
    setup_logging(verbose)
    bounds = gpd.read_file(boundaries_path)
    gdf = fetch_all_pois_by_ortsteil(bounds, ortsteil_col=ortsteil_col, rate_limit_s=rate_limit_s)
    gdf = add_tag_columns(gdf)
    out_raw.parent.mkdir(parents=True, exist_ok=True)
    gdf.to_file(out_raw, driver="GeoJSON")
    counts = count_pois_per_ortsteil(gdf)
    counts = group_poi_columns(counts)
    save_table(counts, out_counts)
    typer.echo(f"✅ Saved raw to {out_raw} and counts to {out_counts}")

@app.command()
def merge_poi_master(
    master_path: Path = typer.Option(..., help="Cleaned ortsteil table CSV/Parquet"),
    poi_counts_path: Path = typer.Option(...),
    out_path: Path = typer.Option("data/master_tables/berlin_ortsteil_master_with_poi_features.csv"),
    verbose: int = typer.Option(1),
):
    setup_logging(verbose)
    master = load_table(master_path)
    poi = load_table(poi_counts_path)
    out = merge_poi_to_master(master, poi)
    save_table(out, out_path)
    typer.echo(f"✅ Wrote merged master+POI to {out_path}")

@app.command()
def clean_ortsteil(
    input_path: Path = typer.Option(..., help="Raw Ortsteil-level CSV/Parquet"),
    output_path: Path = typer.Option("data/cleaned_data/berlin_ortsteil_table.parquet"),
    verbose: int = typer.Option(1),
):
    """Clean raw subdistrict (Ortsteil) data and save a standardized table."""
    setup_logging(verbose)
    df = load_table(input_path)
    out = clean_ortsteil_tables(df)
    save_table(out, output_path)
    typer.echo(f"✅ Wrote cleaned Ortsteil table to {output_path}")


@app.command()
def build_dataset(
    ortsteil_path: Path = typer.Option(..., help="Cleaned Ortsteil table (CSV/Parquet)"),
    poi_counts_path: Path = typer.Option(None, help="POI counts per Ortsteil (CSV/Parquet)"),
    output_path: Path = typer.Option("data/processed/ortsteil_master.parquet"),
    verbose: int = typer.Option(1),
):
    """Merge cleaned Ortsteil data with optional POI counts into a single master dataset."""
    setup_logging(verbose)
    ortsteil_df = load_table(ortsteil_path)
    if poi_counts_path is not None:
        poi_df = load_table(poi_counts_path)
        master = merge_poi_to_master(ortsteil_df, poi_df)
    else:
        master = ortsteil_df.copy()
    save_table(master, output_path)
    typer.echo(f"✅ Built master dataset at {output_path}")