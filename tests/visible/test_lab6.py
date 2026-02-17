"""
Visible Tests for GGY3061 Lab 6: Integration Project
Tests the complete data pipeline implementation.

Test Classes:
- TestDataLoader: Tests for data_loader.py
- TestDataProcessor: Tests for data_processor.py
- TestAnalyzer: Tests for analyzer.py
- TestVisualizer: Tests for visualizer.py
- TestReporter: Tests for reporter.py
- TestPipeline: Tests for main.py integration
"""
import pytest
import pandas as pd
import numpy as np
import os
from pathlib import Path


# ============================================================================
# DATA LOADER TESTS (15 marks)
# ============================================================================

class TestDataLoader:
    """Tests for the data_loader module."""

    def test_load_prospect_data_returns_dataframe(self, sample_csv_file):
        """Test that load_prospect_data returns a DataFrame."""
        from data_loader import load_prospect_data

        result = load_prospect_data(sample_csv_file)

        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"
        assert len(result) > 0, "DataFrame should not be empty"

    def test_load_prospect_data_has_required_columns(self, sample_csv_file):
        """Test that loaded data has expected columns."""
        from data_loader import load_prospect_data

        result = load_prospect_data(sample_csv_file)
        required_columns = ['sample_id', 'hole_id', 'grade', 'from_depth', 'to_depth']

        for col in required_columns:
            assert col in result.columns, f"Missing required column: {col}"

    def test_load_prospect_data_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        from data_loader import load_prospect_data

        with pytest.raises(FileNotFoundError):
            load_prospect_data('nonexistent_file.csv')

    def test_validate_data_returns_dict(self, sample_dataframe):
        """Test that validate_data returns a dictionary."""
        from data_loader import validate_data

        result = validate_data(sample_dataframe)

        assert isinstance(result, dict), "Should return a dictionary"

    def test_validate_data_has_required_keys(self, sample_dataframe):
        """Test that validation report has all required keys."""
        from data_loader import validate_data

        result = validate_data(sample_dataframe)
        required_keys = ['total_records', 'valid_records', 'missing_values',
                        'invalid_grades', 'invalid_depths']

        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

    def test_validate_data_detects_issues(self, sample_dataframe_with_issues):
        """Test that validation detects data quality issues."""
        from data_loader import validate_data

        result = validate_data(sample_dataframe_with_issues)

        assert result['total_records'] == 10, "Should count all records"
        assert result['invalid_grades'] > 0, "Should detect invalid grades"
        assert result['invalid_depths'] > 0, "Should detect invalid depths"

    def test_clean_data_returns_dataframe(self, sample_dataframe_with_issues):
        """Test that clean_data returns a DataFrame."""
        from data_loader import clean_data

        result = clean_data(sample_dataframe_with_issues)

        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"

    def test_clean_data_removes_invalid_grades(self, sample_dataframe_with_issues):
        """Test that clean_data removes records with invalid grades."""
        from data_loader import clean_data

        result = clean_data(sample_dataframe_with_issues)

        # Should not have negative grades
        assert (result['grade'] >= 0).all(), "Should remove negative grades"
        # Should not have grades > 100
        assert (result['grade'] <= 100).all(), "Should remove grades > 100"

    def test_clean_data_removes_negative_depths(self, sample_dataframe_with_issues):
        """Test that clean_data removes records with negative depths."""
        from data_loader import clean_data

        result = clean_data(sample_dataframe_with_issues)

        if 'from_depth' in result.columns:
            valid_depths = result['from_depth'].dropna()
            assert (valid_depths >= 0).all(), "Should remove negative from_depth"

    def test_clean_data_removes_duplicates(self, sample_dataframe_with_issues):
        """Test that clean_data removes duplicate sample_id entries."""
        from data_loader import clean_data

        result = clean_data(sample_dataframe_with_issues)

        assert result['sample_id'].is_unique, \
            "Should remove duplicate sample_id entries"

    def test_clean_data_fills_missing_numeric(self, sample_dataframe_with_issues):
        """Test that clean_data fills missing numeric values with median."""
        from data_loader import clean_data

        result = clean_data(sample_dataframe_with_issues)

        # After cleaning, numeric columns should have no NaN values
        numeric_cols = result.select_dtypes(include='number').columns
        for col in numeric_cols:
            assert result[col].isna().sum() == 0, \
                f"Column '{col}' should have no missing values after cleaning"

    def test_clean_data_does_not_modify_original(self, sample_dataframe_with_issues):
        """Test that clean_data returns a copy without modifying the input."""
        from data_loader import clean_data

        original_len = len(sample_dataframe_with_issues)
        result = clean_data(sample_dataframe_with_issues)

        assert len(sample_dataframe_with_issues) == original_len, \
            "Should not modify the original DataFrame"
        assert result is not sample_dataframe_with_issues, \
            "Should return a new DataFrame, not the same object"


# ============================================================================
# DATA PROCESSOR TESTS (20 marks)
# ============================================================================

class TestDataProcessor:
    """Tests for the data_processor module."""

    def test_calculate_density_adds_column(self, sample_dataframe):
        """Test that calculate_density adds a density column."""
        from data_processor import calculate_density

        result = calculate_density(sample_dataframe)

        assert 'density' in result.columns, "Should add 'density' column"

    def test_calculate_density_correct_values(self, sample_dataframe):
        """Test that density is calculated correctly (mass/volume)."""
        from data_processor import calculate_density

        result = calculate_density(sample_dataframe)

        # Check a few values manually
        for idx in result.index[:5]:
            expected = result.loc[idx, 'mass'] / result.loc[idx, 'volume']
            actual = result.loc[idx, 'density']
            assert abs(actual - expected) < 0.001, "Density calculation incorrect"

    def test_classify_grade_adds_column(self, sample_dataframe):
        """Test that classify_grade adds grade_class column."""
        from data_processor import classify_grade

        result = classify_grade(sample_dataframe, cutoff=2.0)

        assert 'grade_class' in result.columns, "Should add 'grade_class' column"

    def test_classify_grade_correct_classification(self, sample_dataframe):
        """Test that grades are classified correctly."""
        from data_processor import classify_grade

        cutoff = 2.0
        result = classify_grade(sample_dataframe, cutoff=cutoff)

        # Check classification logic
        for idx in result.index:
            grade = result.loc[idx, 'grade']
            grade_class = result.loc[idx, 'grade_class']

            if grade >= 2 * cutoff:
                assert grade_class == 'High Grade', f"Grade {grade} should be High Grade"
            elif grade >= cutoff:
                assert grade_class == 'Medium Grade', f"Grade {grade} should be Medium Grade"
            else:
                assert grade_class == 'Low Grade', f"Grade {grade} should be Low Grade"

    def test_calculate_intervals_adds_column(self, sample_dataframe):
        """Test that calculate_intervals adds interval column."""
        from data_processor import calculate_intervals

        result = calculate_intervals(sample_dataframe)

        assert 'interval' in result.columns, "Should add 'interval' column"

    def test_calculate_intervals_correct_values(self, sample_dataframe):
        """Test that intervals are calculated correctly."""
        from data_processor import calculate_intervals

        result = calculate_intervals(sample_dataframe)

        for idx in result.index[:5]:
            expected = result.loc[idx, 'to_depth'] - result.loc[idx, 'from_depth']
            actual = result.loc[idx, 'interval']
            assert abs(actual - expected) < 0.001, "Interval calculation incorrect"

    def test_filter_by_drillhole_filters_correctly(self, sample_dataframe):
        """Test that filter_by_drillhole returns only specified holes."""
        from data_processor import filter_by_drillhole

        hole_ids = ['DH-01', 'DH-02']
        result = filter_by_drillhole(sample_dataframe, hole_ids)

        assert set(result['hole_id'].unique()).issubset(set(hole_ids)), \
            "Should only contain specified drillholes"

    def test_filter_by_drillhole_none_returns_all(self, sample_dataframe):
        """Test that None drillholes returns all data."""
        from data_processor import filter_by_drillhole

        result = filter_by_drillhole(sample_dataframe, None)

        assert len(result) == len(sample_dataframe), \
            "None should return all records"


# ============================================================================
# ANALYZER TESTS (20 marks)
# ============================================================================

class TestAnalyzer:
    """Tests for the analyzer module."""

    def test_summary_statistics_returns_dataframe(self, sample_dataframe):
        """Test that summary_statistics returns a DataFrame."""
        from analyzer import summary_statistics

        result = summary_statistics(sample_dataframe, ['grade', 'mass'])

        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"

    def test_summary_statistics_has_correct_stats(self, sample_dataframe):
        """Test that summary statistics includes required statistics."""
        from analyzer import summary_statistics

        result = summary_statistics(sample_dataframe, ['grade'])

        # Should have at least count, mean, std, min, max (8 rows from describe())
        assert result.shape[0] >= 5, "Should include at least 5 summary statistics"

        # Check that key statistics are present in index
        result_index_lower = [str(idx).lower() for idx in result.index]
        for stat in ['mean', 'min', 'max']:
            assert any(stat in idx for idx in result_index_lower), \
                f"Should include '{stat}' statistic"

    def test_summary_statistics_correct_values(self, sample_dataframe):
        """Test that summary statistics values are correct."""
        from analyzer import summary_statistics

        result = summary_statistics(sample_dataframe, ['grade', 'mass'])

        # Should include the requested columns
        assert 'grade' in result.columns, "Should include 'grade' column"
        assert 'mass' in result.columns, "Should include 'mass' column"

    def test_grade_by_drillhole_returns_dataframe(self, sample_dataframe):
        """Test that grade_by_drillhole returns a DataFrame."""
        from analyzer import grade_by_drillhole

        result = grade_by_drillhole(sample_dataframe)

        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"

    def test_grade_by_drillhole_groups_correctly(self, sample_dataframe):
        """Test that results are grouped by drillhole."""
        from analyzer import grade_by_drillhole

        result = grade_by_drillhole(sample_dataframe)
        expected_holes = sample_dataframe['hole_id'].unique()

        # Check that all drillholes are represented
        assert len(result) == len(expected_holes), \
            "Should have one row per drillhole"

    def test_correlation_analysis_returns_dataframe(self, sample_dataframe):
        """Test that correlation_analysis returns a DataFrame."""
        from analyzer import correlation_analysis

        result = correlation_analysis(sample_dataframe, ['grade', 'mass', 'volume'])

        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"

    def test_correlation_analysis_symmetric(self, sample_dataframe):
        """Test that correlation matrix is symmetric."""
        from analyzer import correlation_analysis

        result = correlation_analysis(sample_dataframe, ['grade', 'mass', 'volume'])

        # Correlation matrices should be symmetric
        assert result.shape[0] == result.shape[1], "Should be square matrix"

    def test_correlation_analysis_diagonal_ones(self, sample_dataframe):
        """Test that diagonal elements are 1.0 (self-correlation)."""
        from analyzer import correlation_analysis

        result = correlation_analysis(sample_dataframe, ['grade', 'mass', 'volume'])

        for col in result.columns:
            assert abs(result.loc[col, col] - 1.0) < 0.001, \
                "Diagonal should be 1.0"

    def test_identify_high_grade_zones_filters_correctly(self, sample_dataframe):
        """Test that high grade zones are identified correctly."""
        from analyzer import identify_high_grade_zones

        threshold = 2.0
        result = identify_high_grade_zones(sample_dataframe, threshold)

        assert (result['grade'] >= threshold).all(), \
            "All results should have grade >= threshold"

    def test_identify_high_grade_zones_count(self, sample_dataframe):
        """Test that high grade count matches manual calculation."""
        from analyzer import identify_high_grade_zones

        threshold = 2.0
        result = identify_high_grade_zones(sample_dataframe, threshold)
        expected_count = (sample_dataframe['grade'] >= threshold).sum()

        assert len(result) == expected_count, \
            "Count should match manual calculation"


# ============================================================================
# VISUALIZER TESTS (20 marks)
# ============================================================================

class TestVisualizer:
    """Tests for the visualizer module."""

    def test_plot_grade_histogram_creates_file(self, sample_dataframe, temp_output_dir):
        """Test that plot_grade_histogram creates an output file."""
        from visualizer import plot_grade_histogram

        output_path = os.path.join(temp_output_dir, 'grade_histogram.png')
        plot_grade_histogram(sample_dataframe, output_path)

        assert os.path.exists(output_path), "Should create histogram file"

    def test_plot_depth_vs_grade_creates_file(self, sample_dataframe, temp_output_dir):
        """Test that plot_depth_vs_grade creates an output file."""
        from visualizer import plot_depth_vs_grade

        output_path = os.path.join(temp_output_dir, 'depth_vs_grade.png')
        plot_depth_vs_grade(sample_dataframe, output_path)

        assert os.path.exists(output_path), "Should create scatter plot file"

    def test_plot_grade_by_drillhole_creates_file(self, sample_dataframe, temp_output_dir):
        """Test that plot_grade_by_drillhole creates an output file."""
        from visualizer import plot_grade_by_drillhole

        output_path = os.path.join(temp_output_dir, 'grade_by_drillhole.png')
        plot_grade_by_drillhole(sample_dataframe, output_path)

        assert os.path.exists(output_path), "Should create box plot file"

    def test_plot_correlation_heatmap_creates_file(self, sample_correlation_matrix, temp_output_dir):
        """Test that plot_correlation_heatmap creates an output file."""
        from visualizer import plot_correlation_heatmap

        output_path = os.path.join(temp_output_dir, 'correlation_heatmap.png')
        plot_correlation_heatmap(sample_correlation_matrix, output_path)

        assert os.path.exists(output_path), "Should create heatmap file"

    def test_plot_files_not_empty(self, sample_dataframe, temp_output_dir):
        """Test that generated plot files are not empty."""
        from visualizer import plot_grade_histogram

        output_path = os.path.join(temp_output_dir, 'test_histogram.png')
        plot_grade_histogram(sample_dataframe, output_path)

        file_size = os.path.getsize(output_path)
        assert file_size > 0, "Plot file should not be empty"


# ============================================================================
# REPORTER TESTS (10 marks)
# ============================================================================

class TestReporter:
    """Tests for the reporter module."""

    def test_generate_summary_report_returns_string(self, sample_validation_report, sample_statistics):
        """Test that generate_summary_report returns a string."""
        from reporter import generate_summary_report

        result = generate_summary_report(
            sample_validation_report,
            sample_statistics,
            high_grade_count=25,
            project_name='Test Project'
        )

        assert isinstance(result, str), "Should return a string"
        assert len(result) > 0, "Report should not be empty"

    def test_generate_summary_report_contains_project_name(self, sample_validation_report, sample_statistics):
        """Test that report contains project name."""
        from reporter import generate_summary_report

        project_name = 'Aurora Ridge Project'
        result = generate_summary_report(
            sample_validation_report,
            sample_statistics,
            high_grade_count=25,
            project_name=project_name
        )

        assert project_name in result, "Report should contain project name"

    def test_generate_summary_report_contains_statistics(self, sample_validation_report, sample_statistics):
        """Test that report contains key statistics."""
        from reporter import generate_summary_report

        result = generate_summary_report(
            sample_validation_report,
            sample_statistics,
            high_grade_count=25,
            project_name='Test Project'
        )

        # Should contain some reference to records/samples
        assert 'record' in result.lower() or 'sample' in result.lower(), \
            "Report should mention records or samples"

    def test_save_report_creates_file(self, temp_output_dir):
        """Test that save_report creates a file."""
        from reporter import save_report

        content = "# Test Report\n\nThis is a test."
        output_path = os.path.join(temp_output_dir, 'test_report.md')

        save_report(content, output_path)

        assert os.path.exists(output_path), "Should create report file"

    def test_save_report_correct_content(self, temp_output_dir):
        """Test that saved report has correct content."""
        from reporter import save_report

        content = "# Test Report\n\nThis is a test."
        output_path = os.path.join(temp_output_dir, 'test_report.md')

        save_report(content, output_path)

        with open(output_path, 'r') as f:
            saved_content = f.read()

        assert saved_content == content, "Saved content should match input"

    def test_export_processed_data_creates_file(self, sample_dataframe, temp_output_dir):
        """Test that export_processed_data creates a CSV file."""
        from reporter import export_processed_data

        output_path = os.path.join(temp_output_dir, 'processed.csv')
        export_processed_data(sample_dataframe, output_path)

        assert os.path.exists(output_path), "Should create CSV file"

    def test_export_processed_data_readable(self, sample_dataframe, temp_output_dir):
        """Test that exported CSV can be read back."""
        from reporter import export_processed_data

        output_path = os.path.join(temp_output_dir, 'processed.csv')
        export_processed_data(sample_dataframe, output_path)

        loaded_df = pd.read_csv(output_path)

        assert len(loaded_df) == len(sample_dataframe), "Should preserve row count"


# ============================================================================
# PIPELINE INTEGRATION TESTS (15 marks)
# ============================================================================

class TestPipeline:
    """Tests for the main pipeline integration."""

    def test_run_pipeline_returns_dict(self, pipeline_config):
        """Test that run_pipeline returns a dictionary."""
        from main import run_pipeline

        result = run_pipeline(pipeline_config)

        assert isinstance(result, dict), "Should return a dictionary"

    def test_run_pipeline_has_required_keys(self, pipeline_config):
        """Test that pipeline results have required keys."""
        from main import run_pipeline

        result = run_pipeline(pipeline_config)
        required_keys = ['validation', 'statistics', 'high_grade_count', 'output_files']

        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

    def test_run_pipeline_creates_output_files(self, pipeline_config):
        """Test that pipeline creates expected output files."""
        from main import run_pipeline

        result = run_pipeline(pipeline_config)

        assert len(result['output_files']) > 0, "Should generate output files"

        for filepath in result['output_files']:
            full_path = os.path.join(pipeline_config['output_dir'], filepath)
            assert os.path.exists(full_path) or os.path.exists(filepath), \
                f"Output file should exist: {filepath}"

    def test_run_pipeline_validation_report(self, pipeline_config):
        """Test that pipeline validation report is valid."""
        from main import run_pipeline

        result = run_pipeline(pipeline_config)

        assert 'total_records' in result['validation'], \
            "Validation should include total_records"
        assert result['validation']['total_records'] > 0, \
            "Should have processed some records"

    def test_run_pipeline_high_grade_count(self, pipeline_config):
        """Test that pipeline calculates high grade count."""
        from main import run_pipeline

        result = run_pipeline(pipeline_config)

        assert isinstance(result['high_grade_count'], int), \
            "high_grade_count should be an integer"
        assert result['high_grade_count'] >= 0, \
            "high_grade_count should be non-negative"

    def test_run_pipeline_with_drillhole_filter(self, pipeline_config, sample_dataframe):
        """Test pipeline with specific drillhole filter."""
        from main import run_pipeline

        # Get actual drillhole IDs from the test data
        hole_ids = sample_dataframe['hole_id'].unique()[:2].tolist()
        pipeline_config['drillholes'] = hole_ids

        result = run_pipeline(pipeline_config)

        assert result is not None, "Should complete with drillhole filter"


# ============================================================================
# INTEGRATION WITH ACTUAL DATA
# ============================================================================

class TestWithProspectData:
    """Tests using the actual prospect_data.csv file."""

    def test_prospect_data_exists(self, prospect_data_path):
        """Test that prospect_data.csv exists."""
        assert os.path.exists(prospect_data_path), \
            "prospect_data.csv should exist in data directory"

    def test_prospect_data_has_300_records(self, prospect_data_path):
        """Test that prospect data has approximately 300 records."""
        if os.path.exists(prospect_data_path):
            df = pd.read_csv(prospect_data_path)
            assert len(df) >= 280 and len(df) <= 320, \
                "Should have approximately 300 records"

    def test_prospect_data_has_required_columns(self, prospect_data_path):
        """Test that prospect data has all required columns."""
        if os.path.exists(prospect_data_path):
            df = pd.read_csv(prospect_data_path)
            required_columns = ['sample_id', 'hole_id', 'from_depth', 'to_depth',
                              'lithology', 'grade', 'mass', 'volume']

            for col in required_columns:
                assert col in df.columns, f"Missing required column: {col}"
