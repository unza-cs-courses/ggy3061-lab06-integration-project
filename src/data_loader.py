"""
Data Loader Module for GGY3061 Lab 6: Integration Project
Handles CSV loading, data validation, and cleaning operations.

This module provides functions to:
- Load geological prospect data from CSV files
- Validate data quality and identify issues
- Clean data by removing invalid records and handling missing values
"""
import pandas as pd
from typing import Dict, Any


def load_prospect_data(filepath: str) -> pd.DataFrame:
    """
    Load CSV data and return a DataFrame.

    Args:
        filepath: Path to the CSV file containing prospect data

    Returns:
        DataFrame containing the raw geological data

    Raises:
        FileNotFoundError: If the specified file does not exist
        pd.errors.EmptyDataError: If the file is empty

    Example:
        >>> df = load_prospect_data('data/prospect_data.csv')
        >>> print(df.shape)
        (300, 10)
    """
    # TODO: Implement this function
    # Hint: Use pd.read_csv() to load the data
    pass


def validate_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate data quality and return a validation report.

    Performs the following validation checks:
    1. Count total records
    2. Identify missing values per column
    3. Check for invalid grade values (negative or > 100)
    4. Check for invalid depth values (negative)
    5. Calculate valid record count

    Args:
        df: DataFrame to validate

    Returns:
        Dictionary containing validation results:
        - 'total_records': int - total number of records in dataset
        - 'valid_records': int - records passing all validation checks
        - 'missing_values': dict - column name -> count of missing values
        - 'invalid_grades': int - count of records with invalid grades
        - 'invalid_depths': int - count of records with invalid depths

    Example:
        >>> report = validate_data(df)
        >>> print(f"Total: {report['total_records']}, Valid: {report['valid_records']}")
        Total: 300, Valid: 285
    """
    # TODO: Implement validation logic
    # Hint: Use df.isnull().sum() for missing values
    # Hint: Use boolean indexing to count invalid values
    pass


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove invalid records and handle missing values.

    Cleaning operations performed:
    1. Remove rows with negative grade values
    2. Remove rows with negative depth values (from_depth or to_depth)
    3. Fill missing numeric values with column median
    4. Remove duplicate sample_id entries (keep first)

    Args:
        df: DataFrame to clean

    Returns:
        Cleaned DataFrame with invalid records removed

    Note:
        This function returns a copy and does not modify the input DataFrame.

    Example:
        >>> clean_df = clean_data(df)
        >>> print(f"Records before: {len(df)}, after: {len(clean_df)}")
        Records before: 300, after: 290
    """
    # TODO: Implement cleaning logic
    # Hint: Use df.copy() to avoid modifying the original
    # Hint: Use df.drop_duplicates() for removing duplicates
    # Hint: Use df.fillna() with df.median() for filling missing values
    pass


def get_data_summary(df: pd.DataFrame) -> str:
    """
    Generate a text summary of the DataFrame contents.

    Args:
        df: DataFrame to summarize

    Returns:
        String containing a formatted summary of the data

    Example:
        >>> print(get_data_summary(df))
        Data Summary:
        - Records: 300
        - Columns: 10
        - Drillholes: 6
        - Grade range: 0.12 - 8.45 g/t
    """
    # TODO: Implement summary generation
    # This is an optional helper function
    pass
