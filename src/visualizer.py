"""
Visualizer Module for GGY3061 Lab 6: Integration Project
Creates charts, plots, and visualizations for geological data analysis.

This module provides functions to:
- Create histograms of grade distributions
- Plot depth vs grade relationships
- Generate box plots by drillhole
- Create correlation heatmaps
"""
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, Tuple


def plot_grade_histogram(
    df: pd.DataFrame,
    output_path: str,
    bins: int = 30,
    figsize: Tuple[int, int] = (10, 6)
) -> None:
    """
    Create histogram of grade distribution and save to file.

    Creates a histogram showing the frequency distribution of grade values,
    which helps identify the overall grade profile of the prospect.

    Args:
        df: DataFrame with 'grade' column
        output_path: Path to save the figure (e.g., 'output/grade_histogram.png')
        bins: Number of histogram bins (default: 30)
        figsize: Figure size as (width, height) in inches

    Returns:
        None (saves figure to file)

    Example:
        >>> plot_grade_histogram(df, 'output/grade_histogram.png')
        # Creates and saves histogram plot
    """
    # TODO: Implement histogram plotting
    # Hint: Use plt.figure(), plt.hist(), plt.xlabel(), plt.ylabel(), plt.title()
    # Hint: Use plt.savefig(output_path) and plt.close()
    pass


def plot_depth_vs_grade(
    df: pd.DataFrame,
    output_path: str,
    figsize: Tuple[int, int] = (10, 8)
) -> None:
    """
    Create scatter plot of depth vs grade and save to file.

    Visualizes the relationship between sample depth and grade,
    which can reveal depth-related mineralization trends.

    Args:
        df: DataFrame with 'from_depth' and 'grade' columns
        output_path: Path to save the figure
        figsize: Figure size as (width, height) in inches

    Returns:
        None (saves figure to file)

    Note:
        Y-axis is inverted so that depth increases downward,
        following geological convention.

    Example:
        >>> plot_depth_vs_grade(df, 'output/depth_vs_grade.png')
    """
    # TODO: Implement scatter plot
    # Hint: Use plt.scatter()
    # Hint: Use plt.gca().invert_yaxis() to flip depth axis
    pass


def plot_grade_by_drillhole(
    df: pd.DataFrame,
    output_path: str,
    figsize: Tuple[int, int] = (12, 6)
) -> None:
    """
    Create box plot of grade by drillhole and save to file.

    Shows the distribution of grades for each drillhole, making it easy
    to compare variability and identify high-grade holes.

    Args:
        df: DataFrame with 'hole_id' and 'grade' columns
        output_path: Path to save the figure
        figsize: Figure size as (width, height) in inches

    Returns:
        None (saves figure to file)

    Example:
        >>> plot_grade_by_drillhole(df, 'output/grade_by_drillhole.png')
    """
    # TODO: Implement box plot
    # Hint: Use df.boxplot() or plt.boxplot()
    # Hint: Group data by 'hole_id' first
    pass


def plot_correlation_heatmap(
    corr_matrix: pd.DataFrame,
    output_path: str,
    figsize: Tuple[int, int] = (10, 8)
) -> None:
    """
    Create correlation heatmap and save to file.

    Visualizes the correlation matrix as a color-coded heatmap,
    making it easy to identify relationships between variables.

    Args:
        corr_matrix: Correlation matrix DataFrame (from correlation_analysis)
        output_path: Path to save the figure
        figsize: Figure size as (width, height) in inches

    Returns:
        None (saves figure to file)

    Example:
        >>> corr = correlation_analysis(df, ['grade', 'depth', 'density'])
        >>> plot_correlation_heatmap(corr, 'output/correlation_heatmap.png')
    """
    # TODO: Implement heatmap
    # Hint: Use plt.imshow() or plt.matshow() with corr_matrix.values
    # Hint: Add colorbar with plt.colorbar()
    # Hint: Add axis labels with column names
    pass


def plot_grade_profile(
    df: pd.DataFrame,
    hole_id: str,
    output_path: str,
    figsize: Tuple[int, int] = (8, 12)
) -> None:
    """
    Create a downhole grade profile for a specific drillhole.

    Shows how grade varies with depth for a single drillhole,
    useful for identifying mineralized intervals.

    Args:
        df: DataFrame with 'hole_id', 'from_depth', 'to_depth', and 'grade' columns
        hole_id: Drillhole ID to plot (e.g., 'DH-01')
        output_path: Path to save the figure
        figsize: Figure size as (width, height) in inches

    Returns:
        None (saves figure to file)

    Example:
        >>> plot_grade_profile(df, 'DH-01', 'output/DH01_profile.png')
    """
    # TODO: Implement grade profile plot
    # This is an optional helper function
    pass


def plot_lithology_grades(
    df: pd.DataFrame,
    output_path: str,
    figsize: Tuple[int, int] = (12, 6)
) -> None:
    """
    Create box plot of grades by lithology type.

    Args:
        df: DataFrame with 'lithology' and 'grade' columns
        output_path: Path to save the figure
        figsize: Figure size as (width, height) in inches

    Returns:
        None (saves figure to file)

    Example:
        >>> plot_lithology_grades(df, 'output/lithology_grades.png')
    """
    # TODO: Implement lithology box plot
    # This is an optional helper function
    pass


def create_summary_dashboard(
    df: pd.DataFrame,
    output_path: str,
    figsize: Tuple[int, int] = (16, 12)
) -> None:
    """
    Create a multi-panel dashboard with key visualizations.

    Creates a 2x2 grid with:
    - Grade histogram
    - Depth vs grade scatter
    - Grade by drillhole box plot
    - Grade by lithology box plot

    Args:
        df: DataFrame with required columns
        output_path: Path to save the figure
        figsize: Figure size as (width, height) in inches

    Returns:
        None (saves figure to file)

    Example:
        >>> create_summary_dashboard(df, 'output/dashboard.png')
    """
    # TODO: Implement dashboard
    # Hint: Use plt.subplots(2, 2, figsize=figsize)
    # This is an optional helper function
    pass
