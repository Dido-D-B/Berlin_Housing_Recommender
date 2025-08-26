import numpy as np
import pandas as pd
from typing import Dict, Optional, Sequence

# Anchors (approximate Mietspiegel 2024 values)
ANCHORS_CLASS_TO_EUR: Dict[float, float] = {
    1.0: 9.0,
    1.5: 11.0,
    1.7: 12.0,
    1.9: 13.2,
    2.1: 14.4,
    2.3: 15.6,
    2.5: 16.8,
    2.9: 19.0,
}

# Interpolate Mietspiegel class values to €/m² using anchor mapping
def class_to_eur_interpolated(
    values: Sequence[float],
    anchors: Dict[float, float] = ANCHORS_CLASS_TO_EUR
) -> np.ndarray:
    """
    Map Mietspiegel class values (continuous) to €/m² via linear interpolation.
    Clips values outside the anchor range to min/max.
    """
    xs, ys = zip(*sorted(anchors.items()))
    xs_arr = np.array(xs, dtype=float)
    ys_arr = np.array(ys, dtype=float)

    v = np.asarray(values, dtype=float)
    v = np.clip(v, xs_arr.min(), xs_arr.max())
    return np.interp(v, xs_arr, ys_arr)

# Add affordability metrics (rent/m², estimated rent, rent-to-income, label)
def add_affordability(
    df: pd.DataFrame,
    *,
    monthly_income_eur: float,
    size_m2: int = 60,
    threshold: float = 0.30,
    mietspiegel_col: str = "subdistrict_avg_mietspiegel_classification",
    income_col: str = "subdistrict_avg_median_income_eur",
    out_prefix: str = "aff_",
) -> pd.DataFrame:
    """
    Adds rule-based affordability columns:
      aff_rent_per_m2, aff_est_monthly_rent, aff_rent_to_income, aff_label
    """
    if mietspiegel_col not in df.columns:
        raise KeyError(f"Column '{mietspiegel_col}' not found.")
    if income_col not in df.columns:
        raise KeyError(f"Column '{income_col}' not found.")

    out = df.copy()

    rent_per_m2 = pd.Series(
        class_to_eur_interpolated(out[mietspiegel_col].values),
        index=out.index
    )

    out[f"{out_prefix}rent_per_m2"] = rent_per_m2
    out[f"{out_prefix}est_monthly_rent"] = rent_per_m2 * float(size_m2)
    out[f"{out_prefix}rent_to_income"] = out[f"{out_prefix}est_monthly_rent"] / out[income_col]
    out[f"{out_prefix}label"] = out[f"{out_prefix}rent_to_income"] <= float(threshold)

    return out