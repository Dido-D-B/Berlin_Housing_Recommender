# script/pca_export.py
from __future__ import annotations
import pandas as pd
from pathlib import Path
from berlin_housing.features import add_sanity_checks, engineer_features, select_model_features
import numpy as np
from berlin_housing.preprocessing import make_preprocessor, fit_transform_preprocessor
from berlin_housing.pca import pca_2d_for_viz, pca_until_variance

IN_PATH  = "data/processed/final_master.csv"
OUT_DIR  = "data/modeling/berlin_pca"
OUT_NAME = "berlin_subdistricts_pca.csv"

def main():
    df = pd.read_csv(IN_PATH)

    # sanity + engineering
    df = add_sanity_checks(df)
    df = engineer_features(df)

    # choose model features (drop ids + optional columns)
    X = select_model_features(df)

    # Replace infs created by divisions with NaN; imputer will handle them
    X = X.replace([np.inf, -np.inf], np.nan)

    # impute + scale (handles NaNs before PCA)
    preproc = make_preprocessor(kind="standard", impute_strategy="median")
    Xs, preproc = fit_transform_preprocessor(preproc, X)

    # 2D viz (optional: keep if you want the ratios)
    df_pca2, var2 = pca_2d_for_viz(Xs, labels=df["ortsteil"])
    print(f"Explained variance 2D: {var2}")

    # PCA until 90% variance
    Z, pca, cum = pca_until_variance(Xs, target=0.90)

    # attach ortsteil and save
    out = Z.copy()
    out.insert(0, "ortsteil", df["ortsteil"].values)

    Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
    out.to_csv(Path(OUT_DIR) / OUT_NAME, index=False)
    print(f"✅ Saved {OUT_NAME} with shape {out.shape}")

if __name__ == "__main__":
    main()