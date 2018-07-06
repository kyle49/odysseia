# -*- coding: utf-8 -*-
"""
Created on Wed Jul  4 17:36:35 2018

@author: Kyle
"""

import numpy as np
import pandas as pd
import datetime as dt
from tickDataProcessing import tickDataProcessing as TDP
from matplotlib import pyplot as plt

class estImpact:
    
    def __init__(self, stockID, path = None):
        self._DF = TDP(stockID, path)
        self._amts = [1e5]
        self._timeInterval = None
        self._method = None


    def set_times(self, targetTime):
        self._timeInterval = targetTime # a list of two or None
    
    
    def set_amts(self, targetAmount):
        if isinstance(targetAmount, float):
            self._amts = [targetAmount]
            return
        self._amts = targetAmount        
        
            
    def set_method(self, method):
        self._method = method
        # if method is None/last: target Amount will be trade only on askbook/bidbook
        # if method is mean: target Amount will be trade traded 
        # if method is provoke
        
        
            
        
    def _estExtraPrice(self, timeI, ask = True):
        # DF is a TDP object
        # timeI is a time interval
        if ask:
            self._askbook = self._DF.askBook(timeI)
            frame = self._DF.get_data(timeI, ['totalAsk', 'meanAsk'])
            prices = self._askbook.columns.values
            amountOut = frame['totalAsk'] * frame['meanAsk'] - (prices * self._askbook).sum(axis = 1)
            volOut = frame['totalAsk'] - self._askbook.sum(axis = 1)
        else:
            self._bidbook = self._DF.bidBook(timeI)
            frame = self._DF.get_data(timeI, ['totalBid', 'meanBid'])
            prices = self._bidbook.columns.values
            amountOut = frame['totalBid'] * frame['meanBid'] - (prices * self._bidbook).sum(axis = 1)
            volOut = frame['totalBid'] - self._bidbook.sum(axis = 1)
        return amountOut / volOut
    
    

        
    
    def main(self):
        exPList = self._estExtraPrice(self.timeInterval).mean()
        frame = self.DF.get_data(self.timeInterval, ['vol', 'amount'])
        vwap = frame['amount'].sum() / frame['vol'].sum()
        inPList = self.askbook.mean()
        inPList = inPList[inPList.index >= vwap].cumsum()
        estPrice = []
        inflation = []
        for _vol in self.vols:
            try:
                _estPrice = inPList.index[sum(inPList <= _vol)]
            except(IndexError):
                _estPrice = max(exPList, _estPrice)
            print("Vol intended %d, estimated trading price %.2f" %(_vol, _estPrice))
            estPrice.append(_estPrice)
            inflation.append((_estPrice - vwap) / vwap)
        return estPrice, inflation