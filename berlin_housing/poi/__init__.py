"""This package provides POI (Points of Interest) utilities for the Berlin Housing project, re-exporting key functions for fetching, processing, and merging POI data."""

from .poi import (
    default_tags,
    fetch_pois_for_polygon,
    fetch_all_pois_by_ortsteil,
    add_tag_columns,
    count_pois_per_ortsteil,
    group_poi_columns,
    merge_poi_to_master,
)

__all__ = [
    "default_tags",
    "fetch_pois_for_polygon",
    "fetch_all_pois_by_ortsteil",
    "add_tag_columns",
    "count_pois_per_ortsteil",
    "group_poi_columns",
    "merge_poi_to_master",
]