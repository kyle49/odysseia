# -*- coding: utf-8 -*-
"""
Created on Thu Mar 29 14:10:28 2018

@author: Kyle
@origin: Adavance in Financial Machine Learning
"""

import numpy as np

def pmf1(msg, w):
    # Compute p.m.f. for 1-D discrete r.v.
    # len(msg) - w: occurrences
    lib = {}
    if not isinstance(msg, str):
        msg = ''.join(map(str,msg))
    for i in range(w,len(msg)):
        msg_ = msg[i - w:i]
        if msg_ not in lib:
            lib[msg_] = [i - w]
        else:
            lib[msg_] = lib[msg_] + [i - w]
    pmf = float(len(msg) - w)
    pmf = {i:len(lib[i])/pmf for i in lib}
    return pmf


def plugIn(msg, w):
    # Compute plug-in (ML) entropy rate
    pmf = pmf1(msg, w)
    out = -sum([pmf[i] * np.log2(pmf[i]) for i in pmf])/w
    return out,pmf


def lempelZiv_lib(msg):
    if not isinstance(msg, str):
        msg = ''.join(map(str,msg))
    i, lib = 1, [msg[0]] 
    while i<len(msg):
        for j in range(i, len(msg)):
            msg_ = msg[i:j+1]
            if msg_ not in lib:
                lib.append(msg_)
                break
        i = j + 1
    return lib


def matchLength(msg, i, n):
    # Maximum matched length + 1, with overlap.
    # i >= n & len(msg) >= i+n
    if not isinstance(msg, str):
        msg = ''.join(map(str,msg))
    subS = ''
    for j in range(n):
        msg1 = msg[i:i + j + 1]
        for k in range(i - n, i):
            msg0 = msg[k:k + j + 1]
            if msg0 == msg1:
                subS = msg1
                break
    return 1 + len(subS),subS # matched length + 1


def konto(msg, window = None):
    """
    Inverse of the avg length of the shortest non-redundant substring.
    If non-redundant substrings are short, the text is highly entropic.
    window == None for expanding window, in which case len(msg)%2 == 0
    If the end of msg is more relevant, try konto(msg[::-1]) i.e. inverse order
    """
    out = {'num':0, 'sum':0, 'subS':[]}
    if not isinstance(msg, str):
        msg = ''.join(map(str,msg))
    else:
        if window == None:
            window = int(len(msg)/2)
        else:
            window = min(window, len(msg)/2)
        points = range(window, len(msg) - window + 1)
    for i in points:
        if window is None:
            _, msg_ = matchLength(msg, i, i)
            out['sum'] += np.log2(i + 1)/1
        else:
            _, msg_ = matchLength(msg, i, window)
            out['sum'] += np.log2(window + 1)/1
        out['subS'].append(msg_)
        out['num'] += 1
    out['h'] = out['sum']/out['num']
    out['r'] = 1 - out['h']/np.log2(len(msg)) # redundancy 0<=r<=1
    return out


def Encoding (vec, sep = None, method = "Bar", nQ = 2, split = 0.5):
    if sep == None: sep = []
    codes = [str(i) for i in range(10)] + [chr(i) for i in range(ord('a'), ord('z')+1)]
    if method == "Quantile":
        sampleLen = int(len(vec) * split)
        quantileSize = int(sampleLen / nQ)
        for i in range(nQ - 1):
            a = np.sort(vec[0:sampleLen])
            sep.append(a[(i+1) * quantileSize])
    if method == "Sigma":
        init = min(vec)
        sigma = (max(vec) - init) / nQ
        for i in range(nQ - 1):
            sep.append(init + (i+1) * sigma)
    msg = str()
    sep = np.array(sep)
    for i in range(len(vec)):
        msg += codes[sum(sep < vec[i])]
    return msg

if __name__ == '__main__':
    
    # Demo
    msg = '101010'
    print(konto(msg*2))
    print(konto(msg + msg[::-1]))
    
    # Ques.3
    import random
    import matplotlib.pyplot as plt
    
    g = random.Random()
    g.seed(2018)
    X = [g.gauss(0,1) for i in range(1000)]
    
    def NormalEntropy (sigma):
        return 0.5 * np.log(2*np.pi*np.e*sigma)
    
    print("Theoritical entropy: ", NormalEntropy(1))
    
    X1 = Encoding(X, method = "Sigma", nQ = 8)
    X2 = Encoding(X, method = "Quantile", nQ = 8)
    
    print(plugIn(X1, w = 1)[0])
    print(plugIn(X2, w = 1)[0])
    out = konto(X2, window=10)
    print(out['h'])
    out = konto(X2, window=100)
    print(out['h'])
    
    # Ques.4
    
    y = [0]
    for i in range(len(X)):
        y.append(X[i] + 0.5 * y[i])
    
    plt.plot(y)
    plt.show()
    Y1 = Encoding(y, method = "Sigma", nQ = 8)
    Y2 = Encoding(y, method = "Quantile", nQ = 8)
    print(plugIn(Y1, w = 1)[0])
    print(plugIn(Y2, w = 1)[0])
    out = konto(Y2, window=10)
    print(out['h'])
    out = konto(Y2, window=100)
    print(out['h'])
