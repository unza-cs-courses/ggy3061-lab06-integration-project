#!/usr/bin/env python3
"""
Pytest configuration for Lab 6: Hidden Tests
GGY3061 - Introduction to Programming for Geologists

Provides fixtures for hidden tests that verify correctness against
the actual prospect data and student-specific variant parameters.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import json

# Add src directory to path for imports
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def prospect_data_path():
    """Provide path to the prospect data CSV file."""
    return Path(__file__).parent.parent.parent / "data" / "prospect_data.csv"


@pytest.fixture
def prospect_dataframe(prospect_data_path):
    """Load the actual prospect data for testing."""
    if prospect_data_path.exists():
        return pd.read_csv(prospect_data_path)
    else:
        pytest.skip("prospect_data.csv not found")


@pytest.fixture
def prospect_csv_file(prospect_data_path):
    """Provide the prospect data CSV path as a string."""
    if prospect_data_path.exists():
        return str(prospect_data_path)
    else:
        pytest.skip("prospect_data.csv not found")


@pytest.fixture
def variant_config():
    """Load the student's variant configuration."""
    # Try loading from pre-generated config first (created by CI workflow)
    config_path = Path(__file__).parent.parent.parent / ".variant_config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)

    # Fall back to generating from get_variant.py
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "get_variant",
        str(Path(__file__).parent.parent.parent / "scripts" / "get_variant.py")
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.get_my_variant()


@pytest.fixture
def alternative_dataframe():
    """Provide alternative test data to catch hardcoded return values."""
    np.random.seed(99)
    n = 30
    return pd.DataFrame({
        'sample_id': [f'ALT-{i:03d}' for i in range(1, n + 1)],
        'hole_id': np.random.choice(['XH-01', 'XH-02', 'XH-03'], n),
        'from_depth': np.random.uniform(20, 500, n).round(1),
        'to_depth': np.random.uniform(22, 502, n).round(1),
        'lithology': np.random.choice(['Marble', 'Slate', 'Quartzite'], n),
        'grade': np.round(np.random.uniform(0.5, 7.0, n), 2),
        'mass': np.round(np.random.uniform(8, 25, n), 1),
        'volume': np.round(np.random.uniform(3.0, 9.0, n), 1),
    })


@pytest.fixture
def dataframe_with_nulls():
    """Provide a DataFrame with missing values for hidden testing."""
    return pd.DataFrame({
        'sample_id': [f'NULL-{i:03d}' for i in range(1, 11)],
        'hole_id': ['DH-01', 'DH-01', 'DH-02', 'DH-02', 'DH-03',
                     'DH-03', 'DH-01', 'DH-02', 'DH-03', 'DH-01'],
        'from_depth': [10.0, 20.0, None, 40.0, 50.0, 60.0, 70.0, None, 90.0, 100.0],
        'to_depth': [12.0, 22.0, 32.0, 42.0, None, 62.0, 72.0, 82.0, 92.0, 102.0],
        'lithology': ['Granite', 'Basalt', None, 'Schist', 'Basalt',
                       None, 'Granite', 'Schist', 'Quartzite', 'Basalt'],
        'grade': [2.5, None, 3.2, 0.9, 4.1, 1.8, None, 2.7, 3.5, 1.2],
        'mass': [12.5, 15.3, 10.8, None, 14.1, 11.2, 16.0, None, 13.5, 12.0],
        'volume': [5.0, 6.0, 4.5, 5.5, None, 4.8, 6.5, 5.2, 5.0, 4.8],
    })


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for testing."""
    output_dir = tmp_path / 'hidden_output'
    output_dir.mkdir()
    return str(output_dir)


# Cleanup matplotlib figures after tests
@pytest.fixture(autouse=True)
def cleanup_plots():
    """Clean up matplotlib figures after each test."""
    import matplotlib.pyplot as plt
    yield
    plt.close('all')
