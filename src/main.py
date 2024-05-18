from collections import defaultdict
import pandas as pd
import numpy as np
import simplejson


class DataProcessor:
    """
    An abstract class used as a superclass for BrandProcessor and ProductProcessor subclasses, providing a framework to
    process specific data sets.

    Attributes:
        _data_path (str): The file path for the sales data CSV.
        _data_frame (DataFrame): Data is loaded as a dataframe and stored.
        _column_data_types (None): Data types for each column, specified in SubClass constructors.
        _columns_to_drop (list): Columns that will be dropped before exporting to a JSON.
        _new_column_order (list): The order in which the columns should appear in the JSON file.
        _merge_on_columns (list): Columns that should be compared when merging previous and current period data.
        _values_to_merge (list): The columns that will be merged between previous and current period data.
    """

    def __init__(self, path: str):
        """
        Initializes the DataProcessor class with a path to the data file.

        Parameters:
            path (str): Path to the data CSV file.
        """
        self._data_path = path
        self._data_frame = self._load_data()
        self._column_data_types = None
        self._columns_to_drop = ['period_id', 'period_name', 'gross_sales', 'units_sold', 'prev_gross_sales',
                                 'prev_units_sold']
        self._new_column_order = ['current_week_commencing_date', 'previous_week_commencing_date',
                                  'perc_gross_sales_growth', 'perc_unit_sales_growth']
        self._merge_on_columns = ['period_id', 'period_name', 'previous_week_commencing_date',
                                  'current_week_commencing_date']
        self._values_to_merge = ['period_id', 'period_name', 'prev_gross_sales', 'prev_units_sold',
                                 'previous_week_commencing_date', 'current_week_commencing_date']

    @staticmethod
    def process_dataframe(path: str) -> dict:
        pass

    def prepare_dataframe(self) -> dict:
        """
        Processes the product and brand data files, calculates growth metrics, and prepares the data for JSON
        conversion.

        Returns:
            dict: A dictionary containing a converted pd.DataFrame.
        """
        self._merge_data()
        self._calc_growth()
        self._drop_columns()
        self._reorder_columns()
        self._sort_rows()
        self._convert_date_to_string(['current_week_commencing_date', 'previous_week_commencing_date'])
        return self._return_dict()

    def _load_data(self) -> pd.DataFrame:
        """
        Reads a CSV file based on a given path, identifies the dates column and formats accordingly.

        Returns:
            pd.DataFrame: The dataframe containing the CSV data.
        """
        return pd.read_csv(self._data_path, parse_dates=['week_commencing_date'], dayfirst=True)

    def _merge_data(self) -> None:
        """
        - Creates a local dataframe, which is a subset of _data_frame, which is filtered by 'previous' on
        'period name'.
        - An additional column is added to _data_frame 'previous_week_commencing_date' which calculates the
        correlating week_commencing_date in the previous period.
        - To prevent any data collisions, certain columns are renamed in _data_frame and df_previous.
        - df_previous is then updated to correlate to the 'previous_week_commencing_date', 'prev_gross_sales' and
        'prev_units_sold' in the 'current' data period in _data_frame.
        - The two dataframes are then merged using 'outer' which essentially fills in date periods of which either no
        previous or no current sales data was recorded.
        """
        df_previous = self._data_frame[self._data_frame['period_name'] == 'previous']
        self._data_frame['previous_week_commencing_date'] = self._data_frame['week_commencing_date'] - pd.DateOffset(
            years=1)
        self._data_frame = self._data_frame.rename(columns={'week_commencing_date': 'current_week_commencing_date'})
        df_previous = df_previous.rename(columns={'week_commencing_date': 'previous_week_commencing_date',
                                                  'gross_sales': 'prev_gross_sales', 'units_sold': 'prev_units_sold'})

        df_previous['current_week_commencing_date'] = df_previous['previous_week_commencing_date'] + pd.DateOffset(years=1)
        df_previous['period_name'] = 'current'
        df_previous['period_id'] = 2

        self._data_frame = pd.merge(self._data_frame, df_previous[self._values_to_merge], how='outer',
                                     on=self._merge_on_columns)
        self._data_frame = self._data_frame.fillna(0)
        self._data_frame = self._data_frame.astype(self._column_data_types)
        self._data_frame = self._data_frame[self._data_frame['period_name'] == 'current']

    def _calc_growth(self) -> None:
        """
        Calculates growth metrics for the data stored in _data_frame using the following formula:

        % Growth = ((Current Week's Sales - Previous Week's Sales) / Previous Week's Sales) * 100

        To prevent a division error, this formula is only applied where there were previous weekly sales.
        """
        self._data_frame['perc_gross_sales_growth'] = np.where(self._data_frame['prev_gross_sales'] > 0, np.round(((self._data_frame['gross_sales'] - self._data_frame['prev_gross_sales']) / self._data_frame['prev_gross_sales']) * 100, 2), None)
        self._data_frame['perc_unit_sales_growth'] = np.where(self._data_frame['prev_units_sold'] > 0, np.round(((self._data_frame['units_sold'] - self._data_frame['prev_units_sold']) / self._data_frame['prev_units_sold']) * 100, 2), None)

    def _reorder_columns(self) -> None:
        """
        Reorders columns in the order specified in _new_column_order.
        """
        self._data_frame = self._data_frame.reindex(columns=self._new_column_order)

    def _sort_rows(self):
        pass

    def _convert_date_to_string(self, column_name: list) -> None:
        """
        Converts specified date columns in _data_frame to string format.

        Parameters:
            column_name (list): The list of all the columns to be converted to a string format.
        """
        for each in column_name:
            self._data_frame[each] = self._data_frame[each].dt.strftime('%d/%m/%Y')

    def _drop_columns(self) -> None:
        """
        Drops the columns of _data_frame specified in _columns_to_drop.
        """
        self._data_frame.drop(self._columns_to_drop, axis=1)

    def _return_dict(self):
        """
        Converts and returns _data_frame as a dictionary.

        Returns:
            dict: _data_frame as a dictionary
        """
        return self._data_frame.to_dict(orient='records')


class BrandProcessor(DataProcessor):
    """
    A Subclass of DataProcessor, specifically designed to process brand data.

    Attributes (In addition to DataProcessor attributes):
        __data_specific_attributes (list):

    The following attributes have also been updated to include __data_specific_attributes:
        _new_column_order (list)
        _column_data_types (list)
        _merge_on_columns (list)
        _values_to_merge (list)
    """

    def __init__(self, path: str):
        """
        Initializes the BrandProcessor class with a path to the brand data file.

        Parameters:
            path (str): Path to the brand data CSV file.
        """
        super().__init__(path)
        self.__data_specific_attributes = ['brand_id', 'brand']
        self._new_column_order = self.__data_specific_attributes + self._new_column_order
        self._column_data_types = defaultdict(lambda: object, period_id=np.int32, gross_sales=np.float64,
                                              units_sold=np.int32, brand_id=np.int32, prev_gross_sales=np.float64,
                                              prev_units_sold=np.int32)
        self._merge_on_columns += self.__data_specific_attributes
        self._values_to_merge += self.__data_specific_attributes

    @staticmethod
    def process_dataframe(path: str) -> dict:
        """
        Factory method used to create an instance of Product processor and run the prepare_dataframe method which
        returns a sorted dictionary of the product dataframe.

        Parameters:
            path (str): Path to the product data CSV file.

        Returns:
            dict: A dictionary containing a converted pd.DataFrame.
        """
        brand_processor = BrandProcessor(path)
        return brand_processor.prepare_dataframe()

    def _reorder_columns(self) -> None:
        """
        Reorders columns in the order specified in _new_column_order (Overrides method in DataProcessor class). Also
        renames 'brand' column to comply with format specification.
        """
        self._data_frame = self._data_frame.reindex(columns=self._new_column_order)
        self._data_frame = self._data_frame.rename(columns={'brand': 'brand_name'})

    def _sort_rows(self) -> None:
        """
        Sorts rows by 'brand_name' and 'current_week_commencing_date'.
        """
        self._data_frame = self._data_frame.sort_values(['brand_name', 'current_week_commencing_date'])


class ProductProcessor(DataProcessor):
    """
    A Subclass of DataProcessor, specifically designed to process product data.

    Attributes (In addition to DataProcessor attributes):
        __data_specific_attributes (list):

    The following attributes have also been updated to include __data_specific_attributes:
        _new_column_order (list)
        _column_data_types (list)
        _merge_on_columns (list)
        _values_to_merge (list)
    """

    def __init__(self, path: str):
        """
        Initializes the ProductProcessor class with a path to the product data file.

        Parameters:
            path (str): Path to the product data CSV file.
        """
        super().__init__(path)
        self.__data_specific_attributes = ['barcode_no', 'product_name']
        self._new_column_order = self.__data_specific_attributes + self._new_column_order
        self._column_data_types = defaultdict(lambda: object, period_id=np.int32, gross_sales=np.float64,
                                               units_sold=np.int32, prev_gross_sales=np.float64,
                                               prev_units_sold=np.int32, barcode_no=str)
        self._merge_on_columns += self.__data_specific_attributes
        self._values_to_merge += self.__data_specific_attributes

    @staticmethod
    def process_dataframe(path: str) -> dict:
        """
        Factory method used to create an instance of Product processor and run the prepare_dataframe method which
        returns a sorted dictionary of the product dataframe.

        Parameters:
            path (str): Path to the product data CSV file.

        Returns:
            dict: A dictionary containing a converted pd.DataFrame.
        """
        product_processor = ProductProcessor(path)
        return product_processor.prepare_dataframe()

    def _sort_rows(self) -> None:
        """
        Sorts rows by 'product_name' and 'current_week_commencing_date'.
        """
        self._data_frame = self._data_frame.sort_values(['product_name', 'current_week_commencing_date'])


def merge_dict(dict_p: dict, dict_b: dict) -> dict:
    return {'PRODUCT': dict_p, 'BRAND': dict_b}


def dict_to_json(dict_combined: dict, output_path) -> None:
    with open(output_path, 'w') as results_json:
        simplejson.dump(dict_combined, results_json, indent=4, ignore_nan=True)


def run(prod_path='../data/sales_product.csv', brand_path='../data/sales_brand.csv',
        output_path='../output/results.json') -> None:
    """
    Runs the data processing, by calling the factory method for both subclasses, which returns the data in a dictionary.
    The dictionaries are then combined, producing a JSON file in the output directory.
    """
    product_dict = ProductProcessor.process_dataframe(prod_path)
    brand_dict = BrandProcessor.process_dataframe(brand_path)
    merged_data = merge_dict(product_dict, brand_dict)
    dict_to_json(merged_data, output_path)


if __name__ == "__main__":
    run()
