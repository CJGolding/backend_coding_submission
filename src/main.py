from src.BrandProcessor import *
from src.ProductProcessor import *
import simplejson


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
