# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 16:56:06 2018

@framework: http://srome.github.io/Build-Your-Own-Event-Based-Backtester-In-Python/
@author: Kyle
"""

from multiprocessing import Process, Queue, freeze_support

import numpy as np
import datetime as dt
from algorithm import Algorithm
from domain import Portfolio
from orderAPI import OrderApi
from datasource import DataSource
import logging


class Controller:

    def __init__(self, portfolio = None, algorithm = None):

        self._logger = logging.getLogger(__name__)
        self._portfolio = Portfolio() if portfolio is None else portfolio
        self._algorithm = Algorithm() if algorithm is None else algorithm
        self._order_api = OrderApi()

    @classmethod
    def backtest(cls, queue, controller = None):

        controller = cls() if controller is None else controller
        try:
            while True:
                if not queue.empty():
                    o = queue.get()
                    controller._logger.debug(o)

                    if o == 'POISON':
                        break

                    timestamp = o[0]
                    ticker = o[1]
                    price = o[2]

                    # Update pricing

                    controller.process_pricing(ticker = ticker, price = price)

                    # Generate Orders

                    orders = controller._algorithm.generate_orders(timestamp, controller._portfolio)

                    # Process orders

                    if len(orders) > 0:
                        # Randomize the order execution
                        final_orders = [orders[k] for k in np.random.choice(len(orders), replace=False, size=len(orders))]
                        for order in final_orders:
                            controller.process_order(order)

                        controller._logger.info(controller._portfolio.value_summary(timestamp))

        except Exception as e:
            print(e)

        finally:
            controller._logger.info(controller._portfolio.value_summary(None))


    def process_order(self, order):

        success = False
        receipt = self._order_api.process_order(order)

        if receipt is not None:
            success = self.process_receipt(receipt)

        if order is None or success is False:
            self._logger.info(('{order_type} failed: %s at $%s for %s shares' % order).format(order_type = 'Sell' if order[2] < 0 else 'Buy'))


    def process_receipt(self,receipt):

        ticker = receipt[0]
        price = receipt[1]
        share_delta = receipt[2]
        fee = receipt[3]
        temp = self._portfolio.balance - (price * share_delta + fee)

        if temp > 0:
            if share_delta < 0 and -share_delta > self._portfolio.get_shares(ticker):
                # Liquidate
                share_delta = -self._portfolio.get_shares(ticker)
                fee = self._order_api._calculate_fee(share_delta*price)
                if fee > abs(share_delta*price):
                    return False
            self._portfolio.update_trade(ticker=ticker, price=price, share_delta=share_delta, fee=fee)
            self._logger.debug('Trade on %s for %s shares at %s with fee %s' % (ticker,share_delta,price, fee))
            return True
        return False



    def process_pricing(self, ticker, price):

        self._portfolio.update(price=price, ticker = ticker)
        self._algorithm.update(stock=ticker, price = price)




class Backtester:

    def __init__(self):

        self._logger = logging.getLogger(__name__)
        self._settings = {}
        self._default_settings = {
            'Portfolio' : Portfolio(),
            'Algorithm' : Algorithm(),
            'Source' : 'yahoo',
            'Start_Day' : dt.datetime(2016,1,1),
            'End_Day' : dt.datetime.today(),
            'Tickers' : ['AAPL','GOGL','MSFT','AA','APB']
        }


    def set_portfolio(self, portfolio):

        self._settings['Portfolio'] = portfolio


    def set_algorithm(self, algorithm):

        self._settings['Algorithm'] = algorithm


    def set_source(self, source):

        self._settings['Source'] = source


    def set_start_date(self, date):

        self._settings['Start_Day'] = date


    def set_end_date(self, date):

        self._settings['End_Day'] = date


    def set_stock_universe(self, stocks):

        self._settings['Tickers'] = stocks


    def get_setting(self, setting):

        return self._settings[setting] if setting in self._settings else self._default_settings[setting]



    def backtest(self):

        #Setup Logger

        root = logging.getLogger()
        root.setLevel(level=logging.DEBUG)
        import os
        filepath = 'run.log'
        if os.path.exists(filepath):
            os.remove(filepath)

        root.addHandler(logging.FileHandler(filename=filepath))

        # Initiate run
        
        q = Queue() # From multiprocessing
        ds = None
        c = None

        ds = DataSource(
            source=self.get_setting('Source'),
            start=self.get_setting('Start_Day'),
            end=self.get_setting('End_Day'),
            tickers=self.get_setting('Tickers')
        )

        c = Controller(
            portfolio=self.get_setting('Portfolio'),
            algorithm=self.get_setting('Algorithm')
        )

        
        p = Process(target=DataSource.process, args=((q,ds)))
        p1 = Process(target=Controller.backtest, args=((q,c)))

        p.start()
        p1.start()
        p.join()
        p1.join()
        

if __name__ == '__main__':

    freeze_support()
    
    b = Backtester()

    b.backtest()



