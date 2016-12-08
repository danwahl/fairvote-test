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
    #n = data.shape[0]
    m = procon.shape[1]
    
    # simulate election
    v = pd.DataFrame(columns = d.columns)
    for i in range(m):
        # drop voters whose ballots are exhausted
        d.dropna(how='all', inplace=True)
        
        # calculate votes
        r = d.idxmin(axis=1).value_counts()
        v = v.append(r, ignore_index=True)
        
        # check for a winner
        if float(r.max())/float(r.sum()) > 0.5:
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
    codes = pd.read_csv('usps_codes.csv', index_col=0, encoding='utf-8')
    
    # candidate info
    procon = pd.read_csv('procon_data.csv', index_col='Question')
    n = procon.shape[0]
    N = 10000
    
    # generate voters data
    print 'generating random voters'
    voters = pd.DataFrame(index=range(N), columns=procon.columns)
    for i in range(N):
        # calculate random scores and weights
        scores = np.random.randint(-1, 2, size=(n, 1))
        weights = np.random.randint(0, 4, size=(n, 1))
        
        # get weighted correlation with candidates, determine ballot rank
        v = pd.Series(weighted_corr(procon.as_matrix(), scores, weights), index=procon.columns)
        voters.iloc[i] = v[v > 0].rank(ascending=False)
        
    # generate state results
    states = results['state'].unique()
    r0 = pd.DataFrame(index=codes.code, columns=procon.columns)
    r1 = pd.DataFrame(index=codes.code, columns=procon.columns)
    print 'calculating state results'
    for s in results['state'].unique():
        # get votes by candidate
        votes = results[results['state'] == s].groupby('name').sum()['votes'][procon.columns]
        r0.loc[codes.loc[s].code] = votes
        votes.dropna(inplace=True)
 
        # generate simulated ballots       
        data = pd.DataFrame(columns=procon.columns)        
        for c in votes.index:
            data = data.append(voters[voters[c] == 1].sample(votes[c], replace=True), ignore_index=True)
        
        # run ranked vote sim (only for candidates with votes in state)
        #d = data[votes.index]
        v = ranked_vote(data[votes.index].copy())
        r1.loc[codes.loc[s].code] = v.iloc[-1]
        #print s
        #print v    
    
    r0.dropna(inplace=True, how='all')
    r0.fillna(0, inplace=True)
    r0.transpose().astype(np.int32).to_json('before.json')
    
    r1.dropna(inplace=True, how='all')
    r1.fillna(0, inplace=True)
    r1.transpose().astype(np.int32).to_json('after.json')

    