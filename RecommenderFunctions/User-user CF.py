
# coding: utf-8

# In[1]:

import pandas as pd
import numpy as np


# In[2]:

path = "set-path-to-data"


# In[75]:

#load the data
user_row = (pd
            .read_csv(path + "user-row.csv")
            .set_index("Unnamed: 0"))

correlations = (pd
                .read_csv(path + "correlations.csv")
                .set_index("Unnamed: 0")
                .fillna(0))


# In[98]:

def get_n_closest_neighbours(correlations, input_user, n):
    """
    Get n closest neighbours to the input_user, 
    based on user correlations
    
    Args:
        correlations - DataFrame: correlations between users
        input_user - int: id of user
        n - int: number of neighbours to consider
        
    Return:
        DataFrame
    """
    user_cor = correlations.loc[input_user]
    #order according to correlation
    user_cor.sort(ascending = False)
    
    #return top n, excluding itself
    return user_cor.iloc[1: (n+1)]


# In[99]:

def get_corr_weighted_avg(input_user, correlations, user_row, n, normalize = False):
    """
    Get predictions for user_input based on the user-user CF
    
    sum_1^n(r_n * w_n) / sum_1^n(w_n)
    
    Args:
        correlations - DataFrame: correlations between users
        input_user   - int: id of user
        n            - int: number of neighbours to consider
        user_row     - DataFrame: rating matrix
        normalize    - bool: if True use normalized formula 
                            r_u~ + sum_1^n((r_n - r_n~) * w_n) / sum_1^n(w_n)
    """
    #get top n neighbours
    top_n_neighbours = get_n_closest_neighbours(correlations,
                                                input_user,
                                                n)
    #their index
    top_n_ids = [int(x) for x in top_n_neighbours.index.values]
    #subset rankings
    top_n_movie_ratings = user_row.loc[top_n_ids]
    
    top_n_movie_ratings_new = top_n_movie_ratings.copy()
    for id_usr in top_n_neighbours.index.values:
        if normalize: #substract meant
            (top_n_movie_ratings_new
             .loc[int(id_usr)]) -= \
            (top_n_movie_ratings
             .loc[int(id_usr)]
             .mean())
        #weight by correlation
        top_n_movie_ratings_new.loc[int(id_usr)] *= top_n_neighbours.loc[id_usr]
    
    #get correlation only of users who rated the movie per movie
    sum_corr = []
    for movie in top_n_movie_ratings_new.columns:
        this_corr = (top_n_neighbours
                     .ix[top_n_movie_ratings_new
                         .ix[:,movie]
                         .notnull()
                         .values]
                     .sum())
        sum_corr.append(this_corr)
    #predict scores    
    prediction = (top_n_movie_ratings_new
                  .sum(axis = 0)
                  .divide(sum_corr))
    #add avg score of target user
    if normalize:
        prediction += (user_row.loc[input_user]
                       .mean())
    #sort
    prediction.sort(ascending = False)
    
    return prediction
    
#Example
#get_corr_weighted_avg(89, correlations, user_row, 5, True)

