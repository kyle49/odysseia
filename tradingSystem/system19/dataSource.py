# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 11:20:59 2019

@author: Kyle
"""


import numpy as np
import pandas as pd
import tushare as ts
import datetime as dt
import logging
#import os

class Universe:
    
    '''
    Stock pool manager
    Records overall performance of the pool.
    No necessary for now
    '''
    
    def __init__(self, stockList, date = dt.date.today()):
        
        self.stockList = stockList
        self.date = date
        self.dummy = {date: 1}


class DataSource:

    '''
    Data source for the backtester. 
    Must implement a "get_data" function which streams data from the data source.
    '''

    def __init__(self, source='tushare', tickers=['601155.SH'], start = dt.date(2018,1,1), end=dt.date.today()):

        self._logger = logging.getLogger(__name__)
        self._minValidLens = 50
        self.set_source(source = source, tickers = tickers, start = start, end = end)
        


    @classmethod
    def process(cls, queue, source = None):

        # takes queue from controller, add data to the queue
        source = cls() if source is None else source
        while True:
            data = source.get_data()
            if data is not None:
                queue.put(data)
                if data == 'POISON': 
                    # POISON is set to kill process
                    break
    

    def set_source(self, source, tickers, start, end):

        prices = pd.DataFrame()
        counter = 0.
        validTickers = []
        if source == 'tushare':
            '''
            tushare pro's input format:
                code: '000001.SZ'
                date: '20180101'
                
            tushare pro's output format:
                ts_code trade_date OHLC
            '''
            pro = ts.pro_api() # need register with tushare
            _start = start.strftime('%Y%m%d')
            _end = end.strftime('%Y%m%d')
            for ticker in tickers:
                try:
                    self._logger.info('Loading ticker %s' % (counter / len(tickers)))
                    '''
                    dataframe operations
                    '''
                    nFeatures = 2
                    df = pro.daily(ts_code = ticker, start_date = _start, end_date = _end)[['trade_date','close']]
                    df['ma5'] = df['close'].rolling(window = 5).mean()
                    if len(df) < self._minValidLens:
                        continue
                    '''
                    merge
                    '''
                    if len(validTickers) == 0 or len(prices) == 0:
                        prices = df.copy()
                    else:
                        prices = prices.merge(df, on = 'trade_date', suffixes = ('', '_' + ticker))
                        # Note: the default merge type is inner
                    validTickers.append(ticker)
                    
                except Exception as e:
                    self._logger.error(e)
                    pass
                counter += 1
            '''
            perform portfolio level operations here
            '''
            events = []
            for i in range(len(prices)):
                timestamp = dt.datetime.strptime(prices['trade_date'][i], "%Y%m%d")
                for k in range(len(validTickers)):
                    if np.isfinite(sum(prices.iloc[i, (nFeatures * k + 1):(nFeatures * (k + 1) + 1)])):
                        events.append((timestamp, validTickers[k], prices.iloc[i, k]))

        self._source = events
        self._logger.info('Loaded data!')


    @staticmethod
    def convert_to_str(x):
        if x < 10:
            return ("0" + str(x))
        else:
            return str(x)


    @staticmethod
    def convert_to_time(times):
	    return dt.time( int(times//1e7), int(times%1e7//1e5), int(times%1e5//1e3))


    def get_data(self):

        try:
            return self._source.pop(0)
        except IndexError as e:
            return 'POISON'
        
if __name__ == '__main__':
    
    ds = DataSource()
    print(ds._source)