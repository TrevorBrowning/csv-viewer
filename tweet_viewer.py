import streamlit as st
import pandas as pd
import os

# --- Configuration ---
# These must match the columns you saved in the pickle file
COLUMN_TWEET_CONTENT = 'tweet-content'
COLUMN_AUTHOR = 'tweet-username'
COLUMN_TIMESTAMP = 'tweet-time'

# Define which columns to display in the results table
COLUMNS_TO_DISPLAY = [COLUMN_TWEET_CONTENT, COLUMN_AUTHOR, COLUMN_TIMESTAMP]

# --- Data Loading (Hardcoded) ---
@st.cache_data # Use Streamlit's caching to load data efficiently only once
def load_data():
    """Loads the hardcoded data from the local pickle file."""
    PICKLE_FILE_PATH = 'tweets.pkl'
    
    if not os.path.exists(PICKLE_FILE_PATH):
        # NOTE: You must run the data preparation script (Step 1) 
        # and include 'tweets.pkl' in your deployment to avoid this error.
        st.error(f"Data file '{PICKLE_FILE_PATH}' not found. Please check deployment files.")
        return pd.DataFrame()
        
    # Load the compressed DataFrame from the pickle file
    df_loaded = pd.read_pickle(PICKLE_FILE_PATH, compression='zip')
    st.success(f"Successfully loaded {len(df_loaded)} tweets from archive!")
    return df_loaded

# --- Main Application ---
st.set_page_config(layout="wide") 
st.title("FunnyTweeter Archive Viewer 🐦😂")
st.write("Welcome to the permanent archive of funny tweets!")

# Load the data once
df = load_data()

# Only proceed if data was loaded successfully
if not df.empty:
    # Check if essential columns exist
    required_columns = COLUMNS_TO_DISPLAY
    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        st.error(f"Data integrity issue: Missing columns: {', '.join(missing_cols)}")
    else:
        if st.checkbox("Show a sample of the raw data (first 5 rows)", value=False):
            st.write(df.head())
        
        st.header("Search Tweets")
        search_phrase = st.text_input(
            "Enter word or phrase to search for in tweet content:", 
            key="search_box",
            placeholder="e.g., cat, pizza, Monday"
        )

        if search_phrase:
            # Perform case-insensitive search
            search_results_df = df[
                df[COLUMN_TWEET_CONTENT].astype(str).str.contains(search_phrase, case=False, na=False)
            ]

            if not search_results_df.empty:
                st.subheader(f"Found {len(search_results_df)} tweets containing '{search_phrase}':")
                
                # Select and display results
                display_df = search_results_df[COLUMNS_TO_DISPLAY].copy()
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info(f"No tweets found containing '{search_phrase}'.")
        else:
            st.info("Enter a search phrase above to start searching.")
            if st.button("Show all tweets (first 1000)"):
                st.subheader("Displaying first 1000 tweets (or fewer if less data):")
                display_all_df = df[COLUMNS_TO_DISPLAY].head(1000).copy()
                st.dataframe(display_all_df, use_container_width=True)

# Footer for clarity
st.markdown("---")
st.caption(f"Total tweets in archive: {len(df) if not df.empty else 'N/A'}")