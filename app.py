import streamlit as st
import pandas as pd
import pickle
import requests
import time
import gdown
import os

API_KEY = "5de9bb47"

# Function to check if an image URL is valid
def is_image_accessible(url):
    try:
        response = requests.head(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# Function to fetch posters
def fetch_poster(movie_title):
    try:
        url = f"http://www.omdbapi.com/?t={movie_title}&apikey={API_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch data for {movie_title}")

        data = response.json()
        poster_url = data.get("Poster", "")

        # Check if poster URL is valid
        return poster_url if poster_url and is_image_accessible(poster_url) else None
    except Exception as e:
        print(f"Error fetching poster for {movie_title}: {e}")
        return None

# 🔹 **Download similarity.pkl from Google Drive**
SIMILARITY_FILE_ID = "11kD4uOSYlt5OJVbB5dnxDqZQ5XrZYFu-"
SIMILARITY_FILE_PATH = "similarity.pkl"

if not os.path.exists(SIMILARITY_FILE_PATH):  # Download only if not present
    gdown.download(f"https://drive.google.com/uc?id={SIMILARITY_FILE_ID}", SIMILARITY_FILE_PATH, quiet=False)

# Load the files
movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open(SIMILARITY_FILE_PATH, 'rb'))

# Recommendation Function
def recommend(title):
    movie_index = movies[movies['names'] == title].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []

    for i in movies_list:
        movie_name = movies.iloc[i[0]].names
        recommended_movies.append(movie_name)

        time.sleep(0.5)  # Delay to avoid API limit
        poster_url = fetch_poster(movie_name)
        recommended_posters.append(poster_url if poster_url else "Poster Unavailable")

    return recommended_movies, recommended_posters

# Apply Styles
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #00d4ff, #790909, #020024, #fbc2eb);
            background-size: 400% 400%;
            animation: gradientBG 15s ease infinite;
        }
        @keyframes gradientBG {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        h1 {
            color: #ffffff !important;
            text-align: center;
            font-size: 42px;
            font-weight: bold;
            text-shadow: 3px 3px 5px rgba(0, 0, 0, 0.5);
        }
        div.stButton > button {
            color: white;
            font-size: 18px;
            border-radius: 10px;
            border: none;
            padding: 10px;
            box-shadow: 0px 5px 15px rgba(255, 81, 47, 0.5);
            transition: 0.3s ease-in-out;
        }
        div.stButton > button:hover {
            box-shadow: 0px 5px 25px rgba(221, 36, 118, 0.8);
            transform: scale(1.05);
            color: white;
        }
        img {
            display: block;
            margin: auto;
            border-radius: 15px;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
            padding:10px;
        }
        img:hover{
            box-shadow: 0px 5px 25px rgba(221, 36, 118, 0.8);
            transform: scale(1.2);
        }
        .poster-unavailable {
            text-align: center;
            font-size: 18px;
            color: white;
            font-weight: bold;
            margin-top: 20px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title('🎬 AI Movie Recommender')

selected_movie_name = st.selectbox('Which movie do you like?', movies['names'].values)

if st.button('Recommend'):
    recommended_movies, recommended_posters = recommend(selected_movie_name)

    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            if recommended_posters[i] == "Poster Unavailable":
                st.markdown('<p class="poster-unavailable">Poster Unavailable</p>', unsafe_allow_html=True)
            else:
                st.image(recommended_posters[i], width=150)

            st.write(recommended_movies[i])
