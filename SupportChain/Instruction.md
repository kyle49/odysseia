# 函数功能介绍
通过实现对 dataframe 进行折叠与展开来进行时间序列 feature 整理。
启用需要指定一个分类方式，并且明确一个时间变量。函数会根据分类方式求出时间序列，并以时间序列为基础生成统计量保存在 outDF。

## arguments
### df
传入的 dataframe
### varName
指定后将按照该分类进行折叠
可以更改分类依据。
### dateName
指定的时间变量，单位为天。
时间范围设定在 2016-07-01 到 2016-12-31，如果某个 sample 没有对应的时间变量该 sample 将被删除。

## functions
### set_var
用于更改分类，由于没有后续功能更改后需要重新运行 summerize。
### calendarFeatures
引入的是日期相关的特征。每周周一到周日有一个不同的变量，每个月有不同变量。月初（1-5），月中（13-17），月末（26-31）分别有一个变量。
### summerize
将 dataframe 根据 varName 进行折叠。
折叠后的结果保存在 sumDF，并可用于 statsFeatures 计算。
### expanding
将 summerize 的结果展开成原 dataframe 的形式。
注意时间消耗量大。
### statsFeatures
根据 summerize 的结果生产统计量的时间序列并加入原 dataframe。
时间序列的生产遵循 backward only 原则，即生产的统计量仅使用截至对应时间的数据。
目前支持 mean, standard deviance, median 和 skewness 四个统计量。
可以调整窗口来控制统计量的波动，例如如果需要 ma(3) 即为 window=3 时的 mean。
可以设置额外信息给统计量命名。
### pct
计算某分类在某一时刻占总流量的比例。需要先运行 summerize。
设置为直接输出，可以通过 expand = True 加入原 dataframe。
tips: 可以赋值给 sumDF 用于 statsFeatures 输出。
### relativeStrength
计算分类某一时刻相对于其平均值的比例。
注意!!!这个计算使用了未来信息。
其余用法类似 pct
### 其余功能仍在开发中
