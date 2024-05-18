from src.DataProcessor import *
from collections import defaultdict


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