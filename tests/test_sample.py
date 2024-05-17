import sys
import os
import pytest
import pandas as pd
import numpy as np
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.main import DataProcessor, run

# Paths for test data files
product_test_path = 'data/sales_product.csv'
brand_test_path = 'data/sales_brand.csv'
output_path = 'output/results.json'


@pytest.fixture
def data_processor():
    """
    Fixture to create a DataProcessor instance with appropriate CSV file paths.

    Returns:
        DataProcessor: An instance of the DataProcessor class.
    """
    return DataProcessor(product_test_path, brand_test_path)


def test_df_to_json(data_processor):
    """
    Test the df_to_json method to ensure it converts dataframes to JSON and writes to a file.

    Args:
        data_processor (DataProcessor): Fixture for DataProcessor instance.
    """
    product_df = pd.read_csv(product_test_path, parse_dates=['week_commencing_date'], dayfirst=True)
    brand_df = pd.read_csv(brand_test_path, parse_dates=['week_commencing_date'], dayfirst=True)
    product_df, brand_df = data_processor.process_data()

    data_processor.df_to_json(product_df, brand_df)

    assert os.path.exists(output_path)

    with open(output_path, 'r') as f:
        content = f.read()
        assert '"PRODUCT"' in content
        assert '"BRAND"' in content


def test_convert_date_to_string(data_processor):
    """
    Test the _convert_date_to_string method to ensure it correctly converts date columns to string format.

    Args:
        data_processor (DataProcessor): Fixture for DataProcessor instance.
    """
    df = pd.read_csv(product_test_path, parse_dates=['week_commencing_date'], dayfirst=True)
    df = data_processor._convert_date_to_string(df, 'week_commencing_date')
    assert df['week_commencing_date'].iloc[0] == '04/07/2021'


def test_prepare_data(data_processor):
    """
    Test the _prepare_data method to ensure it correctly processes and prepares the data.

    Args:
        data_processor (DataProcessor): Fixture for DataProcessor instance.
    """
    df = data_processor._prepare_data(product_test_path, ['barcode_no', 'product_name'],
                                      defaultdict(lambda: object, period_id=np.int32, gross_sales=np.float64,
                                                  units_sold=np.int32, prev_gross_sales=np.float64,
                                                  prev_units_sold=np.int32, barcode_no=str))
    assert 'previous_week_commencing_date' in df.columns
    assert 'prev_gross_sales' in df.columns
    assert (df['period_name'] == 'current').all()


def test_calc_growth(data_processor):
    """
    Test the _calc_growth method to ensure it correctly calculates the growth metrics.

    Args:
        data_processor (DataProcessor): Fixture for DataProcessor instance.
    """
    df = data_processor._prepare_data(product_test_path, ['barcode_no', 'product_name'],
                                      defaultdict(lambda: object, period_id=np.int32, gross_sales=np.float64,
                                                  units_sold=np.int32, prev_gross_sales=np.float64,
                                                  prev_units_sold=np.int32, barcode_no=str))
    df = data_processor._calc_growth(df)
    assert 'perc_gross_sales_growth' in df.columns
    assert 'perc_unit_sales_growth' in df.columns
    assert df['perc_gross_sales_growth'].iloc[0] == pytest.approx(108.81)
    assert df['perc_unit_sales_growth'].iloc[0] == pytest.approx(123.08)


def test_drop_columns_and_reorder(data_processor):
    """
    Test the _drop_columns_and_reorder method to ensure it correctly drops and reorders columns.

    Args:
        data_processor (DataProcessor): Fixture for DataProcessor instance.
    """
    df = data_processor._prepare_data(product_test_path, ['barcode_no', 'product_name'],
                                      defaultdict(lambda: object, period_id=np.int32, gross_sales=np.float64,
                                                  units_sold=np.int32, prev_gross_sales=np.float64,
                                                  prev_units_sold=np.int32, barcode_no=str))
    df = data_processor._calc_growth(df)
    df = data_processor._drop_columns_and_reorder(df, ['barcode_no', 'product_name'])
    assert set(df.columns) == {'barcode_no', 'product_name', 'current_week_commencing_date',
                               'previous_week_commencing_date', 'perc_gross_sales_growth',
                               'perc_unit_sales_growth'}


def test_column_datatypes(data_processor):
    """
    Test to check if the DataFrame columns are the correct datatype.

    Args:
        data_processor (DataProcessor): Fixture for DataProcessor instance.
    """
    df = data_processor._prepare_data(product_test_path, ['barcode_no', 'product_name'],
                                      defaultdict(lambda: object, period_id=np.int32, gross_sales=np.float64,
                                                  units_sold=np.int32, prev_gross_sales=np.float64,
                                                  prev_units_sold=np.int32, barcode_no=str))
    expected_dtypes = {
        'barcode_no': 'object',
        'product_name': 'object',
        'current_week_commencing_date': 'datetime64[ns]',
        'previous_week_commencing_date': 'datetime64[ns]',
        'gross_sales': 'float64',
        'units_sold': 'int32',
        'prev_gross_sales': 'float64',
        'prev_units_sold': 'int32',
        'period_id': 'int32',
        'period_name': 'object'
    }

    actual_dtypes = df.dtypes.to_dict()

    for column, dtype in expected_dtypes.items():
        assert actual_dtypes[
                   column] == dtype, f"Column {column} has incorrect datatype {actual_dtypes[column]}, expected {dtype}"


def test_run():
    """
    Test the run function to ensure it executes the data processing and prints the expected output.
    """
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)

    run(product_test_path, brand_test_path)

    # Check if output file is created
    assert os.path.exists(output_path)

    with open(output_path, 'r') as f:
        content = f.read()
        assert '"PRODUCT"' in content
        assert '"BRAND"' in content





