import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


# Load the data
users = pd.read_csv('ml-100k/u.user', sep='|', header=None, names=['user_id', 'age', 'gender', 'occupation', 'zip_code'])
ratings = pd.read_csv('ml-100k/u.data', sep='\t', header=None, names=['user_id', 'movie_id', 'rating', 'timestamp'])
movies = pd.read_csv('ml-100k/u.item', sep='|', header=None, encoding='latin-1',
                     names=['movie_id', 'movie_title', 'release_date', 'video_release', 'IMDb_URL', 'unknown', 'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'])


# Calculate the mean age by occupation
mean_age_by_occupation = users.groupby('occupation')['age'].mean()

print(mean_age_by_occupation)


# Filter for movies with at least 35 ratings
movie_ratings_count = ratings.groupby('movie_id').size()
movies_with_enough_ratings = movie_ratings_count[movie_ratings_count >= 35].index

# Calculate the average rating for these movies
average_ratings = ratings[ratings['movie_id'].isin(movies_with_enough_ratings)].groupby('movie_id')['rating'].mean()

# Merge with movie titles and sort by rating
top_20_movies = pd.merge(average_ratings, movies[['movie_id', 'movie_title']], on='movie_id').sort_values(by='rating', ascending=False).reset_index(drop=True).head(20)

print(top_20_movies)

# Merge the user and rating data
user_ratings = pd.merge(ratings, users, on='user_id')

# Define age groups
age_bins = [20, 25, 35, 45, 100]
age_labels = ['20-25', '25-35', '35-45', '45+']
users['age_group'] = pd.cut(users['age'], bins=age_bins, labels=age_labels, right=False)

# Merge movies and ratings data
movies_ratings = pd.merge(ratings, movies[['movie_id', 'movie_title', 'Action', 'Comedy', 'Drama']], on='movie_id')

# Combine with user info
user_movie_data = pd.merge(movies_ratings, users, on='user_id')

# Group by occupation, age group, and genre and calculate the sum of genre counts
top_genres_by_occupation_age = user_movie_data.groupby(['occupation', 'age_group']).agg({
    'Action': 'sum',
    'Comedy': 'sum',
    'Drama': 'sum'
}).reset_index()

print(top_genres_by_occupation_age.columns)
print(top_genres_by_occupation_age[top_genres_by_occupation_age['occupation']=='writer'])


# Create a user-item matrix (movies as columns, users as rows)
user_movie_matrix = ratings.pivot_table(index='movie_id', columns='user_id', values='rating').fillna(0)

# Calculate cosine similarity between movies
movie_similarity = cosine_similarity(user_movie_matrix)

# Create a DataFrame for similarity scores
movie_similarity_df = pd.DataFrame(movie_similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)
co_occurrence = (user_movie_matrix).dot(user_movie_matrix.T)

# Function to get top 10 similar movies for a given movie, with constraints on similarity and co-occurrence
def get_similar_movies(movie_id, top_n=10, similarity_threshold=0.75, co_occurrence_threshold=50):
    # Compute co-occurrence matrix (how many times two movies have been rated together by the same users)
    co_occurrence_count = co_occurrence[movie_id]
    co_occurrence_count = co_occurrence_count[co_occurrence_count.index != movie_id]
    co_occurrence_count = co_occurrence_count[co_occurrence_count>co_occurrence_threshold]
    # Apply the similarity and co-occurrence thresholds, ensuring proper alignment
    similar_movies = movie_similarity_df[movie_id].loc[co_occurrence_count.index]  # Align indices
    similar_movies = similar_movies[similar_movies.index != movie_id]
    
    # Filter based on co-occurrence and similarity thresholds
    filtered_movies = similar_movies[similar_movies >= similarity_threshold]
    
    # Sort by similarity and return top N
    top_similar_movies = filtered_movies.sort_values(ascending=False).head(top_n)
    
    # Convert the Series to DataFrame and reset the index
    top_similar_movies_df = top_similar_movies.reset_index()
    if len(top_similar_movies_df) > 0:
        top_similar_movies_df.columns = ['movie_id', 'similarity_score']  # Rename columns
        
        # Merge with movie titles
        top_similar_movies_with_titles = pd.merge(top_similar_movies_df, movies[['movie_id', 'movie_title']], on='movie_id')
        return top_similar_movies_with_titles
    else:
        return None

similar_movies = {}
for i in range(1, 1683):
    df = get_similar_movies(i)
    if df is not None:
        similar_movies.update({i :df})

print(similar_movies.keys())

# [50, 59, 60, 61, 71, 79, 95, 96, 121, 165, 166, 172, 174, 176, 181, 183, 195, 204, 210, 226, 227, 228, 229, 230, 266, 405, 550, 680]
# only these movies have similar movies with similarity_threshold >=0.75