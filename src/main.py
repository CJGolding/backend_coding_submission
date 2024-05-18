from collections import defaultdict
import pandas as pd
import numpy as np
import simplejson


class DataProcessor:
    """
    A class to process product and brand sales data, calculate growth metrics, and export results to JSON.

    Attributes:
        product_data_path (str): The file path for the product sales data CSV.
        brand_data_path (str): The file path for the brand sales data CSV.
    """
    def __init__(self, path: str):
        """
        Initializes the DataProcessor class with a path to the data file.

        Parameters:
            path (str): Path to the data CSV file.
        """
        self.data_path = path
        self.data_frame = None
        self.column_data_types = None
        self.data_specific_attributes = None
        self.default_columns = ['period_id', 'period_name']
        self.columns_to_drop = self.default_columns + ['gross_sales', 'units_sold', 'prev_gross_sales', 'prev_units_sold']
        self.new_column_order = ['current_week_commencing_date', 'previous_week_commencing_date',
                                 'perc_gross_sales_growth', 'perc_unit_sales_growth']
        self.merge_on_columns = self.default_columns + ['previous_week_commencing_date', 'current_week_commencing_date']
        self.values_to_merge = self.default_columns + ['prev_gross_sales', 'prev_units_sold',
                                                       'previous_week_commencing_date', 'current_week_commencing_date']


    def _load_data(self):
        self.data_frame = pd.read_csv(self.data_path, parse_dates=['week_commencing_date'], dayfirst=True)

    def _merge_data(self):
        df_previous = self.data_frame[self.data_frame['period_name'] == 'previous']
        self.data_frame['previous_week_commencing_date'] = self.data_frame['week_commencing_date'] - pd.DateOffset(
            years=1)
        self.data_frame.rename(columns={'week_commencing_date': 'current_week_commencing_date'})
        df_previous = df_previous.rename(columns={'week_commencing_date': 'previous_week_commencing_date',
                                                  'gross_sales': 'prev_gross_sales',
                                                  'units_sold': 'prev_units_sold'})

        df_previous['current_week_commencing_date'] = df_previous['previous_week_commencing_date'] + pd.DateOffset(
            years=1)
        df_previous['period_name'] = 'current'
        df_previous['period_id'] = 2
        self.data_frame.merge(df_previous[self.values_to_merge], how='outer', on=self.merge_on_columns)
        self.data_frame.fillna(0)
        self.data_frame.astype(self.column_data_types)
        self.data_frame = self.data_frame[self.data_frame['period_name'] == 'current']

    def _calc_growth(self) -> None:
        """
        Calculates growth metrics for the data.

        Parameters:
            df (pd.DataFrame): The DataFrame containing sales data.

        Returns:
            pd.DataFrame: The DataFrame with growth metrics added.
        """
        self.data_frame['perc_gross_sales_growth'] = np.where(self.data_frame['prev_gross_sales'] > 0, np.round(((self.data_frame['gross_sales'] - self.data_frame['prev_gross_sales']) / self.data_frame['prev_gross_sales']) * 100, 2), None)
        self.data_frame['perc_unit_sales_growth'] = np.where(self.data_frame['prev_units_sold'] > 0, np.round(((self.data_frame['units_sold'] - self.data_frame['prev_units_sold']) / self.data_frame['prev_units_sold']) * 100, 2), None)

    @staticmethod
    def prepare_dataframe(path):
        pass

    def _reorder_columns(self) -> None:
        self.data_frame.reindex(columns=self.new_column_order)

    def _sort_rows(self):
        pass

    def _df_to_dict(self):
        self.dict = self.data_frame.to_dict(orient='records')


    def df_to_json(self, product: pd.DataFrame, brand: pd.DataFrame) -> None:
        """
        Converts product and brand DataFrames to JSON and writes to a file in the output directory.

        Parameters:
            product (pd.DataFrame): The processed product data.
            brand (pd.DataFrame): The processed brand data.
        """

        dict_product = product.sort_values(['product_name', 'current_week_commencing_date']).to_dict(orient='records')
        dict_brand = brand.sort_values(['brand_name', 'current_week_commencing_date']).to_dict(orient='records')
        dict_combined = {'PRODUCT': dict_product, 'BRAND': dict_brand}
        with open('C:/Users/goldi/backend-coding-challenge/output/results.json', 'w') as results_json:
            simplejson.dump(dict_combined, results_json, indent=4, ignore_nan=True)

    def _convert_date_to_string(self, column_name: list) -> None:
        """
        Converts date columns in the DataFrame to string format, readable in a JSON file.

        Parameters:
            df (pd.DataFrame): The DataFrame containing date columns.
            current_format(str): The name format of the first date column (accepts'current_week_commencing_date' or
            'week_commencing_date')

        Returns:
            pd.DataFrame: The DataFrame with date columns converted to string format.
        """
        for each in column_name:
            self.data_frame[each] = self.data_frame[each].dt.strftime('%d/%m/%Y')

    def _drop_columns(self) -> None:
        """
        Drops unnecessary columns and reorders the remaining columns in the DataFrame to the specified order.

        Parameters:
            df (pd.DataFrame): The DataFrame to be processed.
            specific_order (list): The list of data specific columns to keep and their order. To be combined with the
            generic order to form a complete list of columns to keep.

        Returns:
            pd.DataFrame: The DataFrame with columns dropped and reordered.
        """
        self.data_frame.drop(self.columns_to_drop, axis=1)

    def _return_dict(self):
        return self.data_frame.to_dict(orient='records')

class BrandProcessor(DataProcessor):

    def __init__(self, path):
        super().__init__(path)
        self.data_specific_attributes = ['brand_id', 'brand']
        self.new_column_order = self.data_specific_attributes + self.new_column_order
        self.column_data_types = defaultdict(lambda: object, period_id=np.int32, gross_sales=np.float64,
                                             units_sold=np.int32, brand_id=np.int32, prev_gross_sales=np.float64,
                                             prev_units_sold=np.int32)
        self.merge_on_columns += self.data_specific_attributes
        self.values_to_merge += self.data_specific_attributes

    def _reorder_columns(self) -> None:
        self.data_frame.reindex(columns=self.new_column_order)
        self.data_frame.rename(columns={'brand': 'brand_name'})

    def _sort_rows(self):
        self.data_frame.sort_values(['brand_name', 'current_week_commencing_date'])


    @staticmethod
    def prepare_dataframe(path) -> dict:
        """
        Processes the product and brand data files, calculates growth metrics, and prepares the data.

        Returns:
            tuple: A tuple containing two DataFrames, the processed product data and brand data.
        """
        brand_processor = BrandProcessor(path)
        brand_processor._load_data()
        brand_processor._merge_data()
        brand_processor._calc_growth()
        brand_processor._drop_columns()
        brand_processor._reorder_columns()
        brand_processor._convert_date_to_string(['current_week_commencing_date', 'previous_week_commencing_date'])
        return brand_processor._return_dict()


class ProductProcessor(DataProcessor):

    def __init__(self, path):
        super().__init__(path)
        self.data_specific_attributes = ['barcode_no', 'product_name']
        self.new_column_order = self.data_specific_attributes + self.new_column_order
        self.column_data_types = defaultdict(lambda: object, period_id=np.int32, gross_sales=np.float64,
                                             units_sold=np.int32, brand_id=np.int32, prev_gross_sales=np.float64,
                                             prev_units_sold=np.int32)
        self.merge_on_columns += self.data_specific_attributes
        self.values_to_merge += self.data_specific_attributes

    def _reorder_columns(self) -> None:
        self.data_frame.reindex(columns=self.new_column_order)

    def _sort_rows(self):
        self.data_frame.sort_values(['product_name', 'current_week_commencing_date'])

    @staticmethod
    def prepare_dataframe(path) -> dict:
        """
        Processes the product and brand data files, calculates growth metrics, and prepares the data.

        Returns:
            tuple: A tuple containing two DataFrames, the processed product data and brand data.
        """
        product_processor = ProductProcessor(path)
        product_processor._load_data()
        product_processor._merge_data()
        product_processor._calc_growth()
        product_processor._drop_columns()
        product_processor._reorder_columns()
        product_processor._convert_date_to_string(['current_week_commencing_date', 'previous_week_commencing_date'])
        return product_processor._return_dict()

def merge_dict(dict_p, dict_b):
    return {'PRODUCT': dict_p, 'BRAND': dict_b}


def dict_to_json(dict_combined, output_path='../output/results.json'):
    with open(output_path, 'w') as results_json:
        simplejson.dump(dict_combined, results_json, indent=4, ignore_nan=True)

def run(prod_path='../data/sales_product.csv', brand_path='../data/sales_brand.csv'):
    """
    Runs the data processing and produces an output file in the output/ directory.
    """
    product_dict = ProductProcessor.prepare_dataframe(prod_path)
    brand_dict = BrandProcessor.prepare_dataframe(brand_path)
    merged_data = merge_dict(product_dict, brand_dict)
    dict_to_json(merged_data)




if __name__ == "__main__":
    run()
