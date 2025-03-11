import streamlit as st
from spotify_client import initialize_spotify_client
from spotify_model import SpotifyModel
from recommender import Recommender
from cache import TrackCache
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize session state
if 'user_id' not in st.session_state:
    st.session_state.user_id = 1  # Default user ID

# Page config
st.set_page_config(
    page_title="Spotify Music Recommender",
    page_icon="🎵",
    layout="wide"
)

# Add custom CSS
st.markdown("""
<style>
    .main { padding: 1rem; }
    .title-container {
        background: linear-gradient(90deg, #1DB954, #191414);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .recommendation-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .track-title {
        color: #1DB954;
        font-size: 1.2rem;
        font-weight: bold;
    }
    .score-container {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def initialize_components():
    spotify_client = initialize_spotify_client()
    spotify_model = SpotifyModel()
    cache = TrackCache()
    recommender = Recommender(spotify_model, spotify_client, cache)
    return recommender

try:
    recommender = initialize_components()
except Exception as e:
    st.error(f"Failed to initialize components: {str(e)}")
    st.stop()

# Modern header
st.markdown("""
<div class="title-container">
    <h1 class="main-title">🎵 Spotify Music Recommender</h1>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    with st.expander("📖 How to Use", expanded=True):
        st.markdown("""
            1. **User ID**: Enter a number (1-1000)
            2. **Track URL**: Paste Spotify track URL
            3. **Choose** number of recommendations
            4. Click 'Get Recommendations'
        """)
    
    user_id = st.number_input("👤 User ID", min_value=1, max_value=1000, value=1)
    track_url = st.text_input("🎵 Spotify Track URL", 
                             placeholder="https://open.spotify.com/track/...")
    num_recommendations = st.slider("📊 Number of Recommendations", 5, 20, 10)

# Main content
if track_url:
    try:
        if not track_url.strip():
            st.error("Please enter a Spotify track URL")
        else:
            track_id = recommender.extract_track_id_from_url(track_url)
            track_info = recommender.get_track_features(track_id)
            
            # Display track info with embed
            st.subheader("🎵 Selected Track")
            st.write(f"**Track:** {track_info['track_name']}")
            st.write(f"**Artist(s):** {track_info['artists']}")
            
            st.markdown(f"""
            <iframe src="https://open.spotify.com/embed/track/{track_id}" 
                    width="100%" height="80" frameborder="0" 
                    allowtransparency="true" allow="encrypted-media">
            </iframe>
            """, unsafe_allow_html=True)
            
            # Get and display recommendations
            with st.spinner("Getting recommendations..."):
                recommendations = recommender.get_hybrid_recommendations(
                    user_id, track_id, num_recommendations
                )
        
        st.subheader("🎯 Recommendations")
        for i, rec in enumerate(recommendations, 1):
            with st.container():
                st.markdown(f"""
                <div class="recommendation-card">
                    <div class="track-title">#{i} {rec['track_name']}</div>
                    <div>Artists: {rec['artists']}</div>
                    <div>Genre: {rec['track_genre']}</div>
                    <div class="score-container">
                        <div>Content Score: {rec['content_score']:.2f}</div>
                        <div>Collaborative Score: {rec['collaborative_score']:.2f}</div>
                        <div>Final Score: {rec['final_score']:.2f}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")

# Add footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Spotify API")
