# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 17:22:59 2018

@framework: http://srome.github.io/Build-Your-Own-Event-Based-Backtester-In-Python/
@author: Kyle
"""

import numpy as np


class Algorithm_stalker:


    def __init__(self, ticker):

        self._space = {}
        self._universe = ticker

        self._window = 10
        # length of moving average

        self._trend = np.zeros(self._price_window)
        # moving average of portfolio values
        self._minimum_wait_between_trades = dt.timedelta(minutes = 5)
        # minimum trade interval
        self._last_trade = {}
        # latest trade time
        self._quota = {}
        # quota for each stock in the universe
        self._maximum_amount_per_trade = 0


    def set_quota(self, portfolio_value):

        self._quota = {}
        amt = portfolio_value / len(self._universe)
        self._maximum_amount_per_trade = amt / 5
        for stock in self._universe:
            self._quota[stock] = amt
    
    
    def update(self, stock, price, vol):

        if stock in self._space:
            self.add_info(stock, price, vol)
        else:
            l = self._window
            self._space[stock] = {'plist': np.zeros(l), 'vlist': np.zeros(l), 'index': 0}
            self._space[stock]['plist'][0] = price
            self._space[stock]['vlist'][0] = vol


    def add_info(self, stock, price, vol):

        plist = self._space[stock]['plist']
        vlist = self._space[stock]['vlist']
        ind = self._space[stock]['index']
        if ind < self._window - 1:
            plist[ind + 1] = price
            vlist[ind + 1] = vol
        else:
            plist[:-1] = plist[1:]
            plist[-1] = price
            vlist[:-1] = vlist[1:]
            vlist[-1] = vol
        ind += 1
        if ind >= self._window:
            self._space[stock]['vwap'] = np.sum(plist * vlist) / np.sum(vlist)
        



    def _determine_if_trading(self, stock, price, time, cash_balance, share_available):
        
        if stock not in self._last_date:
            pass
        elif self._last_trade[stock] - time < self._minimum_wait_between_trades:
            return [False, False]

        if self._space[stock]['ind'] < self._window:
            return [False, False]

        buy, sell = False

        buyable = stock in self._universe and cash_balance > 0
        sellable = share_available > 0.01
        
        if price < self._space[stock]['vwap']:
            buy = True
        else:
            sell = True

        return [buy and buyable, sell and sellable]



    def generate_orders(self, stock, time, portfolio):

        orders = []

        cash = portfolio.balance
        shares = portfolio.get_shares(stock)

        l = len(self._universe)
        if l == 0:
            return orders

        action = self._determine_if_trading(stock, price, time, cash, share):
    
        if action[0]:

            amt = min(cash, self._quota[stock], self._maximum_amount_per_trade)
            vol = np.round(amt / self.get_price(stock))
            orders.append((stock, self.get_price, vol))
            self._last_trade[stock] = time

        if action[1]:

            vol = - min(np.round(self._maximum_amount_per_trade / self.get_price(stock)), shares)
            orders.append((stock, self.get_price, vol))
            self._last_trade[stock] = time

        return orders

    def get_price(self, stock):

        # Assumes history is full
        return self._space[stock]['pList'][-1]



if __name__ == '__main__':

    from domain import Portfolio as portfolio

    a = Algorithm()
    p = portfolio()
    history = np.ones(10)
    a.add_trend_value(p.get_total_value())
    
    ticker = "601155"

