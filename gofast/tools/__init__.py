"""
Tools sub-package offers several tools for data handling, parameters computation 
models estimation and evalution. The extension of the mathematical concepts, 
via the module :mod:`~gofast.tools.mathex`. Whereas the machine learning 
utilities and additional functionalities are performed with
 :mod:`~gofast.tools.mlutils` and :mod:`~gofast.tools.funcutils` respectively. 
"""

from .baseutils import (
    audit_data, 
    read_data,
    sanitize, 
    get_remote_data, 
    array2hdf5, 
    save_or_load, 
    request_data, 
    fancier_downloader,
    speed_rowwise_process,
    store_or_retrieve_data, 
    enrich_data_spectrum, 
    format_long_column_names, 
    summarize_text_columns, 
    simple_extractive_summary, 
    handle_datasets_with_hdfstore, 
    verify_data_integrity, 
    handle_categorical_features, 
    convert_date_features, 
    scale_data, 
    inspect_data, 
    handle_outliers_in_data,
    handle_missing_data, 
    augment_data, 
    assess_outlier_impact
    )
from .mathex import ( 
    interpolate1d, 
    interpolate2d,
    scale_y, 
    get_bearing, 
    moving_average, 
    linkage_matrix, 
    get_distance,
    smooth1d, 
    smoothing, 
    quality_control, 
    adaptive_moving_average, 
    savgol_filter,
    linear_regression,
    quadratic_regression,
    exponential_regression,
    logarithmic_regression,
    sinusoidal_regression,
    cubic_regression,
    step_regression, 
    standard_scaler, 
    minmax_scaler, 
    normalize, 
    category_count, 
    soft_bin_stat, 
    binning_statistic, 
    label_importance,
    make_mxs, 
    )
from .funcutils import ( 
    reshape, 
    to_numeric_dtypes, 
    smart_label_classifier, 
    remove_outliers,
    normalizer, 
    cleaner, 
    save_job, 
    random_selector, 
    interpolate_grid, 
    pair_data, 
    random_sampling, 
    replace_data, 
    store_or_write_hdf5, 
    )

from .mlutils import ( 
    evaluate_model,
    select_features, 
    get_global_score,  
    get_correlated_features, 
    find_features_in, 
    codify_variables, 
    categorize_target, 
    resampling, 
    bin_counting, 
    labels_validator, 
    projection_validator, 
    rename_labels_in , 
    soft_imputer, 
    soft_scaler, 
    select_feature_importances, 
    make_pipe, 
    build_data_preprocessor, 
    load_saved_model, 
    bi_selector, 
    get_target, 
    export_target,  
    stats_from_prediction, 
    fetch_tgz,  
    fetch_model, 
    load_csv, 
    split_train_test_by_id, 
    split_train_test, 
    discretize_categories, 
    stratify_categories, 
    serialize_data, 
    deserialize_data, 
    soft_data_split, 
    laplace_smoothing, 
    features_in, 
    laplace_smoothing_categorical, 
    laplace_smoothing_word
    
    ) 
__all__=[
    'audit_data', 
    'inspect_data', 
    'read_data',
    'augment_data', 
    'assess_outlier_impact', 
    'array2hdf5', 
    'sanitize',
    'save_or_load', 
    'request_data', 
    'get_remote_data', 
    'fancier_downloader',
    'savgol_filter', 
    'interpolate1d', 
    'interpolate2d',
    'scale_y', 
    'select_features', 
    'get_global_score',  
    'split_train_test', 
    'speed_rowwise_process', 
    'get_correlated_features', 
    'find_features_in',
    'codify_variables', 
    'evaluate_model',
    'moving_average', 
    'linkage_matrix',
    'reshape', 
    'to_numeric_dtypes' , 
    'smart_label_classifier', 
    'evaluate_model',
    'select_features', 
    'get_global_score', 
    'split_train_test', 
    'find_features_in', 
    'categorize_target', 
    'resampling', 
    'bin_counting', 
    'labels_validator', 
    'projection_validator', 
    'rename_labels_in' , 
    'soft_imputer', 
    'soft_scaler', 
    'select_feature_importances', 
    'make_pipe', 
    'build_data_preprocessor', 
    'bi_selector', 
    'get_target', 
    'export_target',  
    'stats_from_prediction', 
    'fetch_tgz', 
    'fetch_model', 
    'load_csv', 
    'split_train_test_by_id', 
    'split_train_test', 
    'discretize_categories', 
    'stratify_categories', 
    'serialize_data', 
    'deserialize_data', 
    'soft_data_split', 
    'soft_imputer', 
    'soft_scaler', 
    'make_pipe',
    'label_importance', 
    'remove_outliers', 
    'normalizer',
    'get_distance',
    'get_bearing', 
    'quality_control', 
    'cleaner', 
    'save_job', 
    'random_selector', 
    'interpolate_grid',
    'smooth1d', 
    'smoothing', 
    'pair_data', 
    'random_sampling', 
    'replace_data', 
    'store_or_write_hdf5', 
    "resampling", 
    "bin_counting",
    "adaptive_moving_average", 
    "load_saved_model", 
    "butterworth_filter",
    "laplace_smoothing", 
    "features_in", 
    "linear_regression",
    "quadratic_regression",
    "exponential_regression",
    "logarithmic_regression",
    "sinusoidal_regression",
    'enrich_data_spectrum', 
    'format_long_column_names', 
    'summarize_text_columns', 
    'simple_extractive_summary', 
    "cubic_regression",
    "step_regression", 
    "standard_scaler", 
    "minmax_scaler", 
    "normalize", 
    "category_count", 
    "soft_bin_stat", 
    "binning_statistic",
    "laplace_smoothing_categorical", 
    "laplace_smoothing_word",
    "store_or_retrieve_data", 
    "handle_datasets_with_hdfstore", 
    "verify_data_integrity", 
    "handle_categorical_features", 
    "convert_date_features", 
    "scale_data", 
    "handle_outliers_in_data",
    "handle_missing_data", 
    "make_mxs"
    
    ]



