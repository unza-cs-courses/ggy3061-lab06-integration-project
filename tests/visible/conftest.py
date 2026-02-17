"""
Pytest Configuration for GGY3061 Lab 6: Integration Project
Provides fixtures and configuration for testing the complete pipeline.
"""
import pytest
import pandas as pd
import numpy as np
import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))


@pytest.fixture
def sample_dataframe():
    """Create a sample DataFrame for testing."""
    np.random.seed(42)
    n_samples = 50

    data = {
        'sample_id': [f'GEO-{i:04d}' for i in range(1, n_samples + 1)],
        'hole_id': np.random.choice(['DH-01', 'DH-02', 'DH-03', 'DH-04'], n_samples),
        'from_depth': np.random.uniform(10, 400, n_samples).round(1),
        'to_depth': None,  # Will be calculated
        'lithology': np.random.choice(['Granite', 'Schist', 'Quartzite', 'Basalt'], n_samples),
        'grade': np.random.uniform(0.1, 6.0, n_samples).round(2),
        'mass': np.random.uniform(8.0, 20.0, n_samples).round(1),
        'volume': np.random.uniform(3.0, 8.0, n_samples).round(1),
    }

    df = pd.DataFrame(data)
    # Calculate to_depth as from_depth + random interval
    df['to_depth'] = df['from_depth'] + np.random.uniform(0.5, 2.5, n_samples).round(1)

    return df


@pytest.fixture
def sample_dataframe_with_issues():
    """Create a DataFrame with data quality issues for validation testing."""
    data = {
        'sample_id': ['GEO-001', 'GEO-002', 'GEO-003', 'GEO-004', 'GEO-005',
                      'GEO-006', 'GEO-007', 'GEO-008', 'GEO-001', 'GEO-010'],  # Duplicate ID
        'hole_id': ['DH-01', 'DH-01', 'DH-02', 'DH-02', 'DH-03',
                    'DH-03', 'DH-04', 'DH-04', 'DH-01', 'DH-05'],
        'from_depth': [10.0, 15.5, -5.0, 25.0, 30.0,  # Negative depth
                       35.0, None, 45.0, 50.0, 55.0],  # Missing value
        'to_depth': [12.0, 17.5, -3.0, 27.0, 32.0,
                     37.0, 42.5, 47.0, 52.0, 57.0],
        'lithology': ['Granite', 'Schist', 'Quartzite', 'Basalt', 'Granite',
                      None, 'Schist', 'Quartzite', 'Basalt', 'Granite'],  # Missing
        'grade': [2.5, -0.5, 3.2, None, 4.1,  # Negative and missing
                  1.8, 150.0, 2.9, 3.5, 0.8],  # Invalid > 100
        'mass': [12.5, 15.0, 11.0, 14.5, 13.0,
                 None, 16.0, 12.0, 15.5, 14.0],  # Missing
        'volume': [5.0, 6.0, 4.5, 5.5, 5.2,
                   4.8, 6.5, 4.8, 6.0, 5.5],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_csv_file(sample_dataframe, tmp_path):
    """Create a temporary CSV file for testing."""
    csv_path = tmp_path / 'test_data.csv'
    sample_dataframe.to_csv(csv_path, index=False)
    return str(csv_path)


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create a temporary output directory for testing."""
    output_dir = tmp_path / 'output'
    output_dir.mkdir()
    return str(output_dir)


@pytest.fixture
def sample_statistics():
    """Create sample statistics DataFrame for testing."""
    data = {
        'grade': [50, 2.15, 1.85, 0.12, 1.20, 2.05, 2.95, 8.45],
        'depth': [50, 225.5, 85.2, 10.5, 95.0, 220.0, 350.0, 450.0],
        'mass': [50, 15.25, 3.12, 8.0, 12.5, 15.0, 18.0, 20.0],
    }
    stats = pd.DataFrame(
        data,
        index=['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
    )
    return stats


@pytest.fixture
def sample_correlation_matrix():
    """Create sample correlation matrix for testing."""
    columns = ['grade', 'depth', 'mass', 'volume', 'density']
    data = np.array([
        [1.00, -0.25, 0.15, 0.10, 0.05],
        [-0.25, 1.00, 0.08, 0.12, -0.03],
        [0.15, 0.08, 1.00, 0.65, 0.85],
        [0.10, 0.12, 0.65, 1.00, -0.45],
        [0.05, -0.03, 0.85, -0.45, 1.00],
    ])
    return pd.DataFrame(data, index=columns, columns=columns)


@pytest.fixture
def sample_validation_report():
    """Create sample validation report for testing."""
    return {
        'total_records': 100,
        'valid_records': 92,
        'missing_values': {'grade': 2, 'mass': 3, 'lithology': 1},
        'invalid_grades': 3,
        'invalid_depths': 2
    }


@pytest.fixture
def pipeline_config(sample_csv_file, temp_output_dir):
    """Create sample pipeline configuration for testing."""
    return {
        'input_file': sample_csv_file,
        'output_dir': temp_output_dir,
        'project_name': 'Test Project',
        'target_grade': 2.0,
        'drillholes': None
    }


@pytest.fixture
def prospect_data_path():
    """Return path to the actual prospect_data.csv file."""
    return str(Path(__file__).parent.parent.parent / 'data' / 'prospect_data.csv')


# Cleanup matplotlib figures after tests
@pytest.fixture(autouse=True)
def cleanup_plots():
    """Clean up matplotlib figures after each test."""
    import matplotlib.pyplot as plt
    yield
    plt.close('all')
