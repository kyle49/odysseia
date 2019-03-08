# -*- coding: utf-8 -*-
"""
Created on Fri Mar  8 22:11:37 2019

@author: Kyle
"""

import numpy as np
import datetime as dt

class Algorithm:
    
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