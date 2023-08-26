import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import numpy as np
import joblib

# Load the trained Random Forest model
model_path = '/Users/ren/synchreload/learning algos/random_forest_model_v2.joblib'
lr_model = joblib.load(model_path)

# Convert popularity score to dollar signs
def popularity_to_dollar_signs(popularity):
    if 0 <= popularity < 26:
        return "&#36;/&#36;&#36;&#36;&#36;"
    elif 26 <= popularity < 51:
        return "&#36;&#36;/&#36;&#36;&#36;&#36;"
    elif 51 <= popularity < 76:
        return "&#36;&#36;&#36;/&#36;&#36;&#36;&#36;"
    else:  # This will handle values from 76 to 100 inclusive
        result = "&#36;&#36;&#36;&#36;/&#36;&#36;&#36;&#36;"
        return result

# Spotify API setup
client_id = 'c299b03ade1a4c53a0464dc4f7c62765'
client_secret = '51ee93104be14461bbe5f412e28680ef'
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def preprocess_input_data(input_data, training_columns):
    # One-hot encode categorical variables
    input_df = pd.get_dummies(pd.DataFrame([input_data]))

    # Add missing columns and set them to zero
    for col in training_columns:
        if col not in input_df.columns:
            input_df[col] = 0

    # Reorder columns to match the order of the training data
    input_df = input_df[training_columns]

    return input_df

with open('/Users/ren/synchreload/learning algos/training_columns_v2.txt', 'r') as file:
    training_columns = file.readlines()
training_columns = [col.strip() for col in training_columns]

def main():
    st.title('Music Licensing Price Prediction Tool')

    # Spotify Track Search
    song_title = st.text_input("Enter a song title:")
    
    if song_title:
        results = sp.search(q=song_title, limit=10)
        tracks = results['tracks']['items']
        
        if tracks:
            song_options = [f"{track['name']} by {track['artists'][0]['name']}" for track in tracks]
            selected_song = st.selectbox("Select a song:", song_options)

            # Extracting selected song details
            song_index = song_options.index(selected_song)
            song_data = tracks[song_index]
            st.write(f"Selected Song: {song_data['name']}")
            st.write(f"Artist: {song_data['artists'][0]['name']}")

            # Fetch song and artist popularity
            song_popularity = song_data['popularity']
            artist_id = song_data['artists'][0]['id']
            artist_data = sp.artist(artist_id)
            artist_popularity = artist_data['popularity']

            # Convert popularity to dollar signs and display
            song_popularity_dollar = popularity_to_dollar_signs(song_popularity)
            artist_popularity_dollar = popularity_to_dollar_signs(artist_popularity)
            st.write(f"Song Popularity: {song_popularity_dollar}")
            st.write(f"Artist Popularity: {artist_popularity_dollar}")
        else:
            st.write("No songs found!")

    # Additional Variables Input
    st.subheader("Additional Licensing Parameters")
    license_type = st.selectbox("License Type", ["Advertising", "Feature film", "Series"])
    license_duration = st.slider("License Duration (in weeks)", 1, 260, 12)
    territory = st.selectbox("Territory", ["Global", "Regional", "Local"])
    media_types = st.multiselect("Media Type", ["Television", "Radio", "Online", "Cinema", "VOD"])

    # Depending on license type, choose appropriate budget type
    if license_type == "Advertising":
        media_budget = st.number_input("Enter Media Budget (in $)", value=0)
    else:
        movie_budget = st.number_input("Enter Movie Budget (in $)", value=0)

    # Placeholder for Price Prediction Functionality
    if st.button("Predict Price"):
        # Initialize the input_data dictionary
        input_data = {
            'song_popularity': song_popularity,
            'artist_popularity': artist_popularity,
            'license_duration': license_duration,
            'territory_' + territory: 1,
            'license_type_' + license_type: 1,
        }
        
        # Add media types to the dictionary
        for media in media_types:
            input_data['media_type_' + media] = 1
        
        # Depending on license type, add appropriate budget type
        if license_type == "Advertising":
            input_data['media_budget'] = media_budget
        else:
            input_data['movie_budget'] = movie_budget

        # Preprocess the data
        processed_input = preprocess_input_data(input_data, training_columns)

        # Predict using the trained Random Forest model
        predicted_price = lr_model.predict(processed_input)[0]

        st.write("Predicted Licensing Price: $", round(predicted_price, 2))
    st.markdown("Fueled by [eastaste.net](https://eastaste.net)")
if __name__ == "__main__":
    main()
