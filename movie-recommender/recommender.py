# ==========================================
# Movie Recommendation System (Robust Fixed)
# ==========================================

import pandas as pd
import numpy as np
import warnings

warnings.filterwarnings("ignore")

# Load Data
movies = pd.read_csv("movies.csv")
ratings = pd.read_csv("ratings.csv")

# Merge Data
data = pd.merge(ratings, movies, on="movieId")

# User-Movie Matrix
movie_matrix = data.pivot_table(index="userId", columns="title", values="rating")

# Recommendation Function
def recommend(movie_name, min_ratings=50):
    # Find matching movies
    matches = [title for title in movie_matrix.columns if movie_name.lower() in title.lower()]
    
    if len(matches) == 0:
        return "❌ Movie not found!"
    
    # If multiple matches, ask user to pick
    if len(matches) > 1:
        print("\nMultiple movies found:")
        for i, title in enumerate(matches, 1):
            print(f"{i}. {title}")
        while True:
            try:
                choice = int(input("Enter the number of the correct movie: "))
                if 1 <= choice <= len(matches):
                    movie_name = matches[choice - 1]
                    break
                else:
                    print("❌ Invalid number, try again.")
            except ValueError:
                print("❌ Enter a valid number.")
    else:
        movie_name = matches[0]
    
    print(f"\n✅ Using movie: {movie_name}")
    
    # Ratings count
    ratings_count = data.groupby("title")["rating"].count()
    
    # Make filtered matrix for correlations (exclude unpopular movies only for correlation)
    popular_movies = ratings_count[ratings_count > min_ratings].index
    filtered_matrix = movie_matrix[popular_movies.union([movie_name])]  # include selected movie
    
    # Compute correlations
    movie_ratings = filtered_matrix[movie_name].dropna()
    similar_movies = filtered_matrix.corrwith(movie_ratings)
    
    corr_df = pd.DataFrame(similar_movies, columns=["Correlation"])
    corr_df.dropna(inplace=True)
    corr_df["num_ratings"] = ratings_count
    corr_df = corr_df[corr_df.index != movie_name]
    
    # Sort by correlation
    recommendations = corr_df.sort_values("Correlation", ascending=False)
    
    return recommendations.head(10)

# Main Program
if __name__ == "__main__":
    print("🎬 Movie Recommendation System")
    print("---------------------------------")
    
    print("\n📂 Sample Movies You Can Try:\n")
    print(movies['title'].head(20).to_string(index=False))
    
    while True:
        movie_input = input("\nEnter a movie name (or type 'exit'): ")
        if movie_input.lower() == "exit":
            print("👋 Exiting...")
            break
        
        results = recommend(movie_input)
        print("\n📌 Recommendations:\n")
        print(results)