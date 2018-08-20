# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 13:18:06 2018

@author: Kyle
"""

import numpy as np
import pandas as pd
import datetime as dt

class tsFeatures:
    
    def __init__(self, df, varName, dateName):
        
        self._rawDF = df
        self._varName = varName
        self._dateName = dateName
        self._geneCalendar()
        self.outDF = self._rawDF.copy()
        
    def _geneCalendar(self, beginDate="2016-07-01", endDate="2016-12-31"):
        beginDate = dt.datetime.strptime(beginDate, "%Y-%m-%d")
        endDate = dt.datetime.strptime(endDate, "%Y-%m-%d")
        beginWeekday = 5
        dates = []
        t = beginDate
        while t <= endDate:
            dates.append(t.date())
            t = t + dt.timedelta(days = 1)
        self._calendar = dates
        self._rawDF = self._rawDF[self._rawDF[self._dateName].isin(dates)]
        w = (np.arange(len(dates)) + beginWeekday) %7
        self._weekdays = pd.Series(w, index=dates)
        
    def set_var(self, varName):
        self._varName = varName
                                    
    def set_timeRange(self, beginDate, endDate):
        self._geneCalendar(beginDate, endDate)

                                       
    def calendarFeatures(self):
        df = np.zeros((len(self.outDF), 16))
        a = self.outDF[self._dateName]
        for i in range(len(a)):
            d = a.iloc[i]
            j = self._weekdays[d]
            df[i, j] = 1 # Col.1-7 for week
            df[i, d.month] = 1 # Col.8-13 for months
            if d.day <= 5:
                df[i, 13] = 1
            elif (d.day >= 13 and d.day <= 17):
                df[i, 14] = 1
            elif d.day >= 26:
                df[i, 15] = 1
            # Col.14-16 for early-mid-late in the months
        s = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat", \
             "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "early", "mid", "late"]
        df = pd.DataFrame(df, columns=s, index=self.outDF.index)
        self.outDF = pd.concat([self.outDF, df], axis=1)
        print("calendar features added, current dimensions:", self.outDF.shape)
        
        
    def summerize(self, countName=None):
        df = self._rawDF[[self._varName, self._dateName]].copy()
        if countName is None:
            df['count'] = 1
        else:
            df['count'] = self._rawDF[countName]
        df = df.groupby([self._varName, self._dateName]).sum()
        out = df.unstack(level=1)
        out = out['count'].fillna(0)
        self.sumDF = out
        
    
    def _expanding(self, df, colName):
        # append self.sumDF like dataframe to self.outDF
        while colName in self.outDF.columns:
            colName = colName + 'a'
        self.outDF[colName] = 0.0
        a = self.outDF
        indxs = df.index.tolist()
        dates = df.columns.tolist()
        for i in dates:
            print("processing %d th day" %i)
            for j in indxs:
                a.loc[(a[self._varName]==j)&(a[self._dateName]==i), colName] = df.loc[j, i]
        print(colName+" added, current dimensions:", self.outDF.shape)
        
        
    def statFeatures(self, maxWindow = 60, addInfo = None):
        # only use backward information 
        # the first two days will be 0 due to insufficient stats to compute skewness
        # addInfo can be setted to distinguish results of different time-windows
        stats = ["mean", "std", "med", "skew"]
        if addInfo is not None:
            for i in range(len(stats)):
                stats[i] = stats[i] + addInfo
        for i in stats:
            self.outDF[i] = 0.0
        a = self.outDF
        indxs = self.sumDF.index.tolist()
        dates = self.sumDF.columns.tolist()
        for i in np.arange(3, len(dates)):
            print("processing %d th day" %i)
            df = self.sumDF.iloc[:, max(0, i-maxWindow):i]
            b = pd.DataFrame([df.mean(axis=1), df.std(axis=1), df.median(axis=1), df.skew(axis=1)])
            for j in indxs:
                a.loc[(a[self._varName]==j)&(a[self._dateName]==dates[i]), stats] =  b.loc[:,j].values
        print("stats added, current dimensions:", self.outDF.shape)
        
        
    def pct(self, expand = False):
        out = self.sumDF.divide(self.sumDF.sum())
        if expand:
            self._expanding(out, "pct")
            print("stats added, current dimensions:", self.outDF.shape)
        return out
    
    def relativeStrength(self, expand = False):
        # WARNING: USE FORWARD INFOMATION
        out = self.sumDF / self.sumDF.mean()
        if expand:
            self._expanding(out, "RS")
            print("stats added, current dimensions:", self.outDF.shape)
        return out
    
    
if __name__ == "__main__":
    
    path = "data6/"
    with open(path + "入库信息.csv", mode='rb') as f:
        reader_rk = pd.read_csv(f, sep = ',', encoding='utf-8', error_bad_lines=False)
        
    reader_rk['交付日期'] = pd.to_datetime(reader_rk['交付时间'], format='%Y/%m/%d %H:%M').dt.date
    res = tsFeatures(reader_rk, varName='仓库地址经度', dateName='交付日期')
    print(res.outDF.shape)
    res.summerize()
    print(res.sumDF.shape)
    res.pct(expand = True)
    res.calendarFeatures()
    res.statFeatures()
    res.sumDF = res.relativeStrength()
    res.statFeatures(addInfo="Rs")
    print(res.outDF.columns)