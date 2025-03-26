import pandas as pd
import logging

class DataValidation:
    @staticmethod
    def validate_data_consistency(df: pd.DataFrame, quantity_threshold=10):
        """
        Validates data consistency based on a quantity threshold.

        Args:
            df (pd.DataFrame): Input DataFrame.
            quantity_threshold (int, optional): Threshold for quantity difference. Defaults to 10.

        Returns:
            pd.DataFrame: DataFrame with consistent data.
        """
        try:
            consistent_quantity = df['QUANTITYDIFFERENCE'].abs() < quantity_threshold
            logging.info({"message": "Data consistency validation applied.", "consistent_rows": consistent_quantity.sum()})
            return df[consistent_quantity]
        except Exception as e:
            logging.error(f"An error occurred: {e}")