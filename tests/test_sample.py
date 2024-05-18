import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.main import *
from src.BrandProcessor import *
from src.ProductProcessor import *

# Paths for test data files
product_test_path = 'data/sales_product.csv'
brand_test_path = 'data/sales_brand.csv'
output_path = 'output/results.json'


@pytest.fixture
def data_processors() -> tuple[ProductProcessor, BrandProcessor]:
    """
    Fixture to create a DataProcessor instance with appropriate CSV file paths.

    Returns:
        tuple[ProductProcessor, BrandProcessor]: A tuple of instances for ProductProcessor and BrandProcessor classes.
    """
    return ProductProcessor(product_test_path), BrandProcessor(brand_test_path)


def test_merge_data(data_processors):
    """
    Test the _merge_data method to ensure it correctly merges previous and current data periods with additional columns.

    Args:
        data_processors (tuple[ProductProcessor, BrandProcessor]): A tuple of instances for ProductProcessor and
        BrandProcessor classes.
    """
    product_test_processor = data_processors[0]
    product_test_processor._merge_data()
    assert 'previous_week_commencing_date' in product_test_processor._data_frame.columns
    assert 'prev_gross_sales' in product_test_processor._data_frame.columns
    assert (product_test_processor._data_frame['period_name'] == 'current').all()


def test_convert_date_to_string(data_processors):
    """
    Test the _convert_date_to_string method to ensure it correctly converts date columns to string format, by checking
    both before and after running the method.

    Args:
        data_processors (tuple[ProductProcessor, BrandProcessor]): A tuple of instances for ProductProcessor and
        BrandProcessor classes.
    """
    product_test_processor = data_processors[0]
    assert product_test_processor._data_frame['week_commencing_date'].dtype == 'datetime64[ns]'
    product_test_processor._convert_date_to_string(['week_commencing_date'])
    assert product_test_processor._data_frame['week_commencing_date'].dtype == 'object'


def test_calc_growth(data_processors):
    """
    Test the _calc_growth method to ensure it correctly calculates the growth metrics, producing 2 additional columns.

    Args:
        data_processors (tuple[ProductProcessor, BrandProcessor]): A tuple of instances for ProductProcessor and
        BrandProcessor classes.
    """
    product_test_processor = data_processors[0]
    product_test_processor._merge_data()
    product_test_processor._calc_growth()
    product_test_processor._sort_rows()
    assert 'perc_gross_sales_growth' in product_test_processor._data_frame.columns
    assert 'perc_unit_sales_growth' in product_test_processor._data_frame.columns
    assert product_test_processor._data_frame['perc_gross_sales_growth'].iloc[0] == pytest.approx(19.93)
    assert product_test_processor._data_frame['perc_unit_sales_growth'].iloc[0] == pytest.approx(52.63)


def test_drop_columns_and_reorder(data_processors):
    """
    Test the _drop_columns and reorder_columns methods to ensure the dataframe is in the specified format

    Args:
        data_processors (tuple[ProductProcessor, BrandProcessor]): A tuple of instances for ProductProcessor and
        BrandProcessor classes.
    """
    product_test_processor = data_processors[0]
    product_test_processor._merge_data()
    product_test_processor._calc_growth()
    product_test_processor._drop_columns()
    product_test_processor._reorder_columns()
    product_test_processor._sort_rows()

    assert set(product_test_processor._data_frame.columns) == {'barcode_no', 'product_name',
                                                               'current_week_commencing_date',
                                                               'previous_week_commencing_date',
                                                               'perc_gross_sales_growth', 'perc_unit_sales_growth'}


def test_column_datatypes(data_processors):
    """
    Test to check if the DataFrame columns are the correct datatype.

    Args:
        data_processors (tuple[ProductProcessor, BrandProcessor]): A tuple of instances for ProductProcessor and
        BrandProcessor classes.
    """
    product_test_processor = data_processors[0]
    product_test_processor._merge_data()
    product_test_processor._calc_growth()

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

    actual_dtypes = product_test_processor._data_frame.dtypes.to_dict()

    for column, dtype in expected_dtypes.items():
        assert actual_dtypes[
                   column] == dtype, f"Column {column} has incorrect datatype {actual_dtypes[column]}, expected {dtype}"


def test_merge_and_dict_to_json(data_processors: tuple[ProductProcessor, BrandProcessor]) -> None:
    """
    Test the merge_dict and dict_to_json methods to ensure the two dictionaries are merged, converted to JSON and
    written to a file in the correct structure.

    Args:
        data_processors (tuple[ProductProcessor, BrandProcessor]): A tuple of instances for ProductProcessor and
        BrandProcessor classes.
    """
    product_processor = data_processors[0]
    brand_processor = data_processors[1]
    product_test_df = product_processor.prepare_dataframe()
    brand_test_df = brand_processor.prepare_dataframe()
    merged_data = merge_dict(product_test_df, brand_test_df)
    dict_to_json(merged_data, output_path)

    assert os.path.exists(output_path)

    with open(output_path, 'r') as f:
        content = f.read()
        assert '"PRODUCT"' in content
        assert '"BRAND"' in content


def test_run():
    """
    Test the run function to ensure it executes the data processing and prints the expected output.
    """
    # Ensure output directory exists
    os.makedirs('output', exist_ok=True)

    run(product_test_path, brand_test_path, output_path)

    # Check if output file is created
    assert os.path.exists(output_path)

    with open(output_path, 'r') as f:
        content = f.read()
        assert '"PRODUCT"' in content
        assert '"BRAND"' in content





