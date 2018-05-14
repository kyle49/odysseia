# -*- coding: utf-8 -*-
"""
Created on Wed Apr 25 17:22:59 2018

@framework: http://srome.github.io/Build-Your-Own-Event-Based-Backtester-In-Python/
@author: Kyle
"""

import numpy as np
import datetime as dt


class Algorithm_stalker:


    def __init__(self):

        self._space = {}

        self._window = 10
        # length of moving average

        self._trend = np.zeros(self._window)
        # moving average of portfolio values
        self._minimum_wait_between_trades = dt.timedelta(minutes = 5)
        # minimum trade interval
        self._last_trade = {}
        # latest trade time
        self._maximum_amount_per_trade = 10000

    
    def update(self, stock, price, vol):

        if stock in self._space:
            self.add_info(stock, price, vol)
        else:
            l = self._window
            self._space[stock] = {'plist': np.zeros(l), 'vlist': np.zeros(l), 'index': 0, 'vwap': 0.}
            self._space[stock]['plist'][0] = price
            self._space[stock]['vlist'][0] = vol
        #print(self._space[stock])

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
        self._space[stock]['index'] = ind + 1
        if ind >= self._window:
            self._space[stock]['vwap'] = np.sum(plist * vlist) / np.sum(vlist)


    def _determine_if_trading(self, stock, price, time, cash_balance, quota, share_available):
        
        if stock not in self._last_trade:
            pass
        elif self._last_trade[stock] - time < self._minimum_wait_between_trades:
            return [False, False]

        if self._space[stock]['index'] < self._window:
            return [False, False]

        print("condition valid")
        buy = False; sell = False

        buyable = (quota > 0 and cash_balance > 0)
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
        price = portfolio.get_price(stock)
        quota = portfolio.get_quota(stock)

        action = self._determine_if_trading(stock, price, time, cash, quota, shares)

        if action[0]:

            print("Buy!") ###################
            amt = min(cash, quota, self._maximum_amount_per_trade)
            vol = np.round(amt / price)
            orders.append((stock, price, vol))
            self._last_trade[stock] = time

        if action[1]:

            print("Sell!") ##################
            vol = - min(np.round(self._maximum_amount_per_trade / self.get_price(stock)), shares)
            orders.append((stock, self.get_price, vol))
            self._last_trade[stock] = time

        return orders


    def get_price(self, stock):

        # Assumes history is full
        return self._space[stock]['pList'][-1]




