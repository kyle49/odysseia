# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 14:46:26 2018

@author: Kyle
"""

import numpy as np

def euclid_dist(t1,t2):
    return np.sqrt(sum((t1-t2)**2))

def DTWDistance_naive(s1, s2):
    
    # Computationally expensive
    DTW={}

    for i in range(len(s1)):
        DTW[(i, -1)] = float('inf')
    for i in range(len(s2)):
        DTW[(-1, i)] = float('inf')
    DTW[(-1, -1)] = 0

    for i in range(len(s1)):
        for j in range(len(s2)):
            dist= (s1[i]-s2[j])**2
            DTW[(i, j)] = dist + min(DTW[(i-1, j)],DTW[(i, j-1)], DTW[(i-1, j-1)])

    return np.sqrt(DTW[len(s1)-1, len(s2)-1])

def DTWDistance(s1, s2, w):
    DTW={}

    w = max(w, abs(len(s1)-len(s2)))

    for i in range(-1,len(s1)):
        for j in range(-1,len(s2)):
            DTW[(i, j)] = float('inf')
    DTW[(-1, -1)] = 0

    for i in range(len(s1)):
        for j in range(max(0, i-w), min(len(s2), i+w)):
            dist= (s1[i]-s2[j])**2
            DTW[(i, j)] = dist + min(DTW[(i-1, j)],DTW[(i, j-1)], DTW[(i-1, j-1)])

    return np.sqrt(DTW[len(s1)-1, len(s2)-1])

def LB_Keogh(s1,s2,r):
    LB_sum=0
    for ind,i in enumerate(s1):

        lower_bound=min(s2[(ind-r if ind-r>=0 else 0):(ind+r)])
        upper_bound=max(s2[(ind-r if ind-r>=0 else 0):(ind+r)])

        if i>upper_bound:
            LB_sum=LB_sum+(i-upper_bound)**2
        elif i<lower_bound:
            LB_sum=LB_sum+(i-lower_bound)**2

    return np.sqrt(LB_sum)

from sklearn.metrics import classification_report

def knn(train,test,w):
    preds=[]
    for ind,i in enumerate(test):
        min_dist=float('inf')
        closest_seq=[]
        #print ind
        for j in train:
            if LB_Keogh(i[:-1],j[:-1],5)<min_dist:
                dist=DTWDistance(i[:-1],j[:-1],w)
                if dist<min_dist:
                    min_dist=dist
                    closest_seq=j
        preds.append(closest_seq[-1])
    return classification_report(test[:,-1],preds)

import random

def k_means_clust(data,num_clust,num_iter,w=5):
    centroids=data[random.sample(range(len(data)),num_clust)]
    counter=0
    for n in range(num_iter):
        counter+=1
        print (counter)
        assignments={}
        #assign data points to clusters
        for ind,i in enumerate(data):
            min_dist=float('inf')
            closest_clust=None
            for c_ind,j in enumerate(centroids):
                if LB_Keogh(i,j,5)<min_dist:
                    cur_dist=DTWDistance(i,j,w)
                    if cur_dist<min_dist:
                        min_dist=cur_dist
                        closest_clust=c_ind
            if closest_clust in assignments:
                assignments[closest_clust].append(ind)
            else:
                assignments[closest_clust]=[]

        #recalculate centroids of clusters
        for key in assignments:
            clust_sum=0
            for k in assignments[key]:
                clust_sum=clust_sum+data[k]
            centroids[key]=[m/len(assignments[key]) for m in clust_sum]

    return centroids

if __name__=='__main__':
    
    import time
    

    a = np.arange(0, 5, 0.01)
    ts1 = np.sin(a)
    ts2 = np.cos(3 * a)
    
    start_time = time.time()
    print(euclid_dist(ts1, ts2))
    print("time used: ", (time.time() - start_time)); start_time = time.time()
    print(DTWDistance_naive(ts1, ts2))
    print("time used: ", (time.time() - start_time)); start_time = time.time()
    print(DTWDistance(ts1, ts2, 50))
    print("time used: ", (time.time() - start_time)); start_time = time.time()
    print(LB_Keogh(ts1, ts2, 50))
    print("time used: ", (time.time() - start_time)); start_time = time.time()
    
    
    train = np.genfromtxt('TSC-master/datasets/train.csv', delimiter='\t')
    test = np.genfromtxt('TSC-master/datasets/test.csv', delimiter='\t')
    start_time = time.time()
    print (knn(train,test,4))
    print("time used: ", (time.time() - start_time)); start_time = time.time()
    
    data=np.vstack((train[:,:-1],test[:,:-1]))

    import matplotlib.pylab as plt

    centroids=k_means_clust(data,4,10,4)
    print("time used: ", (time.time() - start_time)); start_time = time.time()
    for i in centroids:
        plt.plot(i)
    plt.show()

##########

