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
    def __init__(self, p_path: str, b_path: str):
        """
        Initializes the DataProcessor class with paths to the product and brand data files.

        Parameters:
            p_path (str): Path to the product data CSV file.
            b_path (str): Path to the brand data CSV file.
        """
        self.product_data_path = p_path
        self.brand_data_path = b_path

    def df_to_json(self, product: pd.DataFrame, brand: pd.DataFrame) -> None:
        """
        Converts product and brand DataFrames to JSON and writes to a file in the output directory.

        Parameters:
            product (pd.DataFrame): The processed product data.
            brand (pd.DataFrame): The processed brand data.
        """
        product, brand = self._convert_date_to_string(product), self._convert_date_to_string(brand)
        dict_product = product.sort_values(['product_name', 'current_week_commencing_date']).to_dict(orient='records')
        dict_brand = brand.sort_values(['brand_name', 'current_week_commencing_date']).to_dict(orient='records')
        dict_combined = {'PRODUCT': dict_product, 'BRAND': dict_brand}
        with open('C:/Users/goldi/backend-coding-challenge/output/results.json', 'w') as results_json:
            simplejson.dump(dict_combined, results_json, indent=4, ignore_nan=True)

    def _convert_date_to_string(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Converts date columns in the DataFrame to string format, readable in a JSON file.

        Parameters:
            df (pd.DataFrame): The DataFrame containing date columns.

        Returns:
            pd.DataFrame: The DataFrame with date columns converted to string format.
        """
        df['current_week_commencing_date'] = df['current_week_commencing_date'].dt.strftime('%d/%m/%Y')
        df['previous_week_commencing_date'] = df['previous_week_commencing_date'].dt.strftime('%d/%m/%Y')
        return df

    def process_data(self) -> tuple:
        """
        Processes the product and brand data files, calculates growth metrics, and prepares the data.

        Returns:
            tuple: A tuple containing two DataFrames, the processed product data and brand data.
        """
        df_product = self._prepare_data(self.product_data_path, ['barcode_no', 'product_name'],
                                        defaultdict(lambda: object, period_id=np.int32, gross_sales=np.float64,
                                                    units_sold=np.int32, prev_gross_sales=np.float64,
                                                    prev_units_sold=np.int32, barcode_no=str))

        df_brand = self._prepare_data(self.brand_data_path, ['brand_id', 'brand'],
                                      defaultdict(lambda: object, period_id=np.int32, gross_sales=np.float64,
                                                  units_sold=np.int32, brand_id=np.int32, prev_gross_sales=np.float64,
                                                  prev_units_sold=np.int32))

        df_brand = self._calc_growth(df_brand)
        df_product = self._calc_growth(df_product)

        df_brand = self._drop_columns_and_reorder(df_brand, ['brand_id', 'brand'])
        df_product = self._drop_columns_and_reorder(df_product, ['barcode_no', 'product_name'])

        return df_product, df_brand.rename(columns={'brand': 'brand_name'})

    def _prepare_data(self, path: str, d_type: list, c_type: defaultdict) -> pd.DataFrame:
        """
        Prepares the data for processing by reading the CSV file, handling dates, and merging data entries to provide
        current and previous entries into a single entry.

        Parameters:
            path (str): The file path to the data CSV.
            d_type (list): A list of columns for data types.
            c_type (defaultdict): A defaultdict specifying the column data types.

        Returns:
            pd.DataFrame: The prepared data DataFrame of either the product or the brand.
        """
        df = pd.read_csv(path, parse_dates=['week_commencing_date'], dayfirst=True)
        df_previous = df[df['period_name'] == 'previous']

        df['previous_week_commencing_date'] = df['week_commencing_date'] - pd.DateOffset(years=1)
        df = df.rename(columns={'week_commencing_date': 'current_week_commencing_date'})
        df_previous = df_previous.rename(columns={'week_commencing_date': 'previous_week_commencing_date',
                                                  'gross_sales': 'prev_gross_sales',
                                                  'units_sold': 'prev_units_sold'})

        df_previous['current_week_commencing_date'] = df_previous['previous_week_commencing_date'] + pd.DateOffset(
            years=1)
        df_previous['period_name'] = 'current'
        df_previous['period_id'] = 2

        merge_values = ['previous_week_commencing_date', 'prev_gross_sales', 'current_week_commencing_date',
                        'period_name',
                        'period_id', 'prev_units_sold']
        df = pd.merge(df, df_previous[merge_values + d_type], how='outer',
                      on=['previous_week_commencing_date', 'current_week_commencing_date', 'period_name',
                          'period_id'] + d_type)
        df = df.fillna(0)
        df = df.astype(c_type)

        return df[df['period_name'] == 'current']

    def _calc_growth(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates growth metrics for the data.

        Parameters:
            df (pd.DataFrame): The DataFrame containing sales data.

        Returns:
            pd.DataFrame: The DataFrame with growth metrics added.
        """
        df['perc_gross_sales_growth'] = np.where(df['prev_gross_sales'] > 0, np.round(((df['gross_sales'] - df['prev_gross_sales']) / df['prev_gross_sales']) * 100, 2), None)
        df['perc_unit_sales_growth'] = np.where(df['prev_units_sold'] > 0, np.round(((df['units_sold'] - df['prev_units_sold']) / df['prev_units_sold']) * 100, 2), None)
        return df

    def _drop_columns_and_reorder(self, df: pd.DataFrame, specific_order: list) -> pd.DataFrame:
        """
        Drops unnecessary columns and reorders the remaining columns in the DataFrame to the specified order.

        Parameters:
            df (pd.DataFrame): The DataFrame to be processed.
            specific_order (list): The list of data specific columns to keep and their order. To be combined with the
            generic order to form a complete list of columns to keep.

        Returns:
            pd.DataFrame: The DataFrame with columns dropped and reordered.
        """
        generic_order = ['current_week_commencing_date', 'previous_week_commencing_date', 'perc_gross_sales_growth',
                         'perc_unit_sales_growth']
        return df.drop(['period_id', 'period_name', 'gross_sales', 'units_sold', 'prev_gross_sales', 'prev_units_sold'],
                       axis=1).reindex(columns=specific_order + generic_order)


def run():
    """
    Runs the data processing and produces an output file in the output/ directory.
    """

    prod_path = 'C:/Users/goldi/backend-coding-challenge/data/sales_product.csv'
    brand_path = 'C:/Users/goldi/backend-coding-challenge/data/sales_brand.csv'

    data_processor = DataProcessor(prod_path, brand_path)
    df_product, df_brand = data_processor.process_data()
    print(df_product.dtypes)
    data_processor.df_to_json(df_product, df_brand)

    print(df_product.to_string())
    print(df_brand.to_string())



if __name__ == "__main__":
    run()
