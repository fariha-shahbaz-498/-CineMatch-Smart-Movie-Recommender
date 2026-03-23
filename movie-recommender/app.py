import streamlit as st
import pandas as pd
import numpy as np
import requests
import re
import webbrowser

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    movies = pd.read_csv("movies.csv")
    ratings = pd.read_csv("ratings.csv")
    data = pd.merge(ratings, movies, on="movieId")
    movie_matrix = data.pivot_table(index="userId", columns="title", values="rating")
    ratings_count = data.groupby("title")["rating"].count()
    return movies, data, movie_matrix, ratings_count

movies, data, movie_matrix, ratings_count = load_data()

# -----------------------------
# Recommendation Function
# -----------------------------
def recommend(movie_name, min_ratings=50):

    matches = [title for title in movie_matrix.columns if movie_name.lower() in title.lower()]
    
    if len(matches) == 0:
        return None, "❌ Movie not found!"

    matches = sorted(matches, key=lambda x: ratings_count.get(x, 0), reverse=True)
    movie_name = matches[0]

    popular_movies = ratings_count[ratings_count > min_ratings].index
    filtered_matrix = movie_matrix[popular_movies.union([movie_name])]

    movie_ratings = filtered_matrix[movie_name].dropna()
    similar_movies = filtered_matrix.corrwith(movie_ratings)

    corr_df = pd.DataFrame(similar_movies, columns=["Correlation"])
    corr_df.dropna(inplace=True)
    corr_df["num_ratings"] = ratings_count
    corr_df = corr_df[corr_df.index != movie_name]

    return corr_df.sort_values("Correlation", ascending=False).head(10), movie_name

# -----------------------------
# 🎬 Get Movie Details + Poster
# -----------------------------
def get_movie_details(title):
    try:
        api_key = "83c7bf60cb146010c070a90dad34a821"

        clean_title = re.sub(r"\(\d{4}\)", "", title).strip()

        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={clean_title}"
        data = requests.get(url).json()

        if data['results']:
            movie = data['results'][0]

            poster = "https://image.tmdb.org/t/p/w500" + movie['poster_path'] if movie['poster_path'] else None
            overview = movie.get("overview", "No description available")
            rating = movie.get("vote_average", "N/A")
            release = movie.get("release_date", "N/A")

            return poster, overview, rating, release

        return None, "No info", "N/A", "N/A"

    except:
        return None, "Error", "N/A", "N/A"

# -----------------------------
# 🎬 Trailer Function
# -----------------------------
def get_trailer_url(title):
    clean_title = re.sub(r"\(\d{4}\)", "", title).strip()
    query = clean_title.replace(" ", "+")
    return f"https://www.youtube.com/results?search_query={query}+trailer"

# -----------------------------
# 🎨 UI Styling
# -----------------------------
st.set_page_config(page_title="CineMatch", layout="wide")

st.markdown("""
<style>
.title {
    font-size: 45px;
    font-weight: bold;
    color: #E50914;
    text-align: center;
}
.movie-card {
    transition: transform 0.3s ease;
}
.movie-card:hover {
    transform: scale(1.08);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🎥 CineMatch – Smart Movie Recommender</div>", unsafe_allow_html=True)

# -----------------------------
# Search
# -----------------------------
movie_input = st.selectbox("🔍 Search Movie:", sorted(movies['title'].tolist()))

# -----------------------------
# Selected Movie Section
# -----------------------------
if movie_input:
    poster, overview, rating, release = get_movie_details(movie_input)

    st.subheader("🎯 Selected Movie")

    col1, col2 = st.columns([1, 2])

    with col1:
        if poster:
            st.image(poster, use_container_width=True)

    with col2:
        st.markdown(f"### {movie_input}")
        st.markdown(f"⭐ Rating: **{rating}**")
        st.markdown(f"📅 Release Date: **{release}**")
        st.markdown(f"📝 {overview}")

        # 🎬 Watch Trailer Button
        if st.button("▶ Watch Trailer"):
            webbrowser.open(get_trailer_url(movie_input))

    # -----------------------------
    # Recommendations
    # -----------------------------
    recommendations, selected_movie = recommend(movie_input)

    st.subheader("🔥 Recommended For You")

    cols = st.columns(5)

    for idx, (title, row) in enumerate(recommendations.iterrows()):
        poster, _, _, _ = get_movie_details(title)

        with cols[idx % 5]:
            if poster:
                st.markdown("<div class='movie-card'>", unsafe_allow_html=True)
                st.image(poster, use_container_width=True)
                st.markdown(f"**{title}**")

                # 🎬 Play Button
                if st.button("▶ Play", key=title):
                    webbrowser.open(get_trailer_url(title))

                st.markdown("</div>", unsafe_allow_html=True)
                st.divider()

# -----------------------------
# ABOUT SECTION
# -----------------------------
st.divider()

st.markdown("""
## 📌 About CineMatch

CineMatch is a Machine Learning-powered movie recommendation system  
that helps users discover movies based on their interests.

### 🚀 Features
- Personalized recommendations  
- Smart search  
- Movie posters & details  
- Trailer links  

### 🧠 Tech Stack
Python • Pandas • ML • Streamlit • TMDB API  

""")

# -----------------------------
# FOOTER
# -----------------------------
st.markdown("""
<hr style="border:1px solid #444">

<div style='text-align: center; color: gray; font-size: 14px;'>

© 2026 CineMatch 🎥 | Built with  using Machine Learning  

</div>
""", unsafe_allow_html=True)