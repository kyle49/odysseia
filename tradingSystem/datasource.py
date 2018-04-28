# -*- coding: utf-8 -*-
"""
Created on Fri Apr 27 09:42:00 2018

@framework: http://srome.github.io/Build-Your-Own-Event-Based-Backtester-In-Python/
@author: Kyle
"""

import numpy as np
import pandas as pd
from pandas_datareader import DataReader
"""
Need to switch to tushare data
Note: tushare takes str-type date only
Data is in reverse time order
"""
import datetime as dt
import logging

class DataSource:

    '''
    Data source for the backtester. Must implement a "get_data" function
    which streams data from the data source.
    '''

    def __init__(self, source='yahoo', tickers=['GOGL','AAPL'], start = dt.datetime(2016,1,1), end=dt.datetime.today()):

        self._logger = logging.getLogger(__name__)
        self.set_source(source = source, tickers= tickers, start=start, end=end)


    @classmethod
    def process(cls, queue, source = None):

        source = cls() if source is None else source
        while True:
            data = source.get_data()
            if data is not None:
                queue.put(data)
                if data == 'POISON':
                    break
    # POISON is set to kill process


    def set_source(self, source, tickers, start, end):

        prices = pd.DataFrame()
        counter = 0.
        for ticker in tickers:
            try:
                self._logger.info('Loading ticker %s' % (counter / len(tickers)))
                prices[ticker] = DataReader(ticker, source, start, end).loc[:, 'Close']
                
                ## Read stock prices via DataReader
                
            except Exception as e:
                self._logger.error(e)
                pass
            counter+=1

        events = []
        for row in prices.iterrows():
            timestamp=row[0]
            series = row[1]
            vals = series.values
            indx = series.index
            for k in np.random.choice(len(vals),replace=False, size=len(vals)): # Shuffle!
                if np.isfinite(vals[k]):
                    events.append((timestamp, indx[k], vals[k]))

        self._source = events
        self._logger.info('Loaded data!')


    def get_data(self):

        try:
            return self._source.pop(0)
        except IndexError as e:
            return 'POISON'
