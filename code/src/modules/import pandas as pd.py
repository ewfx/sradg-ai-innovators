import pandas as pd
import logging

class DataIngestion:
    @staticmethod
    def load_data(filepath: str, chunksize=10000) -> pd.DataFrame:
        """
        Loads data from a CSV file.

        Args:
            filepath (str): Path to the CSV file.
            chunksize (int, optional): Chunk size for reading large files. Defaults to 10000.

        Returns:
            pd.DataFrame: Loaded data, or an empty DataFrame if an error occurs.
        """
        try:
            data_chunks = pd.read_csv(filepath, chunksize=chunksize, parse_dates=['RISKDATE'])
            data = pd.concat(data_chunks, ignore_index=True)
            logging.info({"message": "Data loaded successfully.", "filepath": filepath})
            return data
        except FileNotFoundError:
            logging.error({"message": "File not found.", "filepath": filepath})
            return pd.DataFrame()
        except pd.errors.EmptyDataError:
            logging.error({"message": "No data found.", "filepath": filepath})
            return pd.DataFrame()
        except Exception as e:
            logging.error({"message": "Failed to load data.", "filepath": filepath, "error": str(e)})
            return pd.DataFrame()