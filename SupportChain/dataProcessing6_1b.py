
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import datetime as dt
from matplotlib import pyplot as plt
from dataProcessing import tsFeatures


# ### 入库信息预处理

# In[2]:


path = "data6/"
with open(path + "入库信息.csv", mode='rb') as f:
    reader_rk = pd.read_csv(f, sep = ',', encoding='utf-8', error_bad_lines=False)


# In[3]:


print(reader_rk.shape)
print(reader_rk.columns)


# In[4]:


print(reader_rk.iloc[0,:])


# In[8]:


def uniCount(df):
    varList = df.columns
    uniNum = []
    for vari in varList:
        uniNum.append(len(df[vari].unique()))
    uniNum = pd.Series(uniNum, index=varList)
    print("Total samples %d" %(len(df)))
    print(uniNum.sort_values())


# In[7]:


uniCount(reader_rk)


# In[5]:


a = reader_rk["收货数量"].unique()
print(len(a))
a = np.log(a[a > 0])
print(len(a))
plt.hist(a)
plt.show()


# In[9]:


reader_rk = reader_rk[reader_rk["收货数量"] > 0]


# In[10]:


len(reader_rk)


# ### 出库信息预处理

# In[11]:


with open(path + "出库信息.csv", "rb") as f:
    reader_ck = pd.read_csv(f, sep = '\t', encoding='utf-8', error_bad_lines=False, warn_bad_lines=False)


# In[12]:


print(reader_ck.shape)
print(reader_ck.iloc[0,:])


# In[13]:


uniCount(reader_ck)


# In[14]:


a = reader_ck["商品数量"].unique()
a = np.log(a[a > 0])
print(len(a))
plt.hist(a)
plt.show()


# ### 出入库组合

# In[15]:


item_rk = reader_rk["商品名称"].unique()
item_ck = reader_ck["商品名称"].unique()
warehouse_rk = reader_rk["仓库代码"].unique()
warehouse_ck = reader_ck["仓库代码"].unique()


# #### 根据商品分割

# In[16]:


item_shared = [i for i in item_rk if i in item_ck]
print(len(item_shared))


# In[19]:


df_item_ck = reader_ck[reader_ck["商品名称"].isin(item_shared)].copy()
df_item_rk = reader_rk[reader_rk["商品名称"].isin(item_shared)].copy()


# In[20]:


print(df_item_ck.shape)
print(df_item_rk.shape)


# In[22]:


df_item_rk['交付日期'] = pd.to_datetime(df_item_rk['交付时间'], format='%Y/%m/%d %H:%M').dt.date
df_item_ck['出库日期'] = pd.to_datetime(df_item_ck['出库日期'], format='%Y-%m-%d').dt.date


# In[41]:


from dataProcessing import tsFeatures


# In[31]:


cl_rk = tsFeatures(df_item_rk, varName="商品名称", dateName="交付时间")
cl_rk.summerize("收货数量")
ts_item_rk = cl_rk.sumDF


# In[61]:


a = df_item_rk[["商品名称","交付日期"]].copy()
a['count'] = df_item_rk["收货数量"]


# In[62]:


a = a.groupby(["商品名称","交付日期"]).sum()
ts_item_rk = a.unstack(level=1)
ts_item_rk = ts_item_rk['count'].fillna(0)


# In[67]:


print(ts_item_rk.shape)
#print(ts_item_rk.head())


# In[63]:


a = df_item_ck[["商品名称","出库日期"]].copy()
a['count'] = df_item_ck["商品数量"]
a = a.groupby(["商品名称","出库日期"]).sum()
ts_item_ck = a.unstack(level=1)
ts_item_ck = ts_item_ck['count'].fillna(0)


# In[68]:


print(ts_item_ck.shape)
#print(ts_item_ck.head())


# In[69]:


item_rk = ts_item_rk.index.tolist()
item_ck = ts_item_ck.index.tolist()
item_shared = [i for i in item_rk if i in item_ck]
print(len(item_shared))


# In[79]:


ts_item_ck = ts_item_ck[ts_item_ck.index.isin(item_shared)].copy()


# In[80]:


mix = pd.concat([ts_item_ck, ts_item_rk], axis = 0, keys = ['ck', 'rk'], join='outer')
print(mix.shape)


# In[81]:


mix = mix.fillna(0)
ts_item_ck = mix.loc['ck']
print(ts_item_ck.shape)
ts_item_rk = mix.loc['rk']
print(ts_item_rk.shape)


# In[82]:


out1 = ts_item_ck.index.to_frame()
out1.index = np.arange(2782)


# In[83]:


out1.to_csv("itemShared.csv")


# In[58]:


ts_item_ck.index = np.arange(2782)
ts_item_ck.to_csv("TS_ck.csv")


# In[85]:


ts_item_rk.index = np.arange(2782)
ts_item_rk.to_csv("TS_rk.csv")


# In[94]:


ts_item_kc = ts_item_rk.subtract(ts_item_ck.values)
print(ts_item_kc.shape)
ts_item_kc.head()


# In[89]:


def cum_plot(df, maxLines = 10, newtitle = None, legend = False):
    for i in range(maxLines):
        plt.plot(df.iloc[i,:].cumsum(), label = df.index[i])
    if legend:
        plt.legend()
    plt.title(newtitle)
    plt.show()


# In[96]:


cum_plot(ts_item_kc, 30)


# In[98]:


c = ts_item_kc.cumsum(axis = 1)
c.head()


# In[105]:


kc_bot = c.min(axis = 1)
kc_top = c.max(axis = 1)
kc_med = c.median(axis = 1)
kc_init = kc_med * (kc_bot > 0) + 0.5 * (kc_top - kc_bot) * (kc_bot <= 0)


# In[106]:


kc_init.sort_values()


# In[109]:


c.to_csv("TS_kc.csv")
kc_init = np.round(kc_init, decimals=0)
kc_init.to_csv("initStorage.csv")


# #### 根据仓库分割

# 仓库信息不对应，尝试使用位置标注

# In[16]:


def count_freq(x, l=20):
    indxs = x.unique()
    nums = []
    for i in indxs:
        nums.append(x[x == i].count())
    print(pd.Series(nums, index = indxs))


# In[18]:


ltt_rk = reader_rk["仓库地址经度"].unique()
ltt_ck = reader_ck["仓库经度"].unique()
ltt_shared = []
for i in ltt_rk:
    try:
        j = np.float(i)
        if j in ltt_ck:
            ltt_shared.append(j)
    except:
        continue
print(len(ltt_shared))


# In[47]:


df_ck = reader_ck[reader_ck["仓库经度"].isin(ltt_shared)].copy()


# In[57]:


def ltt_formatting(x):
    try:
        x = np.float(x)
    except:
        x = np.nan
    return x
reader_rk["仓库经度"] = reader_rk["仓库地址经度"].apply(ltt_formatting)


# In[74]:


df_rk = reader_rk[reader_rk["仓库经度"].isin(ltt_shared)].copy()
print(df_rk.shape)


# In[75]:


df_rk['交付日期'] = pd.to_datetime(df_rk['交付时间'], format='%Y/%m/%d %H:%M').dt.date


# In[84]:


def dateRange(beginDate, endDate):
    dates = []
    t = dt.datetime.strptime(beginDate, "%Y-%m-%d")
    e = dt.datetime.strptime(endDate, "%Y-%m-%d")
    while t <= e:
        d = t.date()
        dates.append(d)
        t = t + dt.timedelta(days = 1)
    return dates
date_calender = dateRange('2016-07-01', '2016-12-31')
print(len(date_calender))


# In[89]:


df_rk = df_rk[df_rk['交付日期'].isin(date_calender)]
print(df_rk.shape)


# In[90]:


dfc = df_rk[["仓库经度", '交付日期']].copy()
dfc['count'] = 1
dfc = dfc.groupby(["仓库经度", '交付日期']).sum()
dfc.head()
warehouseTS_rk = dfc.unstack(level = 1) # 仓库代码-分配时间
warehouseTS_rk = warehouseTS_rk['count'].fillna(0)
print(warehouseTS_rk.shape)
print(warehouseTS_rk.head())


# In[87]:


def ts_plot(df, maxLines = 10, newtitle = None):
    for i in range(maxLines):
        plt.plot(df.iloc[i,:], label = df.index[i])
    plt.legend()
    plt.title(newtitle)
    plt.show()


# In[93]:


ts_plot(warehouseTS_rk, maxLines=5)


# In[94]:


df_ck['出库日期'] = pd.to_datetime(df_ck['出库日期'], format='%Y-%m-%d').dt.date


# In[95]:


dfc = df_ck[["仓库经度", '出库日期']].copy()
dfc['count'] = 1
dfc = dfc.groupby(["仓库经度", '出库日期']).sum()
dfc.head()
warehouseTS_ck = dfc.unstack(level = 1) # 仓库代码-分配时间
warehouseTS_ck = warehouseTS_ck['count'].fillna(0)
print(warehouseTS_ck.shape)
print(warehouseTS_ck.head())


# In[96]:


ts_plot(warehouseTS_ck)


# In[98]:


warehouseTS_m = [warehouseTS_ck, warehouseTS_rk]
warehouseTS_m = pd.concat(warehouseTS_m, keys=['ck', 'rk'])
print(warehouseTS_m.shape)


# In[100]:


warehouseTS_m.to_csv("TSbyWarehouse.csv")

