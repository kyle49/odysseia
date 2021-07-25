# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 15:31:09 2018

@author: Kyle
"""

import numpy as np
from random import gauss
from itertools import product

def gridSearch(sigma=1, maxHP=100):
    rPT = rSLm = np.linspace(0, 10, 21)
    count = 0
    out = {}
    for prod_ in product([10, 5, 0, -5, -10], [5, 10, 25, 50, 100]):
        print(prod_)
        count += 1
        coeffs = {'forecast': prod_[0], 'HL': prod_[1], 'sigma':sigma}
        out[count] = batch(coeffs, nIter=1e5, maxHP=maxHP, rPT=rPT, rSLm=rSLm)
    return out

def batch(coeffs, nIter=1e4, maxHP=100, rPT=np.linspace(0, 10, 11), rSLm=np.linspace(0, 10, 11), seed=0):
    phi = 2**(-1./ coeffs['HL'])
    out1 = []
    for comb_ in product(rPT, rSLm):
        out2 = []
        for iter_ in range(int(nIter)):
            p, hp = seed, 0
            while True:
                p = (1 - phi) * coeffs['forecast'] + phi * p + coeffs['sigma'] * gauss(0, 1)
                cP = p - seed
                hp += 1
                if cP > comb_[0] or cP < -comb_[1] or hp > maxHP:
                    out2.append(cP)
                    break
        mean_ = np.mean(out2)
        std_ = np.std(out2)
        print("In (%.1f, %.1f) mean %.3f, std %.3f and sharpe %.3f"
              %(comb_[0], comb_[1], mean_, std_, mean_/std_))
        out1.append((comb_[0], comb_[1], mean_, std_, mean_/std_))
    return out1



from matplotlib import pyplot as plt
import pandas as pd

def heatmap(item, title = "Heat Map", save = False):

    frame = pd.DataFrame(item)
    rowName = frame[0].unique()
    colName = frame[1].unique()
    out = frame[4].values.reshape([len(rowName), len(colName)])
    im, ax = plt.subplots()
    im = plt.imshow(out, cmap = 'bone')
    ax.set_xticks(np.arange(len(colName)))
    ax.set_yticks(np.arange(len(rowName)))
    ax.set_xticklabels(colName, rotation = 90)
    ax.set_yticklabels(rowName)
    ax.set_xlabel("Stop loss")
    ax.set_ylabel("Profit take")
    ax.set_title(title)
    cbar = plt.colorbar(im)
    if save:
        plt.savefig('Heatmaps/' + title + '.png', bbox_inches='tight')
    plt.show(im, cbar)
    
    
if __name__ == '__main__':
    
    res = gridSearch()
    count = 0
    for prod_ in product(['XPosi', 'Posi', 'Zero', 'Nega', 'XNega'],
                         ['XQuick', 'Quick', 'Quater', 'Half', 'Full']):
        title_ = prod_[0] + '-' + prod_[1]
        count += 1
        heatmap(res[count], title = title_, save = True)