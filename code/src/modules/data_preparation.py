import pandas as pd
import logging
from sklearn.preprocessing import LabelEncoder
import pickle

label_encoder = None  # Initialize outside the class

class DataPreparation:
    @staticmethod
    def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocesses the input DataFrame for anomaly detection.

        Args:
            df (pd.DataFrame): Input DataFrame.

        Returns:
            pd.DataFrame: Preprocessed features.
        """
        global label_encoder
        try:
            df['RISKDATE'] = pd.to_datetime(df['RISKDATE'])  # Explicit conversion
            df.sort_values('RISKDATE', inplace=True)
            df['day_of_week'] = df['RISKDATE'].dt.weekday
            df['month'] = df['RISKDATE'].dt.month
            for window in [7, 14, 30]:
                df[f'quantity_mean_{window}d'] = df['QUANTITYDIFFERENCE'].rolling(window).mean()
                df[f'price_std_{window}d'] = df['IMPACT_PRICE'].rolling(window).std()
            df['quantity_diff_lag1'] = df['QUANTITYDIFFERENCE'].diff(1)

            if label_encoder is None:
                try:
                    with open('models/label_encoder.pkl', 'rb') as f:
                        label_encoder = pickle.load(f)
                except FileNotFoundError:
                    label_encoder = LabelEncoder()
                    label_encoder.fit(df['DESKNAME'].astype(str))
                    with open('models/label_encoder.pkl', 'wb') as f:
                        pickle.dump(label_encoder, f)

            desk_names = df['DESKNAME'].astype(str)
            encoded_names = []
            for name in desk_names:
                try:
                    encoded_names.append(label_encoder.transform([name])[0])
                except ValueError:
                    # Handle unseen labels
                    encoded_names.append(-1)  # Or any default value
                    logging.warning(f"Unseen label '{name}' encountered. Using default value.")

            df['deskname_encoded'] = encoded_names

            features = df.fillna(0)[[
                'QUANTITYDIFFERENCE', 'IMPACT_PRICE', 'IMPACT_QUANTITY', 'day_of_week', 'month', 'deskname_encoded',
                'quantity_mean_7d', 'price_std_7d', 'quantity_diff_lag1'
            ]]
            logging.info({"message": "Features created."})
            return features
        except Exception as e:
            logging.error({"message": "Error in preprocessing data.", "error": str(e)})
            raise