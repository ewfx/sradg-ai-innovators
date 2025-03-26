import pandas as pd
import logging

class DataPersistence:
    @staticmethod
    def save_anomalies(df: pd.DataFrame, output_path: str):
        """
        Saves the detected anomalies to a CSV file.

        Args:
            df (pd.DataFrame): DataFrame containing anomalies.
            output_path (str): Path to save the CSV file.
        """
        try:
            df.to_csv(output_path, index=False)
            logging.info({"message": "Anomalies saved.", "path": output_path})
        except Exception as e:
            logging.error({"message": "Failed to save anomalies.", "error": str(e)})