import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import pickle
import os
import logging

# Initialize numpy
# np.import_array()

logger = logging.getLogger(__name__)

class SpotifyModel:
    def __init__(self):
        try:
            # Load pre-trained models with error handling
            model_path = 'nn_model.pkl'
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file {model_path} not found")
            
            try:
                with open(model_path, 'rb') as file:
                    self.nn_model_content = pickle.load(file)
            except Exception as e:
                raise RuntimeError(f"Error loading content-based model: {str(e)}")

            # Load SVD model with graceful fallback
            svd_path = 'svd_model.pkl'
            self.svd = None
            if os.path.exists(svd_path):
                try:
                    with open(svd_path, 'rb') as file:
                        self.svd = pickle.load(file)
                except Exception as e:
                    logger.error(f"Error loading SVD model: {str(e)}")
                    logger.warning("Collaborative filtering will be disabled")
            else:
                logger.warning(f"SVD model file {svd_path} not found")

            # Load data
            self.data_cleaned = pd.read_csv('data/data_cleaned.csv')
            self.new_df = pd.read_csv('data/user_matrix.csv')

            # Prepare content features
            self.data_content_features = self.data_cleaned[['popularity', 'danceability', 'energy', 
                                                          'acousticness', 'instrumentalness', 
                                                          'liveness', 'valence', 'tempo']]
            self.scaler = StandardScaler()
            self.data_content_scaled = self.scaler.fit_transform(self.data_content_features)

        except Exception as e:
            logger.error(f"Error initializing SpotifyModel: {str(e)}")
            raise
