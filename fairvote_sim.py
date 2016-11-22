# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 18:39:38 2016

@author: dan
"""

import numpy as np
import pandas as pd

def weighted_corr(data, s, w):
    # append scores to data
    d = np.hstack((data, s))
    
    # take weighted average
    a = np.average(d, 0, w[:,0])
    
    # calculate weighted variance and covariance wrt scores
    v = np.sum(w*(d - a)**2, axis=0)/np.sum(w)
    c = np.sum(w*((d - a).transpose()*(d - a)[:, -1]).transpose(), axis=0)/np.sum(w)
    
    # return weighted corr
    return (c/np.sqrt(v*v[-1]))[:-1]

def ranked_vote(d):
    n = data.shape[0]
    m = procon.shape[1]
    
    # simulate election
    v = pd.DataFrame(columns = d.columns)
    for i in range(m):
        r = d.idxmin(axis=1).value_counts()
        v = v.append(r, ignore_index=True)
        
        # check for a winner
        if float(r.max())/n > 0.5:
            break
        # otherwise drop the loser and continue
        else:
            d.drop(r.idxmin(), axis=1, inplace=True)
    
    v.fillna(0, inplace=True)
    return v
    
if __name__ == '__main__':
    # election "results"
    results = pd.read_csv('presidential_general_election_2016.csv')
    results['name'].replace('^[A-Z]. ', '', inplace=True, regex=True)
    
    # candidate info
    procon = pd.read_csv('procon_data.csv', index_col='Question')
    n = procon.shape[0]
    N = 10000
    
    # generate voters data
    voters = pd.DataFrame(index=range(N), columns=procon.columns)
    for i in range(N):
        # calculate random scores and weights
        scores = np.random.randint(-1, 2, size=(n, 1))
        weights = np.random.randint(0, 4, size=(n, 1))
        
        # get weighted correlation with candidates, determine ballot rank
        v = pd.Series(weighted_corr(procon.as_matrix(), scores, weights), index=procon.columns)
        voters.iloc[i] = v.rank(ascending=False)
    
    # generate state results
    for s in results['state'].unique():
        # get votes by candidate
        votes = results[results['state'] == s].groupby('name').sum()['votes'][procon.columns]
        votes.dropna(inplace=True)
 
        # generate simulated ballots       
        data = pd.DataFrame(columns=procon.columns)        
        for c in votes.index:
            data = data.append(voters[voters[c] == 1].sample(votes[c], replace=True), ignore_index=True)
        
        # run ranked vote sim (only for candidates with votes in state)
        v = ranked_vote(data[votes.index])
        print s
        print v    
        