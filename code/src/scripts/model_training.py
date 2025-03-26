import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder
import pickle
import yaml

# Load configuration from config.yml
try:
    with open('config/config.yaml', 'r') as file:
        config = yaml.safe_load(file)
except FileNotFoundError:
    print("Error: config/config.yaml not found. Using default configurations.")
    config = {
        'data': {
            'data_file_path': 'data/generated_reconciliation_data.csv',
            'isolation_forest_model_path': 'isolation_forest_model.pkl',
            'kmeans_model_path': 'kmeans_model.pkl',
            'label_encoder_path': 'label_encoder.pkl',
            'contamination_rate': 0.05,
            'random_seed': 42,
            'n_clusters': 5,
            'rolling_windows': [7, 14, 30],
            'quantity_diff_column': 'QUANTITYDIFFERENCE',
            'impact_price_column': 'IMPACT_PRICE',
            'impact_quantity_column': 'IMPACT_QUANTITY',
            'risk_date_column': 'RISKDATE',
            'desk_name_column': 'DESKNAME',
            'features_columns': [
                'QUANTITYDIFFERENCE', 'IMPACT_PRICE', 'IMPACT_QUANTITY', 'day_of_week', 'month', 'deskname_encoded',
                'quantity_mean_7d', 'price_std_7d', 'quantity_diff_lag1'
            ]
        }
    }

# Load data from config
DATA_FILE_PATH = config['data']['data_file_path']
ISOLATION_FOREST_MODEL_PATH = config['data']['isolation_forest_model_path']
KMEANS_MODEL_PATH = config['data']['kmeans_model_path']
LABEL_ENCODER_PATH = config['data']['label_encoder_path']
CONTAMINATION_RATE = config['data']['contamination_rate']
RANDOM_SEED = config['data']['random_seed']
N_CLUSTERS = config['data']['n_clusters']
ROLLING_WINDOWS = config['data']['rolling_windows']
QUANTITY_DIFF_COLUMN = config['data']['quantity_diff_column']
IMPACT_PRICE_COLUMN = config['data']['impact_price_column']
IMPACT_QUANTITY_COLUMN = config['data']['impact_quantity_column']
RISK_DATE_COLUMN = config['data']['risk_date_column']
DESK_NAME_COLUMN = config['data']['desk_name_column']
FEATURES_COLUMNS = config['data']['features_columns']

# Load your data
df = pd.read_csv(DATA_FILE_PATH)
df[RISK_DATE_COLUMN] = pd.to_datetime(df[RISK_DATE_COLUMN])

# Preprocess the data
df.sort_values(RISK_DATE_COLUMN, inplace=True)
df['day_of_week'] = df[RISK_DATE_COLUMN].dt.weekday
df['month'] = df[RISK_DATE_COLUMN].dt.month

for window in ROLLING_WINDOWS:
    df[f'quantity_mean_{window}d'] = df[QUANTITY_DIFF_COLUMN].rolling(window).mean()
    df[f'price_std_{window}d'] = df[IMPACT_PRICE_COLUMN].rolling(window).std()

df['quantity_diff_lag1'] = df[QUANTITY_DIFF_COLUMN].diff(1)

label_encoder = LabelEncoder()
label_encoder.fit(df[DESK_NAME_COLUMN].astype(str))
df['deskname_encoded'] = label_encoder.transform(df[DESK_NAME_COLUMN].astype(str))

features = df.fillna(0)[FEATURES_COLUMNS]

# Train the models
isolation_forest_model = IsolationForest(contamination=CONTAMINATION_RATE, random_state=RANDOM_SEED).fit(features)
kmeans_model = KMeans(n_clusters=N_CLUSTERS, random_state=RANDOM_SEED).fit(features)

# Save the models and encoder
with open(ISOLATION_FOREST_MODEL_PATH, 'wb') as f:
    pickle.dump(isolation_forest_model, f)
with open(KMEANS_MODEL_PATH, 'wb') as f:
    pickle.dump(kmeans_model, f)
with open(LABEL_ENCODER_PATH, 'wb') as f:
    pickle.dump(label_encoder, f)

print('Models and encoder saved.')