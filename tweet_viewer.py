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
        st.error(f"Data file '{PICKLE_FILE_PATH}' not found. Please check deployment files.")
        return pd.DataFrame()
        
    try:
        # Load the compressed DataFrame from the pickle file
        df_loaded = pd.read_pickle(PICKLE_FILE_PATH, compression='zip')
        st.success(f"Successfully loaded {len(df_loaded)} tweets from archive!")
        return df_loaded
    except Exception as e:
        st.error(f"Error loading pickle file: {e}")
        return pd.DataFrame()

# --- Main Application ---
st.set_page_config(layout="wide") 
st.title("FunnyTweeter Archive Viewer")
st.write("Welcome to the permanent archive of funny tweets!")

# Load the data once
df = load_data()

# Only proceed if data was loaded successfully
if not df.empty:
    # Check if essential columns exist (data integrity check)
    required_columns = COLUMNS_TO_DISPLAY
    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        st.error(f"Data integrity issue: Missing columns: {', '.join(missing_cols)}")
    else:
        # --- Sidebar and Global Filters ---
        st.sidebar.header("Data Tools")
        if st.sidebar.checkbox("Show a sample of the raw data (first 5 rows)", value=False):
            st.sidebar.write(df.head())
            
        # New Feature: Filter by Author
        unique_authors = ['All Authors'] + sorted(df[COLUMN_AUTHOR].unique().tolist())
        selected_author = st.sidebar.selectbox(
            "Filter by Author:",
            unique_authors
        )

        # Apply author filter globally
        if selected_author != 'All Authors':
            filtered_df = df[df[COLUMN_AUTHOR] == selected_author]
            st.subheader(f"Showing tweets by: @{selected_author}")
        else:
            filtered_df = df
            
        # Display total count after filtering
        st.sidebar.markdown(f"**Total tweets displayed:** {len(filtered_df)}")
        st.markdown("---") # Visual separator

        # --- Search Interface ---
        st.header("Search Tweets")
        search_phrase = st.text_input(
            "Enter word or phrase to search for in tweet content:", 
            key="search_box",
            placeholder="e.g., cat, pizza, Monday"
        )
        
        # Determine the DataFrame to use for search (filtered_df or df)
        search_target_df = filtered_df
        
        if search_phrase:
            # Perform case-insensitive search on the filtered/full DataFrame
            search_results_df = search_target_df[
                search_target_df[COLUMN_TWEET_CONTENT].astype(str).str.contains(search_phrase, case=False, na=False)
            ]

            if not search_results_df.empty:
                st.subheader(f"Found {len(search_results_df)} tweets containing '{search_phrase}':")
                
                # Select and display results
                display_df = search_results_df[COLUMNS_TO_DISPLAY].copy()
                st.dataframe(display_df, use_container_width=True)
            else:
                st.info(f"No tweets found containing '{search_phrase}'.")
        else:
            st.info("Enter a search phrase above to start searching, or use the buttons below.")
            
            # --- Exploration Buttons (NEW) ---
            # Create a container for the buttons to place them side-by-side
            col1, col2 = st.columns(2) 

            # Button 1: Show All Tweets (or first 1000 of the filtered set)
            with col1:
                if st.button("Show Top 1000 Tweets"):
                    st.subheader(f"Displaying first 1000 tweets (or fewer if less data) from the current selection:")
                    display_all_df = search_target_df[COLUMNS_TO_DISPLAY].head(1000).copy()
                    st.dataframe(display_all_df, use_container_width=True)

            # Button 2: Show Random Tweets 
            with col2:
                if st.button("Display 100 Random Tweets"):
                    # Use pandas .sample() to get a random subset of 100 rows
                    sample_size = min(100, len(search_target_df))
                    
                    # .sample() generates a different random set every time it's run
                    random_sample_df = search_target_df.sample(n=sample_size)[COLUMNS_TO_DISPLAY].copy()
                    
                    st.subheader(f"Displaying a random sample of {sample_size} tweets:")
                    st.dataframe(random_sample_df, use_container_width=True)

# Footer for clarity
st.markdown("---")
st.caption(f"Total tweets in archive: {len(df) if not df.empty else 'N/A'}")