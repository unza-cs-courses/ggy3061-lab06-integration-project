"""
Data Processor Module for GGY3061 Lab 6: Integration Project
Handles data transformations, calculations, and filtering operations.

This module provides functions to:
- Calculate derived values (density, intervals)
- Classify samples based on grade thresholds
- Filter data by various criteria
"""
import pandas as pd
from typing import List, Optional


def calculate_density(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'density' column calculated from mass/volume.

    Formula: density = mass / volume

    Args:
        df: DataFrame with 'mass' and 'volume' columns

    Returns:
        DataFrame with new 'density' column added

    Note:
        Returns a copy of the DataFrame with the new column.
        Division by zero results in NaN values.

    Example:
        >>> df = calculate_density(df)
        >>> print(df['density'].mean())
        2.65
    """
    # TODO: Implement density calculation
    # Hint: df['density'] = df['mass'] / df['volume']
    pass


def classify_grade(df: pd.DataFrame, cutoff: float) -> pd.DataFrame:
    """
    Add 'grade_class' column based on economic cutoff grade.

    Classification rules:
    - 'High Grade': grade >= 2 * cutoff (economic mineralization)
    - 'Medium Grade': cutoff <= grade < 2 * cutoff (marginal)
    - 'Low Grade': grade < cutoff (sub-economic)

    Args:
        df: DataFrame with 'grade' column
        cutoff: Economic cutoff grade threshold (e.g., 2.0 g/t)

    Returns:
        DataFrame with new 'grade_class' column

    Example:
        >>> df = classify_grade(df, cutoff=2.0)
        >>> print(df['grade_class'].value_counts())
        Low Grade       150
        Medium Grade     95
        High Grade       55
    """
    # TODO: Implement grade classification
    # Hint: Use pd.cut() or np.where() for classification
    # Hint: Consider using a function with apply() for custom logic
    pass


def calculate_intervals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'interval' column as the sample length (to_depth - from_depth).

    The interval represents the length of each sample in meters.

    Args:
        df: DataFrame with 'from_depth' and 'to_depth' columns

    Returns:
        DataFrame with new 'interval' column

    Example:
        >>> df = calculate_intervals(df)
        >>> print(f"Average interval: {df['interval'].mean():.2f} m")
        Average interval: 1.50 m
    """
    # TODO: Implement interval calculation
    # Hint: Simple subtraction of two columns
    pass


def filter_by_drillhole(df: pd.DataFrame, hole_ids: Optional[List[str]]) -> pd.DataFrame:
    """
    Filter DataFrame to include only specified drillholes.

    Args:
        df: DataFrame with 'hole_id' column
        hole_ids: List of drillhole IDs to include (e.g., ['DH-01', 'DH-02'])
                  If None, returns the original DataFrame unchanged

    Returns:
        Filtered DataFrame containing only the specified drillholes

    Example:
        >>> filtered = filter_by_drillhole(df, ['DH-01', 'DH-03'])
        >>> print(filtered['hole_id'].unique())
        ['DH-01', 'DH-03']
    """
    # TODO: Implement drillhole filtering
    # Hint: Use df[df['hole_id'].isin(hole_ids)]
    pass


def filter_by_depth_range(
    df: pd.DataFrame,
    min_depth: Optional[float] = None,
    max_depth: Optional[float] = None
) -> pd.DataFrame:
    """
    Filter DataFrame by depth range.

    Args:
        df: DataFrame with 'from_depth' column
        min_depth: Minimum depth to include (optional)
        max_depth: Maximum depth to include (optional)

    Returns:
        Filtered DataFrame within the specified depth range

    Example:
        >>> filtered = filter_by_depth_range(df, min_depth=100, max_depth=300)
        >>> print(f"Depth range: {filtered['from_depth'].min()} - {filtered['from_depth'].max()}")
    """
    # TODO: Implement depth filtering
    # This is an optional helper function
    pass


def calculate_grade_thickness(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'grade_thickness' column (grade * interval).

    Grade-thickness is a common metric in mineral resource estimation,
    representing the accumulated grade over the sample interval.

    Args:
        df: DataFrame with 'grade' and 'interval' columns

    Returns:
        DataFrame with new 'grade_thickness' column

    Note:
        Ensure calculate_intervals() has been called first.

    Example:
        >>> df = calculate_grade_thickness(df)
        >>> print(f"Total grade-thickness: {df['grade_thickness'].sum():.2f}")
    """
    # TODO: Implement grade-thickness calculation
    # This is an optional helper function
    pass
