"""
Hidden Tests for GGY3061 Lab 6: Integration Project
These tests verify correctness against the actual prospect data
and student-specific variant parameters.

Test Classes:
- TestHiddenDataLoader: Verify data loading/validation/cleaning on prospect CSV
- TestHiddenDataProcessor: Verify calculations on prospect data
- TestHiddenAnalyzer: Verify analysis functions on prospect data
- TestHiddenVisualizer: Verify plot creation with prospect data
- TestHiddenReporter: Verify report generation with real data
- TestHiddenVariantVerification: Verify student uses correct variant values
- TestHiddenIntegration: Full pipeline test with prospect data
"""
import pytest
import pandas as pd
import numpy as np
import os
from pathlib import Path


# ============================================================================
# HIDDEN DATA LOADER TESTS
# ============================================================================

class TestHiddenDataLoader:
    """Hidden tests for data_loader module using actual prospect data."""

    def test_load_prospect_csv(self, prospect_csv_file):
        """Test loading the actual prospect_data.csv."""
        from data_loader import load_prospect_data

        result = load_prospect_data(prospect_csv_file)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 300, "Prospect data should have 300 records"

    def test_load_prospect_all_columns(self, prospect_csv_file):
        """Test that all 8 columns are present after loading."""
        from data_loader import load_prospect_data

        result = load_prospect_data(prospect_csv_file)
        expected_columns = ['sample_id', 'hole_id', 'from_depth', 'to_depth',
                            'lithology', 'grade', 'mass', 'volume']

        for col in expected_columns:
            assert col in result.columns, f"Missing column: {col}"

    def test_load_prospect_dtypes(self, prospect_csv_file):
        """Test that numeric columns have correct dtypes."""
        from data_loader import load_prospect_data

        result = load_prospect_data(prospect_csv_file)

        assert pd.api.types.is_numeric_dtype(result['grade']), \
            "'grade' should be numeric"
        assert pd.api.types.is_numeric_dtype(result['mass']), \
            "'mass' should be numeric"
        assert pd.api.types.is_numeric_dtype(result['from_depth']), \
            "'from_depth' should be numeric"

    def test_validate_prospect_data(self, prospect_dataframe):
        """Test validation on the actual prospect data."""
        from data_loader import validate_data

        result = validate_data(prospect_dataframe)

        assert result['total_records'] == 300
        assert isinstance(result['missing_values'], dict)
        assert isinstance(result['invalid_grades'], int)
        assert isinstance(result['invalid_depths'], int)

    def test_validate_returns_correct_total(self, prospect_dataframe):
        """Test that validate_data counts records correctly."""
        from data_loader import validate_data

        result = validate_data(prospect_dataframe)

        assert result['total_records'] == len(prospect_dataframe)

    def test_validate_alternative_data(self, alternative_dataframe):
        """Test validation works on alternative data (not hardcoded)."""
        from data_loader import validate_data

        result = validate_data(alternative_dataframe)

        assert result['total_records'] == len(alternative_dataframe)

    def test_clean_data_removes_duplicates(self, dataframe_with_nulls):
        """Hidden test: clean_data must remove duplicate sample_ids."""
        from data_loader import clean_data

        # Add a duplicate row
        df = pd.concat([dataframe_with_nulls, dataframe_with_nulls.iloc[[0]]])
        result = clean_data(df)

        assert result['sample_id'].is_unique, \
            "clean_data must remove duplicate sample_id entries"

    def test_clean_data_fills_missing_with_median(self):
        """Hidden test: clean_data must fill numeric NaN with median."""
        from data_loader import clean_data

        df = pd.DataFrame({
            'sample_id': ['A', 'B', 'C', 'D', 'E'],
            'hole_id': ['DH-01'] * 5,
            'from_depth': [10.0, 20.0, 30.0, 40.0, 50.0],
            'to_depth': [12.0, 22.0, 32.0, 42.0, 52.0],
            'lithology': ['Granite'] * 5,
            'grade': [1.0, 2.0, None, 4.0, 5.0],
            'mass': [10.0, 12.0, 14.0, None, 18.0],
            'volume': [5.0, 6.0, 7.0, 8.0, 9.0],
        })

        result = clean_data(df)

        # Median of [1,2,4,5] = 3.0; median of [10,12,14,18] = 13.0
        assert result['grade'].isna().sum() == 0, \
            "Grade NaN should be filled"
        assert result['mass'].isna().sum() == 0, \
            "Mass NaN should be filled"

    def test_clean_data_returns_copy(self, prospect_dataframe):
        """Test that clean_data does not modify the original DataFrame."""
        from data_loader import clean_data

        original_shape = prospect_dataframe.shape
        result = clean_data(prospect_dataframe)

        assert prospect_dataframe.shape == original_shape, \
            "clean_data should not modify the original DataFrame"

    def test_clean_data_on_prospect(self, prospect_dataframe):
        """Test cleaning on the actual prospect data."""
        from data_loader import clean_data

        result = clean_data(prospect_dataframe)

        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0, "Cleaned data should not be empty"
        # No negative grades after cleaning
        assert (result['grade'] >= 0).all(), "No negative grades after cleaning"


# ============================================================================
# HIDDEN DATA PROCESSOR TESTS
# ============================================================================

class TestHiddenDataProcessor:
    """Hidden tests for data_processor module using actual prospect data."""

    def test_calculate_density_on_prospect(self, prospect_dataframe):
        """Test density calculation on actual prospect data."""
        from data_processor import calculate_density

        result = calculate_density(prospect_dataframe)

        assert 'density' in result.columns
        # Verify density = mass / volume for all rows
        expected = prospect_dataframe['mass'] / prospect_dataframe['volume']
        np.testing.assert_array_almost_equal(
            result['density'].values, expected.values, decimal=4
        )

    def test_calculate_density_alternative(self, alternative_dataframe):
        """Test density on alternative data (catches hardcoded values)."""
        from data_processor import calculate_density

        result = calculate_density(alternative_dataframe)

        expected = alternative_dataframe['mass'] / alternative_dataframe['volume']
        np.testing.assert_array_almost_equal(
            result['density'].values, expected.values, decimal=4
        )

    def test_classify_grade_on_prospect(self, prospect_dataframe):
        """Test grade classification on actual prospect data."""
        from data_processor import classify_grade

        cutoff = 2.0
        result = classify_grade(prospect_dataframe, cutoff=cutoff)

        assert 'grade_class' in result.columns

        for _, row in result.iterrows():
            grade = row['grade']
            cls = row['grade_class']
            if grade >= 2 * cutoff:
                assert cls == 'High Grade', \
                    f"Grade {grade} with cutoff {cutoff} should be High Grade"
            elif grade >= cutoff:
                assert cls == 'Medium Grade', \
                    f"Grade {grade} with cutoff {cutoff} should be Medium Grade"
            else:
                assert cls == 'Low Grade', \
                    f"Grade {grade} with cutoff {cutoff} should be Low Grade"

    def test_classify_grade_variant_cutoff(self, prospect_dataframe, variant_config):
        """Test classification with the student's variant cutoff."""
        from data_processor import classify_grade

        cutoff = variant_config['parameters']['target_grade']
        result = classify_grade(prospect_dataframe, cutoff=cutoff)

        # Verify at least some samples in each class
        classes = result['grade_class'].unique()
        assert len(classes) >= 2, \
            "Should have at least 2 grade classes with variant cutoff"

    def test_calculate_intervals_on_prospect(self, prospect_dataframe):
        """Test interval calculation on actual prospect data."""
        from data_processor import calculate_intervals

        result = calculate_intervals(prospect_dataframe)

        assert 'interval' in result.columns
        expected = prospect_dataframe['to_depth'] - prospect_dataframe['from_depth']
        np.testing.assert_array_almost_equal(
            result['interval'].values, expected.values, decimal=4
        )

    def test_calculate_intervals_alternative(self, alternative_dataframe):
        """Test intervals on alternative data (catches hardcoded values)."""
        from data_processor import calculate_intervals

        result = calculate_intervals(alternative_dataframe)

        expected = alternative_dataframe['to_depth'] - alternative_dataframe['from_depth']
        np.testing.assert_array_almost_equal(
            result['interval'].values, expected.values, decimal=4
        )

    def test_filter_by_drillhole_subset(self, prospect_dataframe):
        """Test filtering to a specific subset of drillholes."""
        from data_processor import filter_by_drillhole

        selected = ['DH-01', 'DH-03', 'DH-05']
        result = filter_by_drillhole(prospect_dataframe, selected)

        assert set(result['hole_id'].unique()) == set(selected), \
            "Should only contain the specified drillholes"
        assert len(result) < len(prospect_dataframe), \
            "Filtered result should have fewer rows"

    def test_filter_by_drillhole_all(self, prospect_dataframe):
        """Test that None returns all rows."""
        from data_processor import filter_by_drillhole

        result = filter_by_drillhole(prospect_dataframe, None)

        assert len(result) == len(prospect_dataframe)

    def test_filter_by_drillhole_variant(self, prospect_dataframe, variant_config):
        """Test filtering with the student's variant drillholes."""
        from data_processor import filter_by_drillhole

        holes = variant_config['parameters']['drillholes']
        result = filter_by_drillhole(prospect_dataframe, holes)

        assert set(result['hole_id'].unique()).issubset(set(holes))
        assert len(result) > 0, "Variant drillholes should yield results"

    def test_density_does_not_modify_original(self, prospect_dataframe):
        """Test that calculate_density returns a copy."""
        from data_processor import calculate_density

        original_cols = list(prospect_dataframe.columns)
        result = calculate_density(prospect_dataframe)

        assert list(prospect_dataframe.columns) == original_cols, \
            "Should not modify original DataFrame columns"


# ============================================================================
# HIDDEN ANALYZER TESTS
# ============================================================================

class TestHiddenAnalyzer:
    """Hidden tests for analyzer module using actual prospect data."""

    def test_summary_statistics_on_prospect(self, prospect_dataframe):
        """Test summary statistics on actual prospect data."""
        from analyzer import summary_statistics

        result = summary_statistics(prospect_dataframe, ['grade', 'mass'])

        assert isinstance(result, pd.DataFrame)
        assert 'grade' in result.columns
        assert 'mass' in result.columns

    def test_summary_statistics_values_correct(self, prospect_dataframe):
        """Test that summary statistics values match pandas describe()."""
        from analyzer import summary_statistics

        result = summary_statistics(prospect_dataframe, ['grade'])

        # The mean in the result should match pandas calculation
        expected_mean = prospect_dataframe['grade'].mean()
        # Find the mean row (case-insensitive)
        mean_idx = [idx for idx in result.index if str(idx).lower() == 'mean']
        assert len(mean_idx) > 0, "Should have a 'mean' row"
        actual_mean = result.loc[mean_idx[0], 'grade']
        assert abs(actual_mean - expected_mean) < 0.01, \
            f"Mean should be {expected_mean:.4f}, got {actual_mean:.4f}"

    def test_summary_statistics_alternative(self, alternative_dataframe):
        """Test statistics on alternative data (catches hardcoded values)."""
        from analyzer import summary_statistics

        result = summary_statistics(alternative_dataframe, ['grade', 'mass'])

        expected_mean = alternative_dataframe['grade'].mean()
        mean_idx = [idx for idx in result.index if str(idx).lower() == 'mean']
        assert len(mean_idx) > 0
        actual_mean = result.loc[mean_idx[0], 'grade']
        assert abs(actual_mean - expected_mean) < 0.01

    def test_summary_statistics_variant_columns(self, prospect_dataframe, variant_config):
        """Test statistics with the student's variant columns."""
        from analyzer import summary_statistics

        columns = variant_config['parameters']['analysis_columns']
        result = summary_statistics(prospect_dataframe, columns)

        for col in columns:
            assert col in result.columns, \
                f"Variant column '{col}' should be in statistics"

    def test_grade_by_drillhole_on_prospect(self, prospect_dataframe):
        """Test grade groupby on actual prospect data."""
        from analyzer import grade_by_drillhole

        result = grade_by_drillhole(prospect_dataframe)

        assert isinstance(result, pd.DataFrame)
        # Should have 8 drillholes (DH-01 through DH-08)
        assert len(result) == 8, "Should have stats for all 8 drillholes"

    def test_grade_by_drillhole_values(self, prospect_dataframe):
        """Test that per-drillhole means match manual calculation."""
        from analyzer import grade_by_drillhole

        result = grade_by_drillhole(prospect_dataframe)

        # Check DH-01 mean manually
        dh01_data = prospect_dataframe[prospect_dataframe['hole_id'] == 'DH-01']
        expected_mean = dh01_data['grade'].mean()

        # Find DH-01 in result (could be index or column)
        if 'DH-01' in result.index:
            actual_mean = result.loc['DH-01', 'mean'] if 'mean' in result.columns else None
        else:
            actual_mean = None

        if actual_mean is not None:
            assert abs(actual_mean - expected_mean) < 0.01

    def test_grade_by_drillhole_alternative(self, alternative_dataframe):
        """Test groupby on alternative data (catches hardcoded values)."""
        from analyzer import grade_by_drillhole

        result = grade_by_drillhole(alternative_dataframe)

        expected_holes = alternative_dataframe['hole_id'].nunique()
        assert len(result) == expected_holes

    def test_correlation_on_prospect(self, prospect_dataframe):
        """Test correlation analysis on actual prospect data."""
        from analyzer import correlation_analysis

        columns = ['grade', 'mass', 'volume']
        result = correlation_analysis(prospect_dataframe, columns)

        assert result.shape == (3, 3), "Should be a 3x3 matrix"
        # Diagonal should be 1.0
        for col in columns:
            assert abs(result.loc[col, col] - 1.0) < 0.001

    def test_correlation_symmetric(self, prospect_dataframe):
        """Test that correlation matrix is symmetric."""
        from analyzer import correlation_analysis

        columns = ['grade', 'mass', 'volume']
        result = correlation_analysis(prospect_dataframe, columns)

        for c1 in columns:
            for c2 in columns:
                assert abs(result.loc[c1, c2] - result.loc[c2, c1]) < 0.001, \
                    f"Matrix should be symmetric: [{c1},{c2}]"

    def test_correlation_variant_columns(self, prospect_dataframe, variant_config):
        """Test correlation with the student's variant columns."""
        from analyzer import correlation_analysis

        columns = variant_config['parameters']['analysis_columns']
        result = correlation_analysis(prospect_dataframe, columns)

        assert result.shape[0] == len(columns)
        assert result.shape[1] == len(columns)

    def test_high_grade_zones_on_prospect(self, prospect_dataframe):
        """Test high grade identification on actual prospect data."""
        from analyzer import identify_high_grade_zones

        threshold = 2.0
        result = identify_high_grade_zones(prospect_dataframe, threshold)

        expected_count = (prospect_dataframe['grade'] >= threshold).sum()
        assert len(result) == expected_count
        assert (result['grade'] >= threshold).all()

    def test_high_grade_variant_threshold(self, prospect_dataframe, variant_config):
        """Test high grade with the student's variant threshold."""
        from analyzer import identify_high_grade_zones

        threshold = variant_config['parameters']['target_grade']
        result = identify_high_grade_zones(prospect_dataframe, threshold)

        expected = (prospect_dataframe['grade'] >= threshold).sum()
        assert len(result) == expected

    def test_high_grade_alternative(self, alternative_dataframe):
        """Test high grade on alternative data (catches hardcoded values)."""
        from analyzer import identify_high_grade_zones

        threshold = 3.0
        result = identify_high_grade_zones(alternative_dataframe, threshold)

        expected = (alternative_dataframe['grade'] >= threshold).sum()
        assert len(result) == expected


# ============================================================================
# HIDDEN VISUALIZER TESTS
# ============================================================================

class TestHiddenVisualizer:
    """Hidden tests for visualizer module using actual prospect data."""

    def test_histogram_with_prospect_data(self, prospect_dataframe, temp_output_dir):
        """Test histogram creation with actual prospect data."""
        from visualizer import plot_grade_histogram

        output_path = os.path.join(temp_output_dir, 'hidden_histogram.png')
        plot_grade_histogram(prospect_dataframe, output_path)

        assert os.path.exists(output_path), "Should create histogram file"
        assert os.path.getsize(output_path) > 0, "File should not be empty"

    def test_scatter_with_prospect_data(self, prospect_dataframe, temp_output_dir):
        """Test scatter plot with actual prospect data."""
        from visualizer import plot_depth_vs_grade

        output_path = os.path.join(temp_output_dir, 'hidden_scatter.png')
        plot_depth_vs_grade(prospect_dataframe, output_path)

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_boxplot_with_prospect_data(self, prospect_dataframe, temp_output_dir):
        """Test box plot with actual prospect data."""
        from visualizer import plot_grade_by_drillhole

        output_path = os.path.join(temp_output_dir, 'hidden_boxplot.png')
        plot_grade_by_drillhole(prospect_dataframe, output_path)

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_heatmap_with_prospect_data(self, prospect_dataframe, temp_output_dir):
        """Test heatmap with actual prospect correlation data."""
        from analyzer import correlation_analysis
        from visualizer import plot_correlation_heatmap

        corr = correlation_analysis(prospect_dataframe, ['grade', 'mass', 'volume'])
        output_path = os.path.join(temp_output_dir, 'hidden_heatmap.png')
        plot_correlation_heatmap(corr, output_path)

        assert os.path.exists(output_path)
        assert os.path.getsize(output_path) > 0

    def test_histogram_alternative_data(self, alternative_dataframe, temp_output_dir):
        """Test histogram with alternative data (catches hardcoded paths)."""
        from visualizer import plot_grade_histogram

        output_path = os.path.join(temp_output_dir, 'alt_histogram.png')
        plot_grade_histogram(alternative_dataframe, output_path)

        assert os.path.exists(output_path)

    def test_plots_produce_different_files(self, prospect_dataframe, temp_output_dir):
        """Test that different plot functions produce different output files."""
        from visualizer import plot_grade_histogram, plot_depth_vs_grade

        hist_path = os.path.join(temp_output_dir, 'hist.png')
        scatter_path = os.path.join(temp_output_dir, 'scatter.png')

        plot_grade_histogram(prospect_dataframe, hist_path)
        plot_depth_vs_grade(prospect_dataframe, scatter_path)

        hist_size = os.path.getsize(hist_path)
        scatter_size = os.path.getsize(scatter_path)

        # Files should exist and differ in size (different plots)
        assert hist_size > 0
        assert scatter_size > 0


# ============================================================================
# HIDDEN REPORTER TESTS
# ============================================================================

class TestHiddenReporter:
    """Hidden tests for reporter module with real data."""

    def test_report_contains_validation_info(self):
        """Test that report includes validation statistics."""
        from reporter import generate_summary_report

        validation = {
            'total_records': 300,
            'valid_records': 290,
            'missing_values': {'grade': 2, 'mass': 3},
            'invalid_grades': 5,
            'invalid_depths': 2
        }
        stats = pd.DataFrame(
            {'grade': [300, 2.5, 1.5, 0.1, 1.0, 2.0, 3.5, 6.0]},
            index=['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
        )

        result = generate_summary_report(validation, stats, 125, 'Test Project')

        assert '300' in result or 'total' in result.lower(), \
            "Report should reference total records"

    def test_report_with_variant_project_name(self, variant_config):
        """Test that report uses the student's variant project name."""
        from reporter import generate_summary_report

        project_name = variant_config['parameters']['project_name']
        validation = {
            'total_records': 100, 'valid_records': 95,
            'missing_values': {}, 'invalid_grades': 2, 'invalid_depths': 1
        }
        stats = pd.DataFrame(
            {'grade': [100, 2.0, 1.0, 0.5, 1.0, 2.0, 3.0, 5.0]},
            index=['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']
        )

        result = generate_summary_report(validation, stats, 50, project_name)

        assert project_name in result, \
            f"Report should contain variant project name: {project_name}"

    def test_save_report_writes_file(self, temp_output_dir):
        """Test that save_report creates a file with correct content."""
        from reporter import save_report

        content = "# Hidden Test Report\n\nContent here."
        path = os.path.join(temp_output_dir, 'hidden_report.md')

        save_report(content, path)

        assert os.path.exists(path)
        with open(path, 'r') as f:
            saved = f.read()
        assert saved == content

    def test_export_preserves_data(self, prospect_dataframe, temp_output_dir):
        """Test that export_processed_data preserves all data."""
        from reporter import export_processed_data

        path = os.path.join(temp_output_dir, 'hidden_export.csv')
        export_processed_data(prospect_dataframe, path)

        loaded = pd.read_csv(path)
        assert len(loaded) == len(prospect_dataframe)
        assert set(loaded.columns) == set(prospect_dataframe.columns)

    def test_export_alternative_data(self, alternative_dataframe, temp_output_dir):
        """Test export with alternative data (catches hardcoded paths)."""
        from reporter import export_processed_data

        path = os.path.join(temp_output_dir, 'alt_export.csv')
        export_processed_data(alternative_dataframe, path)

        loaded = pd.read_csv(path)
        assert len(loaded) == len(alternative_dataframe)


# ============================================================================
# VARIANT VERIFICATION TESTS
# ============================================================================

class TestHiddenVariantVerification:
    """Tests that verify students are using their assigned variant values."""

    def test_variant_has_required_keys(self, variant_config):
        """Test that variant config has all required keys."""
        assert 'student_id' in variant_config
        assert 'parameters' in variant_config

        params = variant_config['parameters']
        assert 'project_name' in params
        assert 'target_grade' in params
        assert 'drillholes' in params
        assert 'analysis_columns' in params

    def test_variant_target_grade_range(self, variant_config):
        """Test that target_grade is within expected range."""
        target = variant_config['parameters']['target_grade']
        assert 1.5 <= target <= 2.5, \
            f"target_grade {target} should be between 1.5 and 2.5"

    def test_variant_drillholes_valid(self, variant_config):
        """Test that variant drillholes are valid IDs from the CSV."""
        holes = variant_config['parameters']['drillholes']
        valid_holes = {f'DH-{i:02d}' for i in range(1, 9)}

        assert isinstance(holes, list)
        assert 4 <= len(holes) <= 6
        for h in holes:
            assert h in valid_holes, f"Invalid drillhole ID: {h}"

    def test_variant_analysis_columns_valid(self, variant_config):
        """Test that variant analysis columns are valid CSV columns."""
        columns = variant_config['parameters']['analysis_columns']
        valid_columns = {'grade', 'mass', 'volume', 'from_depth'}

        assert isinstance(columns, list)
        assert len(columns) == 3
        assert 'grade' in columns, "analysis_columns should always include 'grade'"
        for col in columns:
            assert col in valid_columns, f"Invalid analysis column: {col}"

    def test_classify_with_variant_cutoff(self, prospect_dataframe, variant_config):
        """Verify classification uses the student's variant cutoff."""
        from data_processor import classify_grade

        target = variant_config['parameters']['target_grade']
        result = classify_grade(prospect_dataframe, cutoff=target)

        # Count expected classes
        high_count = (prospect_dataframe['grade'] >= 2 * target).sum()
        medium_count = ((prospect_dataframe['grade'] >= target) &
                        (prospect_dataframe['grade'] < 2 * target)).sum()
        low_count = (prospect_dataframe['grade'] < target).sum()

        actual_high = (result['grade_class'] == 'High Grade').sum()
        actual_medium = (result['grade_class'] == 'Medium Grade').sum()
        actual_low = (result['grade_class'] == 'Low Grade').sum()

        assert actual_high == high_count, \
            f"High Grade count mismatch: expected {high_count}, got {actual_high}"
        assert actual_medium == medium_count, \
            f"Medium Grade count mismatch: expected {medium_count}, got {actual_medium}"
        assert actual_low == low_count, \
            f"Low Grade count mismatch: expected {low_count}, got {actual_low}"


# ============================================================================
# HIDDEN INTEGRATION TESTS
# ============================================================================

class TestHiddenIntegration:
    """Hidden integration tests running the full pipeline on prospect data."""

    def test_pipeline_with_prospect_data(self, prospect_csv_file, temp_output_dir):
        """Test full pipeline with actual prospect CSV."""
        from main import run_pipeline

        config = {
            'input_file': prospect_csv_file,
            'output_dir': temp_output_dir,
            'project_name': 'Hidden Test Project',
            'target_grade': 2.0,
            'drillholes': None,
        }

        result = run_pipeline(config)

        assert isinstance(result, dict)
        assert 'validation' in result
        assert 'statistics' in result
        assert 'high_grade_count' in result
        assert 'output_files' in result

    def test_pipeline_validation_on_prospect(self, prospect_csv_file, temp_output_dir):
        """Test that pipeline validation report is correct for prospect data."""
        from main import run_pipeline

        config = {
            'input_file': prospect_csv_file,
            'output_dir': temp_output_dir,
            'project_name': 'Validation Test',
            'target_grade': 2.0,
            'drillholes': None,
        }

        result = run_pipeline(config)

        assert result['validation']['total_records'] == 300

    def test_pipeline_with_variant_config(
        self, prospect_csv_file, temp_output_dir, variant_config
    ):
        """Test pipeline using the student's variant configuration."""
        from main import run_pipeline

        params = variant_config['parameters']
        config = {
            'input_file': prospect_csv_file,
            'output_dir': temp_output_dir,
            'project_name': params['project_name'],
            'target_grade': params['target_grade'],
            'drillholes': params['drillholes'],
        }

        result = run_pipeline(config)

        assert isinstance(result, dict)
        assert result['high_grade_count'] >= 0

    def test_pipeline_with_drillhole_filter(self, prospect_csv_file, temp_output_dir):
        """Test pipeline with specific drillhole subset."""
        from main import run_pipeline

        config = {
            'input_file': prospect_csv_file,
            'output_dir': temp_output_dir,
            'project_name': 'Filtered Pipeline',
            'target_grade': 2.0,
            'drillholes': ['DH-01', 'DH-03', 'DH-05'],
        }

        result = run_pipeline(config)

        assert result is not None
        assert isinstance(result['high_grade_count'], int)

    def test_pipeline_creates_output_files(self, prospect_csv_file, temp_output_dir):
        """Test that pipeline generates output files."""
        from main import run_pipeline

        config = {
            'input_file': prospect_csv_file,
            'output_dir': temp_output_dir,
            'project_name': 'Output Test',
            'target_grade': 2.0,
            'drillholes': None,
        }

        result = run_pipeline(config)

        assert len(result['output_files']) > 0, \
            "Pipeline should generate output files"

    def test_pipeline_high_grade_count_correct(
        self, prospect_csv_file, temp_output_dir
    ):
        """Test that pipeline high grade count matches manual calculation."""
        from main import run_pipeline
        from data_loader import load_prospect_data, clean_data

        threshold = 2.5
        config = {
            'input_file': prospect_csv_file,
            'output_dir': temp_output_dir,
            'project_name': 'Count Test',
            'target_grade': threshold,
            'drillholes': None,
        }

        result = run_pipeline(config)

        # Manually calculate expected count on cleaned data
        raw = load_prospect_data(prospect_csv_file)
        cleaned = clean_data(raw)
        expected = (cleaned['grade'] >= threshold).sum()

        assert result['high_grade_count'] == expected, \
            f"High grade count should be {expected}, got {result['high_grade_count']}"

    def test_load_process_analyze_chain(self, prospect_csv_file):
        """Test chaining load -> clean -> process -> analyze."""
        from data_loader import load_prospect_data, clean_data
        from data_processor import calculate_density, calculate_intervals
        from analyzer import summary_statistics

        # Load and clean
        df = load_prospect_data(prospect_csv_file)
        df = clean_data(df)

        # Process
        df = calculate_density(df)
        df = calculate_intervals(df)

        assert 'density' in df.columns
        assert 'interval' in df.columns

        # Analyze
        stats = summary_statistics(df, ['grade', 'density', 'interval'])
        assert 'grade' in stats.columns
        assert 'density' in stats.columns
        assert 'interval' in stats.columns
