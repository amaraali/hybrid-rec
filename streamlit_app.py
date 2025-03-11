import streamlit as st
import logging
from spotify_model import SpotifyModel
from spotify_client import initialize_spotify_client
from cache import SpotifyCache
from recommender import Recommender
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
spotify_model = SpotifyModel()
spotify_client = initialize_spotify_client()
cache = SpotifyCache()
recommender = Recommender(spotify_model, spotify_client, cache)

# Add custom CSS (keep the original CSS)
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 1rem;
    }
    
    /* Header styling */
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
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: rgba(255,255,255,0.8);
        font-size: 1.1rem;
    }
    
    /* Card styling */
    .recommendation-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.2s ease;
    }
    
    .recommendation-card:hover {
        transform: translateY(-5px);
    }
    
    .track-title {
        color: #1DB954;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    .track-info {
        color: #444;
        font-size: 1rem;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .score-container {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 10px;
        margin: 10px 0;
    }
    
    .score-info {
        font-size: 0.9rem;
        color: #666;
        display: flex;
        justify-content: space-between;
        gap: 10px;
    }
    
    .score-item {
        padding: 5px 10px;
        border-radius: 15px;
        background: #e9ecef;
    }
    
    .spotify-embed {
        margin-top: 15px;
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Sidebar styling */
    .sidebar-content {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
    }
    
    .sidebar-header {
        color: #1DB954;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    
    /* Button styling */
    .stButton > button {
        background-color: #1DB954;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        width: 100%;
        font-weight: bold;
    }
    
    .stButton > button:hover {
        background-color: #1ed760;
    }
</style>
""", unsafe_allow_html=True)

# Modern header
st.markdown("""
<div class="title-container">
    <h1 class="main-title">🎵 Spotify Music Recommender</h1>
    <p class="subtitle">Get personalized music recommendations based on your preferences!</p>
</div>
""", unsafe_allow_html=True)

# Sidebar with better organization
st.sidebar.markdown('<p class="sidebar-header">Input Parameters</p>', unsafe_allow_html=True)
with st.sidebar:
    # with st.expander("ℹ️ How to Use", expanded=True):
    #     st.markdown("""
    #     1. Enter your User ID
    #     2. Paste a Track ID or Spotify URL
    #     3. Adjust number of recommendations
    #     4. Click 'Get Recommendations'
    #     """)
    with st.expander("📖 How to Use", expanded=True):
        st.markdown("""
            1. **User ID**: Enter a number between 1-1000
            2. **Track Input**: Paste either:
               - Spotify Track URL
               - Spotify Track ID
            3. **Customize**: Choose number of recommendations
            4. **Generate**: Click to get personalized suggestions
            
            > **Tip**: You can find a track's URL by clicking 'Share' on Spotify
            """)
    
    user_id = st.number_input("👤 User ID", min_value=1, max_value=1000, step=1, value=1)
    track_input = st.text_input("🎵 Track ID or Spotify URL", "5SuOikwiRyPMVoIQDJUgSV")
    top_n = st.slider("📊 Number of Recommendations", min_value=1, max_value=20, value=10)

# Process Track Input
track_id = None
if track_input:
    try:
        if "spotify.com/track/" in track_input:
            track_id = recommender.extract_track_id_from_url(track_input)
            st.sidebar.success(f"Extracted Track ID: {track_id}")
        else:
            track_id = track_input
    except ValueError as e:
        st.sidebar.error(str(e))

# Main content area with tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Recommendations", "User Matrix", "Statistics", "Sample Tracks", "About"])

with tab1:
    if track_id and st.sidebar.button("🔍 Get Recommendations"):
        try:
            with st.spinner("🎵 Creating your personalized playlist..."):
                # Get track details if available
                if track_id in spotify_model.data_cleaned['track_id'].values:
                    track_details = spotify_model.data_cleaned[spotify_model.data_cleaned['track_id'] == track_id].iloc[0]
                    st.subheader("🌱 Seed Track")
                    st.markdown(f"""
                    <iframe style="border-radius:12px" 
                            src="https://open.spotify.com/embed/track/{track_id}?utm_source=generator" 
                            width="100%" height="152" frameBorder="0" 
                            allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                            loading="lazy">
                    </iframe>
                    """, unsafe_allow_html=True)
                    st.divider()
                
                # Get and display recommendations
                recommendations = recommender.get_hybrid_recommendations(user_id=user_id, track_id=track_id, top_n=top_n)
                
                st.subheader(f"🎯 Top {top_n} Recommendations")
                
                for i, rec in enumerate(recommendations, 1):
                    st.markdown(f"""
                    <div class="recommendation-card">
                        <div class="track-title">#{i} {rec['track_name']}</div>
                        <div class="track-info">🎤 {rec['artists']} | 🎭 {rec['track_genre']}</div>
                        <div class="score-container">
                            <div class="score-info">
                                <span class="score-item">Content: {rec['content_score']:.2f}</span>
                                <span class="score-item">Collaborative: {rec['collaborative_score']:.2f}</span>
                                <span class="score-item">Final Score: {rec['final_score']:.2f}</span>
                            </div>
                        </div>
                        <div class="spotify-embed">
                            <iframe style="border-radius:12px" 
                                    src="https://open.spotify.com/embed/track/{rec['track_id']}?utm_source=generator" 
                                    width="100%" height="152" frameBorder="0" 
                                    allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
                                    loading="lazy">
                            </iframe>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.info("Please make sure you've entered valid User ID and Track ID")

with tab2:
    st.header("User Matrix Data")
    if not spotify_model.new_df.empty:
        # Add search/filter functionality
        search_user = st.number_input("Search by User ID", min_value=1, max_value=1000, value=1)
        filtered_df = spotify_model.new_df[spotify_model.new_df['user_id'] == search_user]
        
        # Display basic statistics
        st.subheader("User Listening Statistics")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Tracks", len(filtered_df))
            st.metric("Average Rating", round(filtered_df['rating'].mean(), 2))
        with col2:
            st.metric("Highest Rated", filtered_df['rating'].max())
            st.metric("Lowest Rated", filtered_df['rating'].min())
            
        # Display the filtered dataframe
        st.subheader("User Ratings")
        st.dataframe(filtered_df.style.background_gradient(subset=['rating'], cmap='viridis'))
    else:
        st.warning("User matrix data is not available")

with tab3:
    st.header("User Matrix Statistics")
    if not spotify_model.new_df.empty:
        # Overall statistics
        st.subheader("Overall Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", spotify_model.new_df['user_id'].nunique())
            st.metric("Total Tracks", spotify_model.new_df['track_id'].nunique())
        with col2:
            st.metric("Average Rating", round(spotify_model.new_df['rating'].mean(), 2))
            st.metric("Rating Std Dev", round(spotify_model.new_df['rating'].std(), 2))
        with col3:
            st.metric("Total Ratings", len(spotify_model.new_df))
            st.metric("Rating Density", f"{round(len(spotify_model.new_df)/(spotify_model.new_df['user_id'].nunique()*spotify_model.new_df['track_id'].nunique())*100, 2)}%")
        
        # Rating distribution
        st.subheader("Rating Distribution")
        rating_dist = pd.DataFrame(spotify_model.new_df['rating'].value_counts().sort_index())
        st.bar_chart(rating_dist)
        
        # User activity distribution
        st.subheader("User Activity Distribution")
        user_activity = pd.DataFrame(spotify_model.new_df['user_id'].value_counts())
        st.line_chart(user_activity)
    else:
        st.warning("User matrix data is not available")

with tab4:
    st.header("🎵 Sample Tracks to Try")
    
    # Create sample categories
    categories = {
        "Popular Acoustic": spotify_model.data_cleaned[
            (spotify_model.data_cleaned['track_genre'] == 'acoustic') & 
            (spotify_model.data_cleaned['popularity'] > 0.7)
        ].head(10),
        
        "High Energy": spotify_model.data_cleaned[
            (spotify_model.data_cleaned['energy'] > 0.8)
        ].head(10),
        
        "Chill Tracks": spotify_model.data_cleaned[
            (spotify_model.data_cleaned['energy'] < 0.4) & 
            (spotify_model.data_cleaned['acousticness'] > 0.6)
        ].head(10)
    }
    
    # Display tracks by category with table layout
    for category, tracks in categories.items():
        st.subheader(category)
        
        # Prepare table data
        table_data = []
        for _, track in tracks.iterrows():
            # Format track info for table
            table_data.append({
                "Track Name": track['track_name'],
                "Artists": track['artists'],
                "Genre": track['track_genre'],
                "Track ID": track['track_id'],
                "Actions": track['track_id']  # We'll use this for the button
            })
        
        # Convert to DataFrame for display
        df = pd.DataFrame(table_data)
        
        # Custom CSS to style the table
        st.markdown("""
        <style>
        .track-table {
            font-size: 0.9rem;
            margin: 1rem 0;
        }
        .copy-button {
            background-color: #1DB954;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            cursor: pointer;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Create columns for the table
        cols = st.columns([3, 2, 1.5, 2, 1])
        cols[0].write("**Track Name**")
        cols[1].write("**Artists**")
        cols[2].write("**Genre**")
        cols[3].write("**Track ID**")
        # cols[4].write("**Action**")
        
        # Display each row
        for idx, row in df.iterrows():
            cols = st.columns([3, 2, 1.5, 2, 1])
            cols[0].write(row["Track Name"])
            cols[1].write(row["Artists"])
            cols[2].write(row["Genre"])
            cols[3].write(row["Track ID"])
            
            # Create unique key for each button
            button_key = f"copy_{idx}_{row['Track ID']}"
            
            # Copy button with clipboard.js functionality
            # cols[4].markdown(f"""
            #     <button onclick="navigator.clipboard.writeText('{row['Track ID']}')" 
            #             class="copy-button" 
            #             title="Copy Track ID to clipboard">
            #         Copy ID
            #     </button>
            #     """, 
            #     unsafe_allow_html=True
            # )
        
        st.divider()

with tab5:
    st.markdown("""
    ### 🎵 About the Recommender
     #### 🎯 Content-based Filtering
    Analyzes musical features like:
    - Tempo
    - Energy
    - Danceability
    - Acousticness
    - And more...
    
    #### 👥 Collaborative Filtering
    Learns from user behavior by:
    - Understanding user preferences
    - Finding similar taste profiles
    
    #### 🔄 Hybrid Approach
    This hybrid recommender system combines two approaches:
    - **Content-based filtering**: Recommends songs similar to a given track based on musical features
    - **Collaborative filtering**: Suggests tracks based on user behavior and preferences
    """)