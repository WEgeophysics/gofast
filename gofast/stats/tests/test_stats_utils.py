# -*- coding: utf-8 -*-
"""
test_stats_utils.py

@author: LKouadio <etanoyau@gmail.com>
"""

import pytest 

import numpy as np
import pandas as pd
from gofast.stats.utils import gomean, gomedian, gomode, gostd, govar
from gofast.stats.utils import get_range, quartiles, goquantile, gocorr
from gofast.stats.utils import correlation, z_scores, goiqr 
from gofast.stats.utils import godescribe, t_test_independent
from gofast.stats.utils import goskew, gokurtosis
@pytest.fixture
def sample_dataframe():
    return pd.DataFrame({'A': [1, 2, 3, 4, 5], 'B': [5, 4, 3, 2, 1]})

# Happy path test cases
def test_gomean_with_array():
    print(gomean([1, 2, 3, 4, 5]))
    assert gomean([1, 2, 3, 4, 5]) == 3.0

def test_gomean_with_dataframe_all_columns(sample_dataframe):
    result = gomean(sample_dataframe, as_frame=True)
    assert all(result == pd.Series([3.0, 3.0], index=['A', 'B']))

def test_gomean_with_dataframe_specific_columns(sample_dataframe):
    assert gomean(sample_dataframe, columns=['A']) == 3.0

# Visual check (might be skipped or modified for CI/CD)
def test_gomean_visualization(sample_dataframe):
    # This test might be more about ensuring no errors are raised
    gomean(sample_dataframe, view=True, as_frame=True)

    assert True  # Verify visualization code runs without error

# Happy path test cases
def test_gomedian_with_array():
    assert gomedian([1, 2, 3, 4, 5]) == 3.0

def test_gomedian_with_dataframe_all_columns(sample_dataframe):
    result = gomedian(sample_dataframe, as_frame=True)
    assert all(result == pd.Series([3.0, 3.0], index=['A', 'B']))

def test_gomedian_with_dataframe_specific_columns(sample_dataframe):
    assert gomedian(sample_dataframe, columns=['A']) == 3.0

# Visual check
def test_gomedian_visualization(sample_dataframe):
    # This test ensures no errors are raised during visualization
    gomedian(sample_dataframe, view=True, as_frame=True)
    assert True  # Verify visualization code runs without error

# Happy path test cases
def test_gomode_with_array():
    assert gomode([1, 2, 2, 3, 3, 3]) == 3

def test_gomode_with_dataframe_all_columns(sample_dataframe):
      result = gomode(sample_dataframe, as_frame=True)
      # Assuming mode returns the first mode encountered
      expected = pd.Series([1, 4], index=['A', 'B']) 
      assert all(result == expected)
     
@pytest.mark.skip 
def test_gomode_with_dataframe_specific_columns(sample_dataframe):
    result = gomode(sample_dataframe, columns=['B'], as_frame=True)
    assert result.tolist() == [4, 5] 

# # Visual check
def test_gomode_visualization(sample_dataframe):
    # This test ensures no errors are raised during visualization
    gomode(sample_dataframe, view=True, as_frame=True)
    assert True  # Verify visualization code runs without error

# Edge case test cases
@pytest.mark.skip ("Gomode can raised error for empty list.")
def test_gomode_empty_input():
    with pytest.raises(ValueError):
        gomode([])

def test_govar_with_array():
    data_array = np.array([1, 2, 3, 4, 5])
    expected_variance = 2.0 # calcualted the population variance 
    assert govar(data_array, ddof=0) == expected_variance, "Variance calculation for numpy array failed"

def test_govar_with_list():
    data_list = [1, 2, 3, 4, 5]
    expected_variance = 2.5 # sample variance is computed instead by default ddof=1
    assert govar(data_list) == expected_variance, "Variance calculation for list failed"

def test_govar_with_dataframe():
    data_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    expected_variance = pd.Series([1.0, 1.0], index=['A', 'B'])
    pd.testing.assert_series_equal(
        govar(data_df, as_frame=True), expected_variance, check_names=False)

def test_govar_with_dataframe_columns_specified():
    data_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    expected_variance = 1.0
    assert govar(data_df, columns=['A'], ddof=1) == expected_variance

def test_govar_with_axis_specified():
    data_array = np.array([[1, 2, 3], [4, 5, 6]])
    expected_variance = np.array([2.25, 2.25, 2.25])
    np.testing.assert_array_almost_equal(
        govar(data_array, axis=0, ddof =0), expected_variance)

@pytest.mark.skipif('not hasattr(govar, "view")')
def test_govar_with_view_enabled():
    data_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    # This test assumes that visualization does not affect the return value
    # and primarily ensures that no exceptions are raised during its execution.
    try:
        govar(data_df, view=True, fig_size=(8, 4))
    except Exception as e:
        pytest.fail(f"Visualization raised an exception: {e}")

# new Test data
data_list = [1, 2, 3, 4, 5]
data_array = np.array([1, 2, 3, 4, 5])
data_df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})

@pytest.mark.parametrize("input_data,expected_output", [
    (data_list, np.std(data_list, ddof=1)),
    (data_array, np.std(data_array, ddof=1)),
    (data_df, pd.Series([1.0, 1.0], index=['A', 'B'])),
])
def test_gostd_basic(input_data, expected_output):
    # Test without additional parameters
    result = gostd(input_data)
    if isinstance(input_data, pd.DataFrame):
        pd.testing.assert_series_equal(result, expected_output)
    else:
        assert result == pytest.approx(expected_output)

def test_gostd_with_columns():
    # Test specifying columns in a DataFrame
    result = gostd(data_df, columns=['A'], ddof=1)
    assert result == pytest.approx(3.0)

@pytest.mark.parametrize("ddof,expected_output", [
    (0, np.std(data_list, ddof=0)), (1, np.std(data_list, ddof=1))])
def test_gostd_ddof(ddof, expected_output):
    # Test with different ddof values
    result = gostd(data_list, ddof=ddof)
    assert result == pytest.approx(expected_output)

def test_gostd_as_frame():
    # Test returning result as a DataFrame
    result = gostd(data_list, as_frame=True)
    expected_output = pd.Series(np.std(data_list, ddof=1), index=['Standard Deviation'])
    pd.testing.assert_series_equal(result, expected_output)

def test_gostd_view(capfd):
    # Test visualization (view=True) does not raise errors
    # Note: This does not assert the correctness of the plot, only that the function runs
    gostd(data_list, view=True)
    out, err = capfd.readouterr()
    assert err == ""

@pytest.mark.parametrize("input_data, expected_exception", [
    ('invalid_data_type', ValueError), 
    # Non-numeric DataFrame,  Did not raise any error at least verbose is set. 
  #   (pd.DataFrame({'A': ['a', 'b', 'c']}), ValueError),  
])
def test_gostd_errors(input_data, expected_exception):
    # Test error handling for invalid inputs
    with pytest.raises(expected_exception):
        gostd(input_data)

data_df = pd.DataFrame({'A': [2, 5, 8], 'B': [1, 4, 7]})

@pytest.mark.parametrize("input_data,expected_result", [
    (data_array, pd.Series([4.0], index=['Range Values'])),  # Testing with a numpy array
    (data_df, pd.Series([6.0, 6.0], index=['A', 'B'])),  # Testing with a DataFrame, default columns
])
def test_get_range_basic(input_data, expected_result):
    result = get_range(input_data, as_frame=True)
    if isinstance(result, pd.Series):
        pd.testing.assert_series_equal(result, expected_result)
    else:
        assert result == expected_result

def test_get_range_with_columns():
    # Testing with specified columns in a DataFrame
    result = get_range(data_df, columns=['A'], as_frame=True)
    expected_result = pd.Series([6.], index=['A'])
    pd.testing.assert_series_equal(result, expected_result)

@pytest.mark.parametrize("axis,expected_result", [
    (0, pd.Series([6., 6.], index=['A', 'B'])),  # Testing across index (rows)
    (1, pd.Series([1., 1., 1.], index=[0, 1, 2])),  # Testing across columns
])
def test_get_range_axis(axis, expected_result):
    result = get_range(data_df, axis=axis, as_frame=True)
    pd.testing.assert_series_equal(result, expected_result)

@pytest.mark.parametrize("input_data, expected_exception", [
    ('invalid_data_type', ValueError), 
    ])
def test_get_range_errors(input_data, expected_exception):
    # Testing with invalid input data type
    with pytest.raises(expected_exception):
        get_range(input_data)

# Example of a test function that could be used to test view functionality,
# though it's tricky to assert graphical output in a unit test.
@pytest.mark.skip(reason="Difficult to test view functionality in unit tests")
def test_get_range_view():
    # This is a placeholder to indicate where a test for the view functionality might go
    pass

@pytest.fixture
def sample_data():
    return np.array([1, 2, 3, 4, 5])

@pytest.fixture
def sample_dataframe2():
    return pd.DataFrame({'A': [2, 5, 7, 8], 'B': [1, 4, 6, 9]})

def test_quartiles_with_array(sample_data):
    result = quartiles(sample_data, as_frame=False )
    expected = np.array([2., 3., 4.])
    np.testing.assert_array_equal(result, expected)

def test_quartiles_with_dataframe(sample_dataframe2):
    result = quartiles(sample_dataframe2, as_frame=True)  # as_frame=True is default behaviour
    # Adjust how you construct the expected DataFrame to match the result's structure
    expected = pd.DataFrame({'25%': [4.25, 3.25], '50%': [6., 5.], '75%': [7.25, 6.75]}, 
                            index=['A', 'B'])
    pd.testing.assert_frame_equal(result, expected)

def test_quartiles_with_specified_columns(sample_dataframe2):
    result = quartiles(sample_dataframe2, columns=['A'], as_frame=True)
    expected = pd.DataFrame({'25%': [4.25], '50%': [6.], '75%': [7.25]}, index=['A'])
    pd.testing.assert_frame_equal(result, expected)


def test_quartiles_error_on_mismatched_keyword_argument():
    with pytest.raises(TypeError):
        quartiles(np.array([1, 2, 3]), new_indexes=['a', 'b'])

@pytest.mark.parametrize("plot_type", ['box', 'hist'])
def test_quartiles_visualization_with_plot_types(sample_dataframe2, plot_type):
    # This test ensures no exceptions are raised during plotting
    # Actual visualization output is not checked here
    quartiles(sample_dataframe2, view=True, plot_type=plot_type, fig_size=(4, 4))
    quartiles(sample_dataframe2, view=True, axis=1,  plot_type=plot_type, fig_size=(4, 4))


@pytest.fixture
def sample_array():
    return np.array([1, 2, 3, 4, 5])

@pytest.fixture
def sample_dataframe3():
    return pd.DataFrame({'A': [2, 5, 7, 8], 'B': [1, 4, 6, 9]})

# Test for single quantile with array input
def test_goquantile_single_with_array(sample_array):
    result = goquantile(sample_array, q=0.5, as_frame=False )
    expected = 3.0 # return array of single value 
    assert result == expected, "Failed to compute median correctly for array input"

# Test for multiple quantiles with array input
def test_goquantile_multiple_with_array(sample_array):
    result = goquantile(sample_array, q=[0.25, 0.75], as_frame=False)
    expected = np.array([2., 4.])
    np.testing.assert_array_equal(result, expected, "Failed to compute quartiles correctly for array input")

# Test for single quantile with DataFrame input, as_frame=True
def test_goquantile_single_with_dataframe_as_frame(sample_dataframe3):
    result = goquantile(sample_dataframe3, q=0.5, as_frame=True )
    expected = pd.Series(data= [6.0, 5.0], index=['A', 'B'], name ='50%')
    pd.testing.assert_series_equal(
        result, expected, "Failed to compute median correctly for DataFrame input")

# Test for multiple quantiles with DataFrame input, specific columns
def test_goquantile_multiple_with_dataframe_columns(sample_dataframe3):
    result = goquantile(sample_dataframe3, q=[0.25, 0.75], columns=['A'])
    expected = pd.Series ( np.array([4.25, 7.25]), name="A", index=['25%', "75%"]) 
    pd.testing.assert_series_equal(
        result, expected, "Failed to compute quartiles correctly for specific DataFrame columns")

# Test for visualization option (Note: This might be more about checking if an error is raised, as visual output is hard to test)
@pytest.mark.parametrize("plot_type", ['box', 'hist'])
def test_goquantile_visualization(sample_dataframe3, plot_type):
    # This test ensures no exceptions are raised during plotting
    # It does not check the visual output, which is typically not done in unit tests
    try:
        goquantile(sample_dataframe3, q=[0.25, 0.75], view=True, 
                    plot_type=plot_type, as_frame=True)
    except Exception as e:
        pytest.fail(f"Visualization with plot_type='{plot_type}' raised an exception: {e}")

@pytest.mark.parametrize("method", ["pearson", "kendall", "spearman"])
def test_gocorr_with_dataframe(method):
    # Create a simple DataFrame
    data = pd.DataFrame({
        'A': np.arange(10),
        'B': np.arange(10) * 2,
        'C': np.random.randn(10)
    })

    # Calculate the correlation matrix using the gocorr function
    correlation_matrix = gocorr(data, method=method)

    # Check if the output is a DataFrame
    assert isinstance(correlation_matrix, pd.DataFrame), "Output should be a DataFrame"

    # Check if the diagonal elements are all ones 
    # (since a variable is perfectly correlated with itself)
    np.testing.assert_array_almost_equal(
        np.diag(correlation_matrix), np.ones(correlation_matrix.shape[0]),
        err_msg="Diagonal elements should be 1")

    # Optionally, check if the correlation matrix is symmetric
    np.testing.assert_array_almost_equal(
        correlation_matrix, correlation_matrix.T,
        err_msg="Correlation matrix should be symmetric")

@pytest.mark.parametrize("input_data", [np.random.randn(
    10, 3), [[1, 2, 3], [4, 5, 6], [7, 8, 9]]])
def test_gocorr_with_arraylike(input_data):
    # Calculate the correlation matrix for array-like input
    correlation_matrix = gocorr(input_data)

    # Check if the output is a DataFrame
    assert isinstance(correlation_matrix, pd.DataFrame), "Output should be a DataFrame when input is array-like"

# This test assumes the presence of a plotting display, which may not
#  always be available in a CI environment
@pytest.mark.skip(reason="Requires display for plotting")
def test_gocorr_view():
    data = pd.DataFrame({
        'A': np.random.randn(10),
        'B': np.random.randn(10),
        'C': np.random.randn(10)
    })

    # Simply call gocorr with view=True to ensure no exceptions occur during plotting
    # Note: This does not actually "test" the visual output, but it can 
    # catch errors in the plotting code
    gocorr(data, view=True)

def test_correlation_with_column_names():
    # Create a DataFrame for testing
    data = pd.DataFrame({
        'A': [1, 2, 3, 4],
        'B': [4, 3, 2, 1]
    })
    # Test correlation between two columns specified by name
    corr_value = correlation('A', 'B', data=data)
    assert corr_value == -1, "Correlation between 'A' and 'B' should be -1"

def test_correlation_with_arrays():
    # Test correlation between two array-like inputs
    x = [1, 2, 3, 4]
    y = [4, 3, 2, 1]
    corr_value = correlation(x, y)
    assert corr_value == -1, "Correlation between x and y should be -1"

def test_correlation_matrix():
    # Test correlation matrix computation from a DataFrame
    data = pd.DataFrame({
        'A': np.random.rand(10),
        'B': np.random.rand(10),
        'C': np.random.rand(10)
    })
    corr_matrix = correlation(data=data)
    assert isinstance(corr_matrix, pd.DataFrame), "Output should be a DataFrame"
    assert corr_matrix.shape == (3, 3), "Correlation matrix shape should be (3, 3)"
    assert np.allclose(np.diag(corr_matrix), 1), "Diagonal elements should be 1"

@pytest.mark.parametrize("method", ["pearson", "kendall", "spearman"])
def test_correlation_method(method):
    # Test different methods of correlation computation
    x = np.random.rand(10)
    y = np.random.rand(10)
    corr_value = correlation(x, y, method=method)
    assert isinstance(corr_value, float), f"Correlation value should be a float using method {method}"

# Test for the visualization, should be skipped in a CI environment without display
@pytest.mark.skip(reason="Visualization test requires display environment")
def test_correlation_view():
    x = [1, 2, 3, 4]
    y = [4, 3, 2, 1]
    # This test will check if the function call with view=True raises any exceptions
    try:
        correlation(x, y, view=True, plot_type='scatter')
    except Exception as e:
        pytest.fail(f"Visualization with view=True should not raise exceptions. Raised: {str(e)}")

@pytest.mark.parametrize("data,expected_iqr, as_frame", [
    ([1, 2, 3, 4, 5], 2.0, False ),
    (np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]), 4.5, False),
    (pd.DataFrame({'A': [2, 5, 7, 8], 'B': [1, 4, 6, 9]}), pd.Series(
        [3., 3.5], index=['A', 'B'], name="IQR"), True ),
])
def test_goiqr(data, expected_iqr, as_frame):
    result = goiqr(data, as_frame=as_frame)
    if as_frame:
        pd.testing.assert_series_equal(result, expected_iqr)
    else:
        assert result == expected_iqr

@pytest.mark.parametrize("data, view, plot_type", [
    ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], True, 'boxplot'),
    (pd.DataFrame({
        'A': np.random.normal(0, 1, 100),
        'B': np.random.normal(1, 2, 100),
        'C': np.random.normal(2, 3, 100)
    }), True, 'boxplot'),
])
def test_goiqr_view(data, view, plot_type):
    # This test ensures that the function runs with visualization
    # enabled but does not check the plot itself
    assert goiqr(data, view=view, plot_type=plot_type, as_frame=False) is not None


@pytest.mark.parametrize("data,expected, as_frame", [
    ([1, 2, 3, 4, 5], np.array(
        [-1.26491106, -0.63245553,  0. ,  0.63245553,  1.26491106]), False),
    (pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]}), pd.DataFrame(
        {'A': [-1., 0., 1.], 'B': [-1., 0., 1.]}), True),
])
def test_z_scores(data, expected, as_frame):
    result = z_scores(data, as_frame=as_frame)
    if as_frame:
        pd.testing.assert_frame_equal(result, pd.DataFrame(expected), rtol=1e-3)
    else:
        np.testing.assert_array_almost_equal(result, expected, decimal=5)

@pytest.mark.parametrize("data, view, plot_type", [
    ([1, 2, 3, 4, 5], True, 'hist'),
    (pd.DataFrame({'A': np.random.normal(
        0, 1, 100), 'B': np.random.normal(1, 2, 100)}), True, 'box'),
])
def test_z_scores_view(data, view, plot_type):
    # This test ensures that the function runs with visualization enabled 
    # but does not check the plot itself
    assert z_scores(data, view=view, plot_type=plot_type, as_frame=False) is not None

def test_godescribe_with_array():
    """Test godescribe with a numpy array input."""
    data = np.random.rand(100, 4)
    result = godescribe(data, as_frame=True)
    assert isinstance(result, pd.DataFrame), "Result should be a DataFrame for array input with as_frame=True"

def test_godescribe_with_dataframe_columns():
    """Test godescribe with a DataFrame and specific columns."""
    df = pd.DataFrame(np.random.rand(100, 4), columns=['A', 'B', 'C', 'D'])
    result = godescribe(df, columns=['A', 'B'])
    assert 'A' in result.columns and 'B' in result.columns, "Result should include specified columns"
    assert 'C' not in result.columns and 'D' not in result.columns, "Result should not include unspecified columns"

def test_godescribe_view_false():
    """Test godescribe with view=False to ensure no plot is generated."""
    df = pd.DataFrame(np.random.rand(100, 4), columns=['A', 'B', 'C', 'D'])
    result = godescribe(df, view=False)
    # This test assumes the function does not raise an exception and returns the correct type
    assert isinstance(result, pd.DataFrame), "Result should be a DataFrame when view=False"

def test_godescribe_invalid_plot_type():
    """Test godescribe with an invalid plot_type value."""
    df = pd.DataFrame(np.random.rand(100, 4), columns=['A', 'B', 'C', 'D'])
    with pytest.raises(ValueError):
        godescribe(df, view=True, plot_type='invalid_plot_type')

def test_godescribe_as_frame_false():
    """Test godescribe with as_frame=False."""
    df = pd.DataFrame(np.random.rand(10, 2), columns=['A', 'B'])
    result = godescribe(df, as_frame=False)
    # Expecting a Series if as_frame=False for shape[1] 2 and array otherwise
    # with the same shape and data is a DataFrame
    assert isinstance(result, np.ndarray), "Result should be a numpy array when as_frame=False"

def test_calculate_skewness_with_array():
    """Test skewness calculation with a numpy array input."""
    data = np.random.normal(0, 1, size=1000)
    skewness = goskew(data)
    assert isinstance(skewness, float), "Skewness should be a float for array input"

def test_calculate_skewness_with_dataframe():
    """Test skewness calculation with a DataFrame input."""
    df = pd.DataFrame({
        'normal': np.random.normal(0, 1, 1000),
        'right_skewed': np.random.exponential(1, 1000)
    })
    skewness = goskew(df, as_frame=True)
    assert isinstance(skewness, pd.DataFrame), ( 
        "Skewness should be a Series for DataFrame input with as_frame=True"
        )
    assert 'normal' in skewness.index and 'right_skewed' in skewness.index, ( 
        "Skewness Series should contain columns from DataFrame"
        ) 

def test_calculate_skewness_view_false():
    """Test that no plot is generated when view=False."""
    data = np.random.normal(0, 1, size=1000)
    skewness = goskew(data, view=False)
    # This test assumes the function does not raise an exception
    assert isinstance(skewness, float), "Skewness calculation should succeed without generating a plot"

def test_calculate_skewness_invalid_plot_type():
    """Test error handling for unsupported plot_type."""
    data = np.random.normal(0, 1, size=1000)
    with pytest.raises(ValueError):
        goskew(data, view=True, plot_type='unsupported_plot_type')

def test_calculate_skewness_columns_specified():
    """Test skewness calculation for specified DataFrame columns."""
    df = pd.DataFrame({
        'A': np.random.normal(0, 1, 1000),
        'B': np.random.exponential(1, 1000)
    })
    skewness = goskew(df, columns=['A'], as_frame=True)
    assert 'A' in skewness.index, "Specified index should be included in skewness calculation"
    assert 'B' not in skewness, "Unspecified columns should not be included in skewness calculation"

def test_calculate_kurtosis_array():
    """Test kurtosis calculation with a numpy array."""
    data = np.random.normal(0, 1, 1000)
    kurtosis = gokurtosis(data)
    assert isinstance(kurtosis, float), "Kurtosis should be a float for numpy array input"

def test_calculate_kurtosis_dataframe():
    """Test kurtosis calculation with a pandas DataFrame."""
    df = pd.DataFrame({
        'A': np.random.normal(0, 1, size=1000),
        'B': np.random.standard_t(10, size=1000),
    })
    kurtosis = gokurtosis(df, as_frame=True)
    assert isinstance(kurtosis, pd.DataFrame), "Kurtosis should be a DataFrame when as_frame is True"
    assert 'A' in kurtosis.index and 'B' in kurtosis.index, "Kurtosis DataFrame should contain correct index"

@pytest.mark.skip ("Need visualization environnement.")
def test_calculate_kurtosis_view():
    """Test kurtosis calculation with visualization enabled (view=True)."""
    # This test simply runs the function with view=True to ensure no exceptions are raised.
    # It does not check the correctness of the plot.
    data = np.random.normal(0, 1, 1000)
    try:
        gokurtosis(data, view=True)
    except Exception as e:
        pytest.fail(f"Kurtosis calculation with view=True should not raise an exception. Raised: {e}")

def test_calculate_kurtosis_invalid_input():
    """Test kurtosis calculation with invalid input."""
    data = "not a valid input"
    with pytest.raises(( TypeError, ValueError)):
        gokurtosis(data)

# Test with numeric lists
def test_with_numeric_lists():
    sample1 = [22, 23, 25, 27, 29]
    sample2 = [18, 20, 21, 20, 19]
    t_stat, p_value, reject_null = t_test_independent(sample1, sample2)
    assert isinstance(t_stat, float) and isinstance(p_value, float)
    assert reject_null==True

# Test with DataFrame columns
def test_with_dataframe_columns():
    df = pd.DataFrame({'Group1': [22, 23, 25, 27, 29], 'Group2': [18, 20, 21, 20, 19]})
    t_stat, p_value, reject_null = t_test_independent('Group1', 'Group2', data=df)

    assert isinstance(t_stat, float) and isinstance(p_value, float)
    assert reject_null==True

# Test with invalid input (string without DataFrame)
def test_with_invalid_input():
    with pytest.raises(ValueError):
        t_test_independent('Group1', 'Group2')

# Test as_frame option
def test_as_frame_option():
    sample1 = [22, 23, 25, 27, 29]
    sample2 = [18, 20, 21, 20, 19]
    result = t_test_independent(sample1, sample2, as_frame=True)
    assert isinstance(result, pd.Series)
    assert 'T-statistic' in result.index and 'P-value' in result.index and 'Reject Null' in result.index

if __name__=="__main__": 
    # test_gomode_with_dataframe_specific_columns(sample_dataframe)
    pytest.main([__file__])



