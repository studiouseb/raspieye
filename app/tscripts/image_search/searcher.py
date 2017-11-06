# -*- coding: utf-8 -*-
"""
Created on Wed Nov  1 04:15:39 2017

@author: seb
"""

import numpy as np
import csv

class Searcher:
    def __init__(self, indexPath):
        #store the index path
        self.indexPath = indexPath
        
    def search(self, queryFeatures, limit=10):
        #initialse results dictionary
        results = {}
        #open the index file for reading
        with open(self.indexPath) as f:
            #initialise the csvreader
            reader = csv.reader(f)
            
            #loop over the rows in the index
            for row in reader:
                #parse the image and features, compute chi squared distance
                #between indexed features and query features
                features = [float(x) for x in row[1:]]
                d = self.chi2_distance(features, queryFeatures)
                
                #with the distance in hand, update the results dict
                #key is current imageID in index and the value is the distance computed
                #represents similarity
                results[row[0]] = d
                
            #close reader
            f.close()
            
        #sort results, so smaller distances are front of list
        results = sorted([(v, k) for (k, v) in results.items()])
        
        #return limited results
        return results[:limit]
        
    def chi2_distance(self, histA, histB, eps = 1e-10):
        #compute the chi-squared distance
        d = 0.5 * np.sum([((a - b) ** 2) / (a + b + eps)
            for (a, b) in zip(histA, histB)])
                
        #return the chi-squared distance
        return d
            