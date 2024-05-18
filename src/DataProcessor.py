
import pandas as pd
import numpy as np


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