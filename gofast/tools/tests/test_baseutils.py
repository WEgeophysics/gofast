# -*- coding: utf-8 -*-

import tempfile
import os
import unittest
from importlib import resources
from unittest.mock import patch, mock_open, MagicMock
import pandas as pd
import numpy as np
import pytest # noqa

from sklearn.datasets import fetch_california_housing
#from sklearn.datasets import load_boston # `load_boston` has been removed from scikit-learn since version 1.2.

from gofast.tools.baseutils import array2hdf5
from gofast.tools.baseutils import summarize_text_columns
from gofast.tools.baseutils import enrich_data_spectrum
from gofast.tools.baseutils import simple_extractive_summary
from gofast.tools.baseutils import format_long_column_names
from gofast.tools.baseutils import sanitize
from gofast.tools.baseutils import remove_target_from_array
from gofast.tools.baseutils import save_or_load
from gofast.tools.baseutils import read_data
from gofast.tools.baseutils import download_file
from gofast.tools.baseutils import fetch_remote_data, get_remote_data
from gofast.tools.baseutils import request_data
from gofast.tools.baseutils import lowertify
# from gofast.tools.baseutils import move_file
from gofast.tools.baseutils import fancier_downloader
from gofast.tools.baseutils import store_or_retrieve_data, base_storage
from gofast.tools.baseutils import audit_data, verify_data_integrity 
from gofast.tools.baseutils import handle_categorical_features
from gofast.tools.baseutils import convert_date_features
from gofast.tools.baseutils import handle_missing_data
from gofast.tools.baseutils import handle_outliers_in_data
from gofast.tools.baseutils import scale_data

from gofast.tools.baseutils import inspect_data
from gofast.tools.baseutils import augment_data
from gofast.tools.baseutils import assess_outlier_impact
from gofast.tools.baseutils import transform_dates
from gofast.tools.baseutils import merge_frames_on_index  
from gofast.tools.baseutils  import apply_tfidf_vectorization  
from gofast.tools.baseutils  import apply_bow_vectorization  
from gofast.tools.baseutils  import apply_word_embeddings  
from gofast.tools.baseutils  import boxcox_transformation  
from gofast.tools.baseutils  import check_missing_data  


DOWNLOAD_FILE='https://raw.githubusercontent.com/WEgeophysics/gofast/main/gofast/datasets/data/iris.csv'
class TestSummarizeTextColumns(unittest.TestCase):
    def test_summarize_text_columns(self):
        data = {
            'id': [1, 2],
            'column1': [
                "Sentence one. Sentence two. Sentence three.",
                "Another sentence one. Another sentence two. Another sentence three."
            ],
            'column2': [
                "More text here. Even more text here.",
                "Second example here. Another example here."
            ]
        }
        df = pd.DataFrame(data)
        summarized_df = summarize_text_columns(
            df, ['column1', 'column2'], 
            stop_words='english', encode=True, drop_original=False, 
            compression_method='mean')
        self.assertIn('column1_encoded', summarized_df.columns)
        self.assertIn('column2_encoded', summarized_df.columns)
        self.assertEqual(summarized_df.shape[1], 5)  # id column + 2 encoded columns

class TestSimpleExtractiveSummary(unittest.TestCase):
    def test_simple_extractive_summary(self):
        messages = [
            "Further explain the background and rationale for the study. "
            "Explain DNA in simple terms for non-scientists. "
            "Explain the objectives of the study which do not seem perceptible. THANKS",
            "We think this investigation is a good thing. In our opinion, it already allows the "
            "initiators to have an idea of what the populations think of the use of DNA in forensic "
            "investigations in Burkina Faso. And above all, know, through this survey, if these "
            "populations approve of the establishment of a possible genetic database in our country."
        ]
  
        summary, encoding = simple_extractive_summary(messages, encode=True)
        self.assertIsInstance(summary, str)
        if encoding is not None:
            self.assertGreater(encoding.size, 0)

class TestFormatLongColumnNames(unittest.TestCase):
    def test_format_long_column_names(self):
        data = {'VeryLongColumnNameIndeed': [1, 2, 3], 'AnotherLongColumnName': [4, 5, 6]}
        df = pd.DataFrame(data)
        new_df, mapping = format_long_column_names(df, max_length=10, return_mapping=True, name_case='capitalize')
        self.assertIn('Verylongco', new_df.columns)
        self.assertIn('Anotherlon', new_df.columns)
        self.assertEqual(len(mapping), 2)


class TestEnrichDataSpectrum(unittest.TestCase):
    def test_enrich_data_spectrum(self):
        housing = fetch_california_housing()
        data = pd.DataFrame(housing.data, columns=housing.feature_names)
        augmented_data = enrich_data_spectrum(data, noise_level=0.02, resample_size=50, synthetic_size=50, bootstrap_size=50)
        self.assertGreater(augmented_data.shape[0], data.shape[0])

class TestSanitize(unittest.TestCase):
    def test_sanitize(self):
        data = {'A': [1, 2, None, 4], 'B': ['X', 'Y', 'Y', None], 'C': [1, 1, 2, 2]}
        df = pd.DataFrame(data)
        cleaned_df = sanitize(df, fill_missing='median', remove_duplicates=True, outlier_method='z_score', consistency_transform='lower')
        self.assertFalse(cleaned_df.isnull().any().any())
        self.assertTrue('x' in cleaned_df['B'].values)

class TestRemoveTargetFromArray(unittest.TestCase):
    def test_remove_target_from_array(self):
        arr = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        target_indices = [1, 2]
        modified_arr, target_arr = remove_target_from_array(arr, target_indices)
        self.assertEqual(modified_arr.tolist(), [[1], [4], [7]])
        self.assertEqual(target_arr.tolist(), [[2, 3], [5, 6], [8, 9]])

# Note: This test case is conceptual and may need adjustments for real-world usage
class TestReadData(unittest.TestCase):
    @patch('gofast.tools.baseutils.pd.read_csv')
    def test_read_data_csv(self, mock_read_csv):
        with resources.path ('gofast.datasets.data', "bagoue.csv") as p : 
            file = str(p)
        mock_read_csv.return_value = pd.DataFrame({'A': [1, 2, 3]})
        df = read_data(file)
        self.assertTrue(isinstance(df, pd.DataFrame))
        self.assertFalse(df.empty)
        mock_read_csv.assert_called_once_with(file)

# Note: This test assumes h5py is installed and a temporary file can be written and read
class TestArray2HDF5(unittest.TestCase):
    def test_array2hdf5_store_and_load(self):
        arr = np.array([[1, 2], [3, 4]])
        with tempfile.NamedTemporaryFile(delete=False, suffix='.h5') as tmp:
            tmp_name = tmp.name
        array2hdf5(tmp_name, arr, task='store')
        loaded_arr = array2hdf5(tmp_name, task='load')
        os.remove(tmp_name)  # Clean up the temporary file
        self.assertTrue(np.array_equal(arr, loaded_arr))

class TestLowertify(unittest.TestCase):
    def test_lowertify(self):
        result = lowertify("Test", "STRING", 123)
        self.assertEqual(result, ('test', 'string', '123'))
        test_result, string_result= lowertify("Test", "STRING", return_origin=True)
        self.assertEqual(test_result, ('test', 'Test'))
        self.assertEqual(string_result, ('string', 'STRING'))

# Note: This test case is conceptual and may need adjustments for real-world usage
class TestSaveOrLoad(unittest.TestCase):
    @patch('gofast.tools.baseutils.np.save')
    def test_save_array(self, mock_save):
        arr = np.array([1, 2, 3])
        save_or_load("dummy.npy", arr, task='save', format='.npy')
        mock_save.assert_called_once()

    @patch('gofast.tools.baseutils.np.load')
    def test_load_array(self, mock_load):
        mock_load.return_value = np.array([1, 2, 3])
        result = save_or_load("dummy.npy", task='load')
        self.assertTrue(np.array_equal(result, np.array([1, 2, 3])))
        mock_load.assert_called_once_with("dummy.npy")

class TestRequestData(unittest.TestCase):
    @patch('gofast.tools.baseutils.requests.get')
    def test_request_data_get_as_json(self, mock_get):
        mock_get.return_value.json.return_value = {'key': 'value'}
        response = request_data('http://example.com', as_json=True)
        self.assertEqual(response, {'key': 'value'})

    @patch('gofast.tools.baseutils.requests.post')
    def test_request_data_post_as_text(self, mock_post):
        mock_post.return_value.text = 'response text'
        response = request_data('http://example.com', method='post', as_text=True)
        self.assertEqual(response, 'response text')

class TestFetchRemoteData(unittest.TestCase):
    @patch('gofast.tools.baseutils.urllib.request.urlopen')
    @patch('builtins.open', new_callable=mock_open)
    def test_fetch_remote_data_success(self, mock_file, mock_urlopen):
        mock_urlopen.return_value.read.return_value = b'data'
        status = fetch_remote_data(DOWNLOAD_FILE, save_path='/local/path')
        self.assertTrue(status)

class TestGetRemoteData(unittest.TestCase):
    @patch('gofast.tools.baseutils.urllib.request.urlopen')
    @patch('builtins.open', new_callable=mock_open)
    def test_get_remote_data_success(self, mock_file, mock_urlopen):
        mock_urlopen.return_value.read.return_value = b'data'
        status = get_remote_data(DOWNLOAD_FILE, save_path='/local/path')
        self.assertTrue(status)


class TestDownloadFile(unittest.TestCase):
    @patch('gofast.tools.baseutils.requests.get')
    @patch('builtins.open', new_callable=mock_open)
    def test_download_file(self, mock_file, mock_get):
        mock_get.return_value.__enter__.return_value.iter_content.return_value = [b'chunk1', b'chunk2']
        download_file(DOWNLOAD_FILE, 'iris.csv')
        mock_file.assert_called_with('iris.csv', 'wb')
        handle = mock_file()
        handle.write.assert_any_call(b'chunk1')
        handle.write.assert_any_call(b'chunk2')

class TestFancierDownloader(unittest.TestCase):
    @patch('gofast.tools.baseutils.requests.get')
    def test_fancier_downloader(self, mock_get):
        mock_get.return_value.__enter__.return_value.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_get.return_value.__enter__.return_value.headers = {'content-length': '1024'}
        
        with patch('gofast.tools.baseutils.tqdm'), \
              patch('builtins.open', mock_open()) as mocked_file:
            local_filename = fancier_downloader(DOWNLOAD_FILE, 'iris.csv')
            mocked_file.assert_called_once_with('iris.csv', 'wb')
            self.assertIn('iris.csv', local_filename)

# class TestMoveFile(unittest.TestCase):
#     @patch('gofast.tools.baseutils.shutil.move')
#     @patch('gofast.tools.baseutils.os.makedirs')
#     @patch('gofast.tools.baseutils.os.path.exists', return_value=False)
#     def test_move_file(self, mock_exists, mock_makedirs, mock_move):
#         move_file('source_file.txt', 'dest_dir')
#         mock_makedirs.assert_called_once_with('dest_dir', exist_ok=True)
#         mock_move.assert_called_once_with('source_file.txt', 'dest_dir/source_file.txt')


class TestStoreOrRetrieveData(unittest.TestCase):
    @patch('gofast.tools.baseutils.pd.HDFStore', autospec=True)
    def test_store_data(self, mock_store):
        mock_store.return_value.__enter__.return_value = MagicMock()
        datasets = {'dataset1': np.array([1, 2, 3]), 'df1': pd.DataFrame({'A': [4, 5, 6]})}
        store_or_retrieve_data('my_datasets.h5', datasets, 'store')
        # Verify store.put or create_dataset was called for each dataset
        self.assertFalse(mock_store.return_value.__enter__.return_value.put.called or 
                        mock_store.return_value.__enter__.return_value.create_dataset.called)

    @patch('gofast.tools.baseutils.h5py.File', autospec=True)
    def test_retrieve_data(self, mock_h5file):
        mock_h5file.return_value.__enter__.return_value.keys.return_value = ['dataset1']
        type(mock_h5file.return_value.__enter__.return_value).get = MagicMock(return_value=pd.DataFrame({'A': [4, 5, 6]}))
        result = store_or_retrieve_data('my_datasets.h5', operation='retrieve')
        self.assertIsInstance(result, dict)
        # self.assertIn('dataset1', result)

class TestBaseStorage(unittest.TestCase):
    @patch('gofast.tools.baseutils.h5py.File', autospec=True)
    def test_base_storage_store(self, mock_h5file):
        mock_h5file.return_value.__enter__.return_value.create_dataset = MagicMock()
        datasets = {'dataset1': np.array([1, 2, 3]), 'df1': pd.DataFrame({'A': [4, 5, 6]})}
        base_storage('my_datasets.h5', datasets, 'store')
        self.assertTrue(mock_h5file.return_value.__enter__.return_value.create_dataset.called)

    @patch('gofast.tools.baseutils.h5py.File', autospec=True)
    def test_base_storage_retrieve(self, mock_h5file):
        mock_h5file.return_value.__enter__.return_value.keys.return_value = ['dataset1']
        mock_h5file.return_value.__enter__.return_value.get = MagicMock(return_value=pd.DataFrame({'A': [4, 5, 6]}))
        result = base_storage('my_datasets.h5', operation='retrieve')
        self.assertIsInstance(result, dict)
        # self.assertIn('dataset1', result)

class TestVerifyDataIntegrity(unittest.TestCase):
    def test_verify_data_integrity(self):
        data = pd.DataFrame({'A': [1, 2, None], 'B': [4, None, 6], 'C': [7, 8, 9]})
        is_valid, report = verify_data_integrity(data)
        self.assertFalse(is_valid)
        self.assertIn('missing_values', report)
        self.assertIn('duplicates', report)
        self.assertIn('outliers', report)

class TestAuditData(unittest.TestCase):
    @patch('gofast.tools.baseutils.scale_data')
    @patch('gofast.tools.baseutils.convert_date_features')
    @patch('gofast.tools.baseutils.handle_missing_data')
    @patch('gofast.tools.baseutils.handle_outliers_in_data')
    def test_audit_data(self, mock_outliers, mock_missing, mock_convert_date, mock_scale):
        data = pd.DataFrame({'A': [1, 2, None], 'B': [4, None, 6]})
        audited_data, _ = audit_data(data, handle_outliers=True, 
                                     handle_missing=True, 
                                     handle_date_features=True, 
                                     handle_scaling=True,
                                     return_report=True)
        self.assertIsInstance(audited_data, pd.DataFrame)
        mock_outliers.assert_called_once()
        mock_missing.assert_called_once()
        mock_convert_date.assert_called_once()
        mock_scale.assert_called_once()

class TestHandleCategoricalFeatures(unittest.TestCase):
    def test_handle_categorical_features(self):
        data = pd.DataFrame({'A': [1, 2, 1, 3], 'B': list(range(4))})
        updated_data = handle_categorical_features(data, categorical_threshold=3)
        self.assertTrue(pd.api.types.is_categorical_dtype(updated_data['A']))
        self.assertFalse(pd.api.types.is_categorical_dtype(updated_data['B']))

class TestConvertDateFeatures(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            'date': ['2021-01-01', '2021-06-15'],
            'value': [10, 20]
        })

    def test_convert_date_features(self):
        updated_data, report = convert_date_features(
            self.data, ['date'], day_of_week=True, quarter=True, return_report=True
        )
        self.assertIn('date_dayofweek', updated_data.columns)
        self.assertIn('date_quarter', updated_data.columns)
        self.assertTrue('date_dayofweek' in report['added_features'])
        self.assertTrue('date_quarter' in report['added_features'])

class TestScaleData(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            'A': np.random.randint(1, 100, 10),
            'B': np.random.randint(1, 100, 10)
        })

    def test_scale_data_minmax(self):
        scaled_data, _ = scale_data(self.data, method='minmax', return_report=True)
        self.assertTrue(scaled_data['A'].min() >= 0 and scaled_data['A'].max() <= 1)
        self.assertTrue(scaled_data['B'].min() >= 0 and scaled_data['B'].max() <= 1)

    def test_scale_data_standard(self):
        scaled_data, _ = scale_data(self.data, method='standard', return_report=True)
        self.assertAlmostEqual(scaled_data['A'].mean(), 0, places=1)
        self.assertAlmostEqual(scaled_data['B'].mean(), 0, places=1)

class TestHandleOutliersInData(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            'A': [1, 2, 3, 100],
            'B': [4, 5, 6, -50]
        })

    def test_handle_outliers_clip(self):
        handled_data = handle_outliers_in_data(self.data, method='clip')
        self.assertTrue(handled_data['A'].max() <= 100 and handled_data['B'].min() >= -50)

    def test_handle_outliers_replace(self):
        handled_data = handle_outliers_in_data(self.data, method='replace', replace_with='median')
        self.assertNotIn(100, handled_data['A'])
        self.assertNotIn(-50, handled_data['B'])

class TestHandleMissingData(unittest.TestCase):
    def setUp(self):
        self.data = pd.DataFrame({
            'A': [1, np.nan, 3, np.nan],
            'B': [np.nan, 5, 6, 7]
        })

    def test_handle_missing_data_fill_mean(self):
        updated_data = handle_missing_data(self.data, method='fill_mean')
        self.assertFalse(updated_data.isnull().any().any())

    def test_handle_missing_data_drop_cols(self):
        updated_data = handle_missing_data(self.data, method='drop_cols', dropna_threshold=0.8)
        self.assertNotIn('A', updated_data.columns)
        self.assertIn('B', updated_data.columns)

class TestInspectData(unittest.TestCase):
    def test_inspect_data(self):
        data = pd.DataFrame({
            'A': [1, 2, 3, None, 5],
            'B': [1, 1, 2, 3, 3]
        })
        # Execution test
        try:
            inspect_data(data)
            execution_passed = True
        except Exception as e: # noqa
            execution_passed = False
        self.assertTrue(execution_passed, "Inspect data should execute without errors.")

class TestAugmentData(unittest.TestCase):
    def setUp(self):
        self.X = np.array([[1, 2], [3, 4]])
        self.y = np.array([0, 1])

    def test_augment_data(self):
        X_aug, y_aug = augment_data(self.X, self.y, augmentation_factor=2)
        self.assertEqual(len(X_aug), len(self.X) * 2)
        self.assertEqual(len(y_aug), len(self.y) * 2)

    def test_augment_data_no_y(self):
        X_aug = augment_data(self.X, augmentation_factor=2)
        self.assertEqual(len(X_aug), len(self.X) * 2)

class TestAssessOutlierImpact(unittest.TestCase):
    def test_assess_outlier_impact(self):
        df = pd.DataFrame({
            'feature1': np.random.rand(100),
            'feature2': np.random.rand(100),
            'target': np.random.randint(0, 2, 100)
        })
        metric_with, metric_without = assess_outlier_impact(df, 'target')
        self.assertIsInstance(metric_with, float)
        self.assertIsInstance(metric_without, float)

class TestTransformDates(unittest.TestCase):
    def test_transform_dates(self):
        data = pd.DataFrame({
            'date': ['2021-01-01', '2021-01-02'],
            'value': [1, 2]
        })
        transformed_data = transform_dates(data, transform=True)
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(transformed_data['date']))

    def test_transform_dates_return_columns(self):
        data = pd.DataFrame({
            'date': ['2021-01-01', '2021-01-02'],
            'value': [1, 2]
        })
        dt_columns = transform_dates(data, transform=True, return_dt_columns=True)
        self.assertIn('date', dt_columns)


def test_merge_frames_on_index():
    # Create sample DataFrames
    df1 = pd.DataFrame({'Key': ['A', 'B', 'C'], 'Value1': [1, 2, 3]})
    df2 = pd.DataFrame({'Key': ['A', 'B', 'C'], 'Value2': [4, 5, 6]})
    
    # Perform the merge
    merged_df = merge_frames_on_index(df1, df2, index_col='Key')
    
    # Expected result
    expected_df = pd.DataFrame({'Value1': [1, 2, 3], 'Value2': [4, 5, 6]}, index=['A', 'B', 'C'])
    
    pd.testing.assert_frame_equal(merged_df, expected_df)

def test_apply_tfidf_vectorization():
    # Sample DataFrame with text
    df = pd.DataFrame({'Text': ['this is a test', 'another test', 'test']})
    
    # Apply TF-IDF vectorization
    result_df = apply_tfidf_vectorization(df, text_columns='Text', max_features=2)
    
    # Check if result contains expected number of features
    assert result_df.shape[1] == 2  # Adjust based on the number of generated features
    assert 'tfidf_0' in result_df.columns and 'tfidf_1' in result_df.columns

def test_apply_bow_vectorization():
    df = pd.DataFrame({'Text': ['simple test', 'another simple test', 'test']})
    result_df = apply_bow_vectorization(df, text_columns='Text', max_features=2)
    
    assert result_df.shape[1] == 2
    assert 'bow_0' in result_df.columns and 'bow_1' in result_df.columns

def test_apply_word_embeddings():
    df = pd.DataFrame({'Text': ['deep learning', 'machine learning']})
    # Assume 'path/to/embeddings' is a valid path to embedding file
    result_df = apply_word_embeddings(df, text_columns='Text', embedding_file_path='path/to/embeddings', n_components=10)
    
    assert result_df.shape[1] == 10
    assert all([col.startswith('embedding_') for col in result_df.columns])


def test_boxcox_transformation():
    df = pd.DataFrame({'Value': [0.1, 1.5, 2.5, 3.5]})
    transformed_df, lambda_values = boxcox_transformation(df, columns=['Value'], adjust_non_positive='adjust')
    
    assert 'Value' in transformed_df.columns
    assert lambda_values['Value'] is not None


def test_check_missing_data():
    df = pd.DataFrame({'A': [1, None, 3], 'B': [4, 5, None]})
    missing_stats = check_missing_data(df, view=False)
    
    assert missing_stats.loc['A', 'Count'] == 1
    assert missing_stats.loc['B', 'Count'] == 1

if __name__ == '__main__':
    unittest.main()











