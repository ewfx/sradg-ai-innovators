# modules/model_layer.py
import pandas as pd
import numpy as np
import logging
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.cluster import KMeans
import pickle
import os
import yaml

# Load configuration
try:
    with open('config/config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)
    isolation_forest_path = config['data']['isolation_forest_model_path']
    kmeans_path = config['data']['kmeans_model_path']
    n_clusters_config = config['data']['n_clusters']
    contamination_config = config['data']['contamination_rate']
except FileNotFoundError:
    print("config.yaml not found, using defaults.")
    isolation_forest_path = 'models/isolation_forest_model.pkl'
    kmeans_path = 'models/kmeans_model.pkl'
    n_clusters_config = 5
    contamination_config = 0.05

# Load models if they exist
isolation_forest_model = None
kmeans_model = None
if os.path.exists(isolation_forest_path):
    with open(isolation_forest_path, 'rb') as f:
        isolation_forest_model = pickle.load(f)

if os.path.exists(kmeans_path):
    with open(kmeans_path, 'rb') as f:
        kmeans_model = pickle.load(f)
print ("kmeans_model", kmeans_path)

class ModelLayer:
    @staticmethod
    def detect_anomalies(features: pd.DataFrame, method='isolation_forest', contamination=contamination_config) -> np.array:

        """
        Detects anomalies in the given features.
        """
        global isolation_forest_model
        try:
            if method == 'isolation_forest':
                if isolation_forest_model is None:
                    logging.info("Training a new Isolation Forest model.")
                    print("Training a new Isolation Forest model.") #added print.
                    isolation_forest_model = IsolationForest(contamination=contamination, random_state=42).fit(features)
                    os.makedirs(os.path.dirname(isolation_forest_path), exist_ok=True)
                    with open(isolation_forest_path, 'wb') as f:
                        pickle.dump(isolation_forest_model, f)
                    logging.info(f"Isolation Forest model saved to: {isolation_forest_path}")
                else:
                    logging.info("Using pre-trained Isolation Forest model.")
                    print("Using pre-trained Isolation Forest model.") #added print.
                
                preds = isolation_forest_model.predict(features)
            elif method == 'lof':
                
                logging.info("Using LocalOutlierFactor for anomaly detection.")
                print("Using LocalOutlierFactor for anomaly detection.") #added print.
                preds = LocalOutlierFactor(contamination=contamination).fit_predict(features)
            else:
                raise ValueError("Invalid anomaly detection method.")

            logging.info({"message": f"Anomalies detected using {method}.", "count": sum(preds == -1)})
            logging.info(f"Anomaly predictions: {preds}")
            logging.info(f"Feature values for anomaly detection:\n{features}")

            print(f"Anomalies detected using {method}. Count: {sum(preds == -1)}") #added print.
            print(f"Anomaly predictions: {preds}") #added print.
            print(f"Feature values for anomaly detection:\n{features}") #added print.

            result = np.where(preds == -1, 'Yes', 'No')
            return result

        except Exception as e:
         logging.error({"message": "Error during anomaly detection.", "error": str(e)})
        print(f"Error during anomaly detection: {e}") #added print.
        raise


    @staticmethod
    def cluster_data(features: pd.DataFrame, n_clusters=n_clusters_config) -> np.array:
        """
        Clusters the data using KMeans.
        """
        global kmeans_model
        try:
            if features.empty:
                logging.warning("Received empty dataframe for clustering.")
                return pd.Series([])

            effective_n_clusters = min(n_clusters, len(features))

            if len(features) >= effective_n_clusters:
                if kmeans_model is None:
                    kmeans_model = KMeans(n_clusters=effective_n_clusters, random_state=42).fit(features)
                    os.makedirs(os.path.dirname(kmeans_path), exist_ok=True)
                    with open(kmeans_path, 'wb') as f:
                        pickle.dump(kmeans_model, f)
                clusters = kmeans_model.predict(features)
                logging.info({"message": "Data clustered."})
                return clusters
            else:
                logging.warning(f"Skipping clustering. n_samples={len(features)} < n_clusters={effective_n_clusters}")
                return pd.Series([-1] * len(features))
        except Exception as e:
            logging.error({"message": "Error during clustering.", "error": str(e)})
            raise