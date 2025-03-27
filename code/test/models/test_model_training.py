
import os
import pytest
import pandas as pd
import pickle
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import LabelEncoder

def test_model_training_outputs_exist():
    # Paths based on the script's default config
    iso_path = 'isolation_forest_model.pkl'
    kmeans_path = 'kmeans_model.pkl'
    encoder_path = 'label_encoder.pkl'

    assert os.path.exists(iso_path), "Isolation Forest model not saved"
    assert os.path.exists(kmeans_path), "KMeans model not saved"
    assert os.path.exists(encoder_path), "Label encoder not saved"

def test_model_loading_and_types():
    with open('isolation_forest_model.pkl', 'rb') as f:
        isolation_model = pickle.load(f)
    assert isinstance(isolation_model, IsolationForest)

    with open('kmeans_model.pkl', 'rb') as f:
        kmeans_model = pickle.load(f)
    assert isinstance(kmeans_model, KMeans)

    with open('label_encoder.pkl', 'rb') as f:
        encoder = pickle.load(f)
    assert isinstance(encoder, LabelEncoder)
