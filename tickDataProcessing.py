# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:37:28 2018

@author: Kyle
"""

import numpy as np
import pandas as pd
import datetime as dt

class tickDataProcessing:
    
    def __init__(self, stockID, path = 'dataPackages/'):        
        # time intervals measured in minute
        # path = None if data is in local file        
        name = stockID + '.csv'
        if path is not None:
            name = path + name
        df = pd.read_csv(name, index_col = 0, header = None, sep = " ")
        df = df[df.index >= 93000000]
        names = ['status', 'trades', 'vol', 'amount', 'totalAsk', 'totalBid', 'prev', 
                 'cumVol', 'cumAmount', 'last', 'meanAsk', 'meanBid'] + \
                 self.pasteName('ask') + self.pasteName('askVol') + \
                 self.pasteName('bid') + self.pasteName('bidVol')
        df.columns = names
        self._rawDF = df
        self._sampleDF = df
        
        
    @staticmethod
    def pasteName(name, n = 10):
        out = []
        for i in range(n):
            out.append(name + str(i + 1))
        return out
    
    
    def get_data(self, timeI = None, args = ['last'], convert = False):
        # time should be a list of start-time and end-time in NUM or time format
        # 'askbook' and 'bidbook' are short-cuts to call the ten-level ask/bid order book
        if 'askbook' in args:
            args += self.pasteName('ask') + self.pasteName('askVol')
            args.remove('askbook')
        if 'bidbook' in args:
            args += self.pasteName('bid') + self.pasteName('bidVol')
            args.remove('bidbook')
        if timeI is None:
            out = self._sampleDF[args]
        else:
            start_, end_ = timeI[0], timeI[1]
            df = self._sampleDF
            if isinstance(timeI[0], dt.time):    
                start_ = int(timeI[0].hour *1e7 + timeI[0].minute *1e5 + timeI[0].second *1e3)
            if start_ < 93000000: start_ = 93000000
            df = df[df.index >= start_]
            if isinstance(timeI[1], dt.time):
                end_ = int(timeI[1].hour *1e7 + timeI[1].minute *1e5 + timeI[1].second *1e3)
            if end_ > 150000000: end_ = 150000000
            df = df[df.index <= end_]
            out = df[args]
        if convert:
            return self.convert_to_time(out)
        else:
            return out


    @staticmethod
    def convert_to_time(df):
        df.index = pd.Series(df.index).apply(lambda t: 
            dt.time(int(t//1e7), int(t %1e7//1e5), int(t %1e5//1e3)))    

            
    def sampling(self, df = None, jump = 10, loc = -1):
        if df is None:
            df = self._rawDF
        if loc < 0:
            loc = np.random.randint(jump)
        n = int(len(df) / jump)
        self._sampleDF = df.iloc[np.arange(n) * jump + loc, :]
        return self._sampleDF
        
    
    def reset(self):
        self._sampleDF = self._rawDF
        
            
    def askBook(self, timeI):
        df = self.get_data(timeI, ['askbook'])
        # Generate the observed matrix
        _max = df['ask10'].values
        valid_ = pd.DataFrame(columns = np.unique(df.iloc[:,0:10].values))
        for i in _max:
            valid_ = valid_.append(pd.Series([0], index = [i]), ignore_index = True)
        valid_.fillna(method = 'bfill', axis = 1, inplace = True)
        # Form the data matrix
        Dic = {}
        for i in range(len(df)):
            dic = {}
            for j in range(10):
                dic[df.iloc[i, j]] = df.iloc[i, 10 + j]
            Dic[i] = dic
        data_ = pd.DataFrame(Dic).transpose()
        out = valid_ + data_.fillna(value = 0)
        out.fillna(method = 'ffill', inplace = True)
        out.index = df.index
        return out


    def bidBook(self, timeI):
        df = self.get_data(timeI, ['bidbook'])
        # Generate the observed matrix
        _max = df['bid10'].values
        valid_ = pd.DataFrame(columns = np.unique(df.iloc[:,0:10].values))
        for i in _max:
            valid_ = valid_.append(pd.Series([0], index = [i]), ignore_index = True)
        valid_.fillna(method = 'ffill', axis = 1, inplace = True)
        # Form the data matrix
        Dic = {}
        for i in range(len(df)):
            dic = {}
            for j in range(10):
                dic[df.iloc[i, j]] = df.iloc[i, 10 + j]
            Dic[i] = dic
        data_ = pd.DataFrame(Dic).transpose()
        out = valid_ + data_.fillna(value = 0)
        out.fillna(method = 'ffill', inplace = True)
        out.index = df.index
        return out
    

    def get_stats(self, timeIntervals = 5):
        df = self._rawDF
        initTime = 93000000
        intervalTime = timeIntervals * 1e5
        out = pd.DataFrame()
        while(initTime < 150000000):
            dfc = df[df.index <= initTime + intervalTime]
            df = df[df.index > initTime + intervalTime]
            initTime = round(df.index[0], -5)
            if len(dfc) < 1:
                continue
            if initTime > 113000000 and initTime < 130000000:
                initTime = 130000000
                continue
            _high = dfc['last'].max()
            _low = dfc['last'].min()
            _open = dfc['last'].iloc[0]
            _close = dfc['last'].iloc[-1]
            _vol = dfc['vol'].sum()
            _amount = dfc['amount'].sum()
            if _vol > 0 and _amount > 0:
                _vwap = round(_amount / _vol, 2)
            else:
                _vwap = np.nan
            _spread = (dfc['ask1'] - dfc['bid1']).mean()
            _std = dfc['last'].std()
            _summary = pd.Series([_open, _high, _low, _close, _vwap, _vol, _amount, _spread, _std],
                                 ['open', 'high', 'low', 'close', 'vwap', 'vol', 'amount', 'spread', 'std'])
            out[int(initTime)] = _summary
            if len(df) < 1:
                break
        out = out.transpose()
        self.convert_to_time(out)
        return out
        

if __name__ == '__main__':
    
    df = tickDataProcessing('600159')
    out = df.get_stats()
    print(out.head())
    df.sampling()
    timeInterval = [dt.time(14, 30), dt.time(14, 45)]
    out = df.bidBook(timeInterval)
    print(out)


        
