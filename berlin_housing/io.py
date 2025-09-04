"""This module provides I/O utilities for the Berlin Housing project,
including functions to load the master dataset from CSV and clean
unnecessary index columns.
"""

# Imports
import pandas as pd
from .config import MASTER_CSV

# Load master dataset from CSV, drop unnecessary index columns
def load_master() -> pd.DataFrame:
    df = pd.read_csv(MASTER_CSV)
    for junk in ("index", "Unnamed: 0"):
        if junk in df.columns:
            df = df.drop(columns=junk)
    return df