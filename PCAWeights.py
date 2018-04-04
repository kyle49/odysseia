# -*- coding: utf-8 -*-
"""
Created on Wed Apr  4 12:22:00 2018

@author: Kyle
@origin: Adavance in Financial Machine Learning
"""

import numpy as np
#import pandas as pd

def pcaWeights(cov, riskDist = None, riskTarget = 1.):
    # Following the riskAlloc dist., match riskTarget
    eVal, eVec = np.linalg.eigh(cov) # cov must be Hermitian
    indices = eVal.argsort()[::-1]
    eVal, eVec = eVal[indices], eVec[:,indices]
    if riskDist is None:
        riskDist = np.zeros(cov.shape[0])
        riskDist[-1] = 1.
    loads = riskTarget * (riskDist/eVal) ** 0.5
    wghts = np.dot(eVec, np.reshape(loads, (-1,1)))
    #ctr = (loads/riskTarget)**2 * eVal # verify riskDist
    return wghts

