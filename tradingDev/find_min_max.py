# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 09:26:43 2018

@author: Kyle
"""

from tickDataProcessing import tickDataProcessing as TDP
import numpy as np
from matplotlib import pyplot as plt

DF = TDP('600519')
prices = np.array(DF.get_data()['last'])

def speaker(sr, rate = .05):
    delta = (sr[-1] - sr[0]) / len(sr)
    sr = sr - np.arange(len(sr)) * delta
    return sr * (np.arange(len(sr)) * rate)
plt.plot(speaker(prices))
plt.show()

def min_max(sr, burnIn = .1):
    n = len(sr)
    _start = int(n * burnIn)
    sr_prior = sr[0:_start]
    _min, _max = sr_prior.min(), sr_prior.max()
    _argmin, _argmax = sr_prior.argmin(), sr_prior.argmax()
    minList = [_argmin]
    maxList = [_argmax]
    for i in np.arange(_start, n):
        if sr[i] > _max:
            _max = sr[i]
            _argmax = i
            maxList[-1] = i
            minList.append(_argmin)
        elif sr[i] < _min:
            _min = sr[i]
            _argmin = i
            minList[-1] = i
            maxList.append(_argmax)
    minList.append(_argmin)
    maxList.append(_argmax)
    return np.unique(minList), np.unique(maxList)

deeps, peaks = min_max(speaker(prices))
plt.plot(prices)
plt.plot(peaks, prices[peaks])
plt.plot(deeps, prices[deeps])
plt.show()

def rand_window_scanner(sr, nIter = 10000):
    a = np.random.rand(nIter, 2)
    L = a.min(axis = 1)
    R = a.max(axis = 1)
    n = len(sr)
    L = (L * n).astype(int)
    R = (R * n).astype(int)
    R[L-R == 0] += 1
    _max = []
    _min = []
    for i in np.arange(n):
        try:
            seg = sr[L[i]:R[i]]
        except(IndexError):
            continue
        _max.append(L[i] + seg.argmax())
        _min.append(L[i] + seg.argmin())
    return _max, _min

# plot histogram