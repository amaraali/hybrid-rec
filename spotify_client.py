import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import logging
import streamlit as st

logger = logging.getLogger(__name__)

def initialize_spotify_client():
    try:
        client_credentials_manager = SpotifyClientCredentials(
            client_id=st.secrets["SPOTIFY_CLIENT_ID"],
            client_secret=st.secrets["SPOTIFY_CLIENT_SECRET"]
        )
        return spotipy.Spotify(
            client_credentials_manager=client_credentials_manager,
            requests_timeout=10,
            retries=3
        )
    except Exception as e:
        logger.error(f"Failed to initialize Spotify client: {str(e)}")
        return None
