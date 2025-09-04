"""Visualization utilities for clustering tasks in the Berlin Housing project, including histograms, correlation heatmaps, and cluster profile plots."""

# Imports
from __future__ import annotations
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Plot a grid of histograms for selected columns
def hist_grid(df: pd.DataFrame, cols: list[str], title: str = ""):
    """
    Plot a grid of histograms for selected columns in the DataFrame.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        cols (list[str]): List of column names to plot histograms for.
        title (str): Optional title for the entire plot.

    Returns:
        None
    """
    df[cols].hist(figsize=(16, 12), bins=20)
    plt.tight_layout()
    if title: 
        plt.suptitle(title, y=1.02, fontsize=16)
    plt.show()

# Plot full correlation heatmap of numeric columns
def corr_heatmap(df: pd.DataFrame, title: str = "Correlation Matrix"):
    """
    Plot a heatmap of the correlation matrix for numeric columns in the DataFrame.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        title (str): Title for the heatmap.

    Returns:
        pd.DataFrame: The correlation matrix used for the heatmap.
    """
    corr = df.corr(numeric_only=True)
    plt.figure(figsize=(20, 16))
    sns.heatmap(corr, annot=False, cmap="coolwarm", center=0, linewidths=0.5)
    plt.title(title)
    plt.show()
    return corr

# Plot heatmap of strong correlations above a threshold
def strong_corr_heatmap(df: pd.DataFrame, threshold: float = 0.5, title: str = "Strong Correlations"):
    """
    Plot a heatmap of correlations above a specified absolute value threshold.

    Parameters:
        df (pd.DataFrame): The DataFrame containing the data.
        threshold (float): Minimum absolute correlation value to display.
        title (str): Title for the heatmap.

    Returns:
        pd.DataFrame: The masked correlation matrix showing only strong correlations.
    """
    corr = df.corr(numeric_only=True)
    strong = corr.mask(corr.abs() < threshold)
    plt.figure(figsize=(16, 12))
    sns.heatmap(strong, annot=True, fmt=".2f", cmap="coolwarm", center=0, linewidths=0.5)
    plt.title(f"{title} (|corr| > {threshold})")
    plt.show()
    return strong

# Plot normalized cluster feature profiles as grouped bar chart
def plot_scaled_profiles(
    scaled_profiles: pd.DataFrame,
    title: str = "Normalized Cluster Feature Profiles",
) -> None:
    """
    Plot normalized cluster feature profiles as a grouped bar chart.

    Parameters:
        scaled_profiles (pd.DataFrame): DataFrame with normalized feature profiles per cluster.
        title (str): Title for the plot.

    Returns:
        None
    """
    (scaled_profiles.T).plot(kind="bar", figsize=(14, 6))
    plt.title(title)
    plt.ylabel("Normalized Mean (0–1)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.legend(title="Cluster")
    plt.show()