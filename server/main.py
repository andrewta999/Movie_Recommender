from flask import Flask, jsonify,  request
from scipy.sparse.linalg import svds
import scipy.sparse as sps
import numpy as np 
import pandas as pd 
import tmdbsimple as tmdb 
import json 
from flask_cors import CORS, cross_origin


tmdb.API_KEY = '7f0a3676a16634d796f37dc1a852c29b'
BASE_URL = "https://image.tmdb.org/t/p/w300"


def GetSparseSVD(ratings_centered_matrix, K):
    u, s, vt = svds(ratings_centered_matrix, k=K)
    sigma = np.diag(s)
    return u, sigma, vt

def get_poster(title):
    search = tmdb.Search()
    search.movie(query=title)
    res = search.results[0]
    return BASE_URL + res['poster_path']

def convert(data):
    history = []
    for i in data:
        history.append(int(i))
    return history

def GetRecommendedMovies(user_history_movie_ids):
    ratings_df = ratings.copy()
    ratings_df = ratings_df[['userId', 'movieId', 'rating']]
    
    # create a new user id - add 1 to current largest
    new_user_id = np.max(ratings_df['userId']) + 1

    new_user_movie_ids = user_history_movie_ids
    new_user_ratings = 4.5

    new_data = pd.DataFrame([[new_user_id, i, new_user_ratings] for i in new_user_movie_ids], columns=['userId', 'movieId', 'rating'])
    ratings_df = ratings_df.append(new_data, ignore_index=True)
    
    # fix index to be multilevel with userId and movieId
    ratings_df.set_index(['userId', 'movieId'], inplace=True)
    
    # create new ratings_matrix
    ratings_matrix_plus = sps.csr_matrix((ratings_df.rating,(ratings_df.index.codes[0], ratings_df.index.codes[1]))).todense()

    user_ratings_mean = np.mean(ratings_matrix_plus, axis = 1)
    ratings_matrix_centered = ratings_matrix_plus - user_ratings_mean.reshape(-1, 1)

    Ua, sigma, Vt = GetSparseSVD(ratings_matrix_centered, K=50)
    all_user_predicted_ratings = np.dot(np.dot(Ua, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
    
    # predictions_df based on row/col ids, not original movie ids
    predictions_df = pd.DataFrame(all_user_predicted_ratings, columns = movies.index)  

    # Get and sort the user's predictions
    suggestions = predictions_df.iloc[new_user_id].sort_values(ascending=False)
    suggestions = pd.DataFrame(suggestions).reset_index()
    suggestions.columns = ['movieId', 'predictions']
    suggestions = suggestions.merge(movies, left_on='movieId', right_on='movieId', how='inner').sort_values('predictions', ascending=False)
    suggestions = suggestions[~suggestions['movieId'].isin(new_user_movie_ids)]
    suggestions = suggestions.head(20).reset_index()

    #get poster url for each movie
    data = []
    for i in range(20): 
        data.append(get_poster(suggestions['titles'].iloc[i]))

    suggestions['url'] = pd.Series(data)
    suggestions = suggestions[['movieId', 'title', 'url']].to_json(orient="records")
    return json.loads(suggestions)

ratings = None
movies = None

app = Flask(__name__)
#CORS(app)

@app.before_first_request
def init():
    global movies, ratings 
    movies = pd.read_csv('./movies.csv')
    ratings = pd.read_csv('./ratings.csv')

# get recommendations provided history movie ids
@app.route('/recommend', methods=['GET'])
@cross_origin()
def get_recommendation():
    req_data = str(request.args.get('ids'))
    movies_history = req_data.split(' ')
    history = convert(movies_history)
    recommendations = GetRecommendedMovies(history)
    response = jsonify(recommendations)
    return response  

# get search movies
@app.route('/search', methods=['GET'])
@cross_origin()
def search():
    key = request.args.get('query')
    key = key.lower()
    filter_pd = movies['titles'].str.contains(key, na=False)
    filter_res = movies[filter_pd]
    res = filter_res[['movieId', 'title']].to_json(orient="records")
    response = jsonify(json.loads(res))
    return response 

if __name__ == '__main__':
    app.run(debug=True)
