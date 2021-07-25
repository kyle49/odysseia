# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 10:37:28 2018

@author: Kyle
"""

import numpy as np
import pandas as pd
import datetime as dt
from sklearn import preprocessing

"""
Dealing with WIND (3s) tick data
The default time index is Hour(1-2 digits)-Min(2 digits)-Sec(2 digits)-MSec(3 digits)

V1.02: combined tickDataFeatures
V1.03: new APIs
V1.04: fixed bugs caused by mid-break. WARNING: it may lead to different time-index 
V1.10: added data streaming class
V1.11: set some Volume-related statistics to their logrithm in tickDataFeatures
"""

def loadData(file, path):
    return tickDataProcessing(file[0:6], path)


class tickDataProcessing:
    
    def __init__(self, stockID, path = '../dataPackages/'):        
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
        
            
    def askBook(self, timeI, avg = False):
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
        if 0 in out.columns:
            out = out.drop(0, axis = 1)
        if avg: 
            return out.mean()
        return out


    def bidBook(self, timeI, avg = False):
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
        if 0 in out.columns:
            out = out.drop(0, axis = 1)
        if avg: 
            return out.mean()[::-1]
        return out
        

    def get_stats(self, timeIntervals = 5):
        df = self._rawDF
        initTime = 93000000
        intervalTime = timeIntervals * 1e5
        out = pd.DataFrame()
        while(initTime < 150000000):
            if initTime >= 113000000 and initTime < 130000000:
                initTime = 130000000
                continue
            dfc = df[df.index <= initTime + intervalTime]
            df = df[df.index > initTime + intervalTime]
            initTime = round(df.index[0], -5)
            if len(dfc) < 1:
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
    
    
    def get_orderVwap(self, timeIntervals = 5, orderRange = 5):
        df = self._rawDF
        initTime = 93000000
        intervalTime = timeIntervals * 1e5
        out = pd.DataFrame()
        while(initTime < 150000000):
            dfc = df[df.index <= initTime + intervalTime].values
            df = df[df.index > initTime + intervalTime]
            initTime = round(df.index[0], -5)
            if len(dfc) < 1:
                continue
            if initTime > 113000000 and initTime < 130000000:
                initTime = 130000000
                continue
            _askVol = dfc[:, 22:(22 + orderRange)]
            _askAmount = dfc[:, 12:(12 + orderRange)] * _askVol
            _askVwap = _askAmount.sum() / _askVol.sum()
            _bidVol = dfc[:, 42:(42 + orderRange)]
            _bidAmount = dfc[:, 32:(32 + orderRange)] * _bidVol
            _bidVwap = _bidAmount.sum() / _bidVol.sum()
            
            _summary = pd.Series([_askVwap, _bidVwap],
                                 ['askVwap' + str(orderRange), 'bidVwap' + str(orderRange)])
            out[int(initTime)] = _summary
            if len(df) < 1:
                break
        out = out.transpose()
        return out



class tickDataFeatures:
    
    def __init__(self, df, priors = {}):
        self.df = df # df: an OHLC talbe, in the form of tickDataProcessing.get_stats
        self.priors = priors # a dictionary of previous information
        self.setParas()
        
    def setParas(self, minLen = 2, maxLen = 8, decayRate = .8, stoch = (14, 3, 5), delay = 2):
        self._minLen = minLen
        self._maxLen = maxLen
        self._decayRate = decayRate
        self._stoch = stoch
        self._delay = delay

    def getRet(self, delay):
        self.ret = self.df['close'].diff(delay)
        if 'close' in self.priors.keys():
            self.ret[delay - 1] = (self.df['close'][0] - self.priors['close']) / self.df['close'][0]
        else:
            self.ret[delay - 1] = (self.df['close'][0] - self.df['open'][0]) / self.df['close'][0]
        _c = np.append(np.ones(delay), self.df['close'][:-delay].values)
        self.ret = self.ret / _c
        self.ret[self.ret > 0.1] = 0.0
        self.ret[self.ret < -0.1] = 0.0
        
    def getDelayedStats(self, delay, arg = 'close'):
        return self.df[arg].rolling(window = delay + 1).sum() - self.df[arg].rolling(window = delay).sum()

    def getTail(self):
        return self.df.iloc[-1].copy()
    
    def RSI(self):
        marginGain = self.ret.copy()
        marginGain[marginGain < 0] = 0
        marginLoss = marginGain - self.ret
        marginGain = marginGain.rolling(window = self._maxLen, min_periods = self._minLen).sum()
        marginLoss = marginLoss.rolling(window = self._maxLen, min_periods = self._minLen).sum()
        out = marginGain / (marginGain + marginLoss)
        return out.replace(np.inf, np.nan).replace(-np.inf, np.nan)
    
    @staticmethod
    def DEMA(x, a):
        ema1 = x.ewm(alpha = a).mean()
        ema2 = ema1.ewm(alpha = a).mean()
        return 2*ema1 - ema2
    
    def TypicalPrice(self):
        self.TP = self.df[['close', 'high', 'low']].mean(axis = 1)
    
    def TrueRange(self):
        df = self.df[['close', 'high', 'low']].copy()
        df.iloc[1:,0] = df.iloc[:-1,0] # shift close
        if 'close' in self.priors.keys():
            df.iloc[0,0] = self.priors['close']
        else:
            df.iloc[0,0] = self.df['open'].iloc[0]
        self.TR = np.max(df, axis = 1) - np.min(df, axis = 1)
    
    def AverageTrueRange(self):
        self.TrueRange()
        self.ATR = self.TR.ewm(alpha = self._decayRate).mean()
    
    def DirectIndex(self):
        df = self.df[['high', 'low']].diff()
        df = df * [1, -1]
        df[df < 0] = 0
        maxCol = np.argmax(df.values, axis=1)
        df['high'] = df['high'] * (1 - maxCol)
        df['low'] = df['low'] * maxCol
        df = df.ewm(alpha = self._decayRate).mean()
        df = df.divide(self.ATR, axis = 0)
        dx = abs(df['high'] - df['low']) / (df['high'] + df['low'])
        return dx.ewm(alpha = self._decayRate).mean()
    
    def STOCH(self):
        df = self.df[['high', 'low', 'close']].copy()
        hl = pd.DataFrame(index = df.index, columns = ['HH', 'LL'])
        _hh = _ll = np.nan
        if 'high' in self.priors.keys():
            _hh = self.priors['high']
        if 'low' in self.priors.keys():
            _ll = self.priors['low']
        for i in range(len(hl)):
            _start = max(0, i - self._stoch[0])
            hh = df.iloc[_start:(i + 1), 0].max()
            ll = df.iloc[_start:(i + 1), 1].min()
            if i < self._stoch[0]:
                hh = max(_hh, hh)
                ll = min(_ll, ll)
            hl.iloc[i,0] = hh
            hl.iloc[i,1] = ll
        fastK = (df['close'] - hl['LL']) / (hl['HH'] - hl['LL'])
        fastD = fastK.rolling(window = self._stoch[1], min_periods = self._minLen).mean()
        fullK = fastK.rolling(window = self._stoch[2], min_periods = self._minLen).mean()
        fullD = fastD.rolling(window = self._stoch[2], min_periods = self._minLen).mean()
        return {'fastK':fastK, 'fastD':fastD, 'fullK':fullK, 'fullD':fullD}
    
    def OnBalanceVolume(self, log = True):
        v = self.df['vol'].copy()
        r = self.ret
        v = v * np.sign(r)
        if log:
            v = v.cumsum()
            return np.log(np.abs(v) + 1) * np.sign(v)
        else:
            return v.cumsum()
    
    def CloseLocationValue(self):
        self.CLV = (2*self.df['close'] - self.df['high'] - self.df['low'])/(self.df['high'] - self.df['low'])
        
    def ChaikinMoneyFlow(self, log = True):
        self.CloseLocationValue()
        v = self.df['vol'].copy()
        MFV = v * self.CLV
        ADL = MFV.cumsum()
        if log:
            ADL = np.log(np.abs(ADL) + 1) * np.sign(ADL)
        MFI = MFV.rolling(window = self._maxLen).sum() / v.rolling(window = self._maxLen).sum()
        return {'ADL':ADL, 'MFI':MFI}
    
    def MoneyFlowIndex(self):
        self.TypicalPrice()
        v = self.df['vol'].copy()
        tp = self.TP.copy()
        dp = tp.diff()
        dp.iloc[0] = 0
        MF = tp * v
        MF[dp == 0] = 0
        tp[dp <= 0] = 0
        posiMF = v * tp
        return posiMF.rolling(window = self._maxLen).sum() / MF.rolling(window = self._maxLen).sum()

    def main(self, style = 0):
        out = {}
        if style == 0:
            self.getRet(1)
            out['RSI'] = self.RSI()
            self.AverageTrueRange()
            out['ATR'] = self.ATR
            out['DX'] = self.DirectIndex()
            stoch_ = self.STOCH()
            for i in stoch_.keys():
                out[i] = stoch_[i]
            chaikin_ = self.ChaikinMoneyFlow()
            out['CLV'] = self.CLV
            out['OBV'] = self.OnBalanceVolume()
            out['ADL'] = chaikin_['ADL']
            out['cMFI'] = chaikin_['MFI']
            out['pMFI'] = self.MoneyFlowIndex()
            out = pd.DataFrame(out)
            _df = self.df.copy()
            _df['vol'] = np.log(_df['vol'] + 1)
            _df['amount'] = np.log(_df['amount'] + 1)
            return _df.join(out)
        elif style == 1:
            out = pd.DataFrame(out)
            out['closeDelay1'] = self.getDelayedStats(1) - self.df['close']
            out['closeDelay2'] = self.getDelayedStats(2) - self.df['close']
            out['closeDelay5'] = self.getDelayedStats(5) - self.df['close']
            out['closeVwap'] = self.df['close'] - self.df['vwap']
            out['openClose'] = self.df['open'] - self.df['close']
            out['highLow'] = self.df['close'] - self.df['low']
            self.TypicalPrice()
            self.AverageTrueRange()
            out['closeTP'] = self.df['close'] - self.TP
            out['ATR'] = self.ATR
            self.getRet(1)
            out['RSI'] = self.RSI()
            out['DX'] = self.DirectIndex()
            out['vol'] = np.log(self.df['vol'] + 1)
            out['amount'] = np.log(self.df['amount'] + 1)
            out['volMA5Ratio'] = np.log(self.df['vol'].rolling(window = 5).mean() + 1) - out['vol']
            out['std'] = self.df['std']
            out['spread'] = self.df['spread']
            return out
        elif style == 2:
            out = pd.DataFrame(out)
            out['closeDelay1'] = self.getDelayedStats(1) - self.df['close']
            out['closeDelay2'] = self.getDelayedStats(2) - self.df['close']
            out['closeDelay5'] = self.getDelayedStats(5) - self.df['close']
            out['closeVwap'] = self.df['close'] - self.df['vwap']
            out['openClose'] = self.df['open'] - self.df['close']
            out['highLow'] = self.df['close'] - self.df['low']
            self.TypicalPrice()
            self.AverageTrueRange()
            out['closeTP'] = self.df['close'] - self.TP
            out['ATR'] = self.ATR
            out = out / float(self.df['open'][0])
            return out
        return pd.DataFrame(out)


import os
   
def geneTrainingData(Path, skip = 0, delay = 2, scale = True):
    X = []
    Y = []
    for root, dirs, files in os.walk(Path):
        for file in files:
            try:
                Df = loadData(file, path = root + os.sep)
                df = tickDataFeatures(Df.get_stats())
            except:
                print('Error in reading', file)
                continue
            _X = df.main()
            _X = _X.iloc[skip:(-delay)]
            if scale:
                _X = preprocessing.scale(_X.fillna(method = 'ffill').fillna(0))
            df.getRet(delay)
            _Y = df.ret[(skip + delay):]
            X.append(_X)
            Y.append(np.array(_Y))
    return(np.array(X, dtype = float), np.array(Y, dtype = float))
            
            
def geneTrainingData_shuffle(Path, skip = 0, delay = 2, scale = True, length = 5, printName = False, minLen = 0, style = 1):
    X = []
    Y = []
    for root, dirs, files in os.walk(Path):
        subuniverse = np.random.choice(files, len(files), replace = False)
    count = 0
    for file in subuniverse:
        try:
            Df = loadData(file, path = root + os.sep)
            df = tickDataFeatures(Df.get_stats())
        except:
            print('Error in reading', file)
            continue
        _X = df.main(style = style)
        _X = _X.iloc[skip:(-delay)]
        if len(_X) < minLen:
            continue
        if scale:
            try:
                _X = preprocessing.scale(_X.fillna(method = 'ffill').fillna(0))
            except:
                continue
        df.getRet(delay)
        _Y = df.ret[(skip + delay):]
        if len(_Y) < minLen:
            continue
        if printName:
            print(file, "X shape: ", _X.shape, " Y shape: ", _Y.shape)
            print(_Y.index)
        X.append(_X)
        Y.append(np.array(_Y))
        count += 1
        if count >= length:
            break
    return(np.array(X, dtype = float), np.array(Y, dtype = float))        
            

class dataStream:
    
    def __init__(self, length = 5, skip = 0, delay = 2, minLen = 0, maxLen = 1000, style = 1):
        self._path = {}
        self.universe = {}
        self._length = length
        self._skip = skip
        self._delay = delay
        self._minLen = minLen
        self._maxLen = maxLen
        self._style = style
        self._scale = True
        self._shuffle = True
        
    def setUniverse(self, _time, universe = []):
        self.universe[_time] = universe
    
    def setPath(self, _time, path):
        self._path[_time] = path
        
    def gene(self, _time):
        X = []
        Y = []
        if _time not in self.universe.keys():
            print(_time, "is not a valid date !")
            return
        if self._shuffle:
            _range = min(len(self.universe[_time]), self._length * 3)
            subuniverse = np.random.choice(self.universe[_time], _range, replace = False)
        else:
            subuniverse = self.universe[_time]
        count = 0
        for stock in subuniverse:
            try:
                Df = loadData(stock, path = self._path[_time])
                df = tickDataFeatures(Df.get_stats())
            except:
                print('Error in reading', stock, 'on', _time)   
                self.universe[_time].remove(stock)
                continue
            _X = df.main(style = self._style)
            _X = _X.iloc[self._skip:(-self._delay)]
            if len(_X) < self._minLen or len(_X) > self._maxLen:
                print('Error in the length of', stock, 'on', _time)
                self.universe[_time].remove(stock)
                continue
            if self._scale:
                try:
                    _X = preprocessing.scale(_X.fillna(method = 'ffill').fillna(0))
                except:
                    print('Error in scaling', stock, 'on', _time)
                    self.universe[_time].remove(stock)
                    continue
            df.getRet(self._delay)
            _Y = df.ret[(self._skip + self._delay):]
            if len(_Y) != len(_X):
                print('Error in the length of', stock, 'on', _time)
                self.universe[_time].remove(stock)
                continue
            X.append(_X)
            Y.append(_Y)
            count += 1
            if count >= self._length:
                break
        return(np.array(X, dtype = float), np.array(Y, dtype = float))            
    

if __name__ == '__main__':
    

    df = tickDataProcessing('000001', path = "dataPackages/rawdata/01/")
    out = df.get_stats()
    print(out.head())
    Df = tickDataFeatures(out)


