#!/usr/bin/env python
# coding: utf-8

# In[294]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import ast
import scipy.sparse as sps
import seaborn as sns
get_ipython().run_line_magic('matplotlib', 'inline')


# In[319]:


# load the rating dataset
ratings_df_raw = pd.read_csv('data1/ratings.csv')
ratings_df = ratings_df_raw.copy()
ratings_df.shape


# In[296]:


#cast unix time to readable time
ratings_df['timestamp'] = [datetime.datetime.fromtimestamp(dt) for dt in ratings_df['timestamp'].values]
ratings_df['timestamp'].describe()


# In[297]:


ratings_df.head()


# In[324]:


# load movies dataset
movies_df_raw = pd.read_csv('data1/movies.csv')
movies_df = movies_df_raw.copy()
print('Shape:', movies_df.shape)
movies_df['title'].nunique()
movies_df


# In[299]:


# rating data set exploration
# plot reviews per user
plt.scatter(ratings_df['userId'].unique(), ratings_df['userId'].value_counts(normalize=False).sort_values())
plt.suptitle('Number of Reviews per UserId', fontsize=16)
plt.xlabel('Reviewer User ID', fontsize=14)
plt.ylabel('Number of Reviews', fontsize=14)
plt.grid()


# In[300]:


#distribution of ratings
ratings_df['rating'].plot.hist()
plt.suptitle('Rating Histogram', fontsize=16)
plt.xlabel('Rating Category', fontsize=14)
plt.ylabel('Rating Frequency', fontsize=14)
plt.grid()


# In[303]:


# we now clean the dataset

# remove any movies not found in the ratings set
movies_df_raw = movies_df_raw[movies_df_raw['movieId'].isin(ratings_df_raw['movieId'])]
movies_df_raw.tail()

movies_df_raw = movies_df_raw.reset_index(drop=True)
movies_df_raw['movieId_new'] = movies_df_raw.index
movies_df_raw.tail()


# In[304]:


# clean the rating dataset
ratings_df_raw = ratings_df_raw[['userId', 'movieId', 'rating']]
# we merge two dataset to find movies that have ratings
ratings_df_raw = ratings_df_raw.merge(movies_df_raw[['movieId', 'movieId_new', 'title']], on='movieId', how='inner') 
ratings_df_raw = ratings_df_raw[['userId',  'movieId_new', 'rating', 'title']]
ratings_df_raw.columns = ['userId',  'movieId', 'rating', 'title']

# clean up userids to start at 0 not 1
ratings_df_raw['userId'] -= 1
ratings_df = ratings_df_raw.copy()
ratings_df.head()


# In[305]:


a = pd.DataFrame(ratings_df['title'].unique())
a[a[0] == "Toy Story (1995)"]
movies_df_raw['title']


# In[306]:


# getting recommendation
import scipy.sparse.linalg
from sklearn.metrics import mean_absolute_error
import scipy.sparse as sps

ratings_matrix = sps.csr_matrix((ratings_df['rating'], (ratings_df['userId'], ratings_df['movieId']))).todense()

print('shape ratings_matrix:', ratings_matrix.shape)


# In[310]:


# set our seed row of ratings using movie Toy Story
movie_toy_story = (ratings_matrix[:,0])
movie_toy_story[0:20]


# In[311]:


# Euclidian distance
distances_to_movie = []
for other_movies in ratings_matrix.T:
    distances_to_movie.append(scipy.spatial.distance.euclidean(movie_toy_story, other_movies.tolist()))

# create dataframe of movie and distance scores to Toy Story 
distances_to_movie = pd.DataFrame({'movie':movies_df_raw['title'],'distance':distances_to_movie})

# sort by ascending distance (i.e. closest to movie_toy_story)
distances_to_movie = distances_to_movie.sort_values('distance')
distances_to_movie.head(10)


# In[313]:


# mahattan distance
distances_to_movie = []
for other_movies in ratings_matrix.T:distances_to_movie.append(scipy.spatial.distance.cityblock(movie_toy_story, other_movies.tolist()))
     
# create dataframe of movie and distance scores to Toy Story 
distances_to_movie = pd.DataFrame({'movie':movies_df_raw['title'],'distance':distances_to_movie})

# sort by ascending distance - i.e. closest to movie_toy_story
distances_to_movie = distances_to_movie.sort_values('distance')
distances_to_movie.head(10)


# In[315]:


#Jaccard distance
distances_to_movie = []
for other_movies in ratings_matrix.T:distances_to_movie.append(scipy.spatial.distance.jaccard(movie_toy_story, other_movies.tolist()))
     
# create dataframe of movie and distance scores to Toy Story 
distances_to_movie = pd.DataFrame({'movie':movies_df_raw['title'],'distance':distances_to_movie})

# sort by ascending distance (i.e. closest to movie_toy_story)
distances_to_movie = distances_to_movie.sort_values('distance')
distances_to_movie.head(10)


# In[316]:


# cosine distance
distances_to_movie = []
for other_movies in ratings_matrix.T:distances_to_movie.append(scipy.spatial.distance.cosine(movie_toy_story, other_movies.tolist()))
     
# create dataframe of movie and distance scores to Toy Story 
distances_to_movie = pd.DataFrame({'movie':movies_df_raw['title'],'distance':distances_to_movie})

# sort by ascending distance (i.e. closest to movie_toy_story)
distances_to_movie = distances_to_movie.sort_values('distance')
distances_to_movie.head(10)


# In[ ]:




