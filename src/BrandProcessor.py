from DataProcessor import *
from collections import defaultdict


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