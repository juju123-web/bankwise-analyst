**来源**：[UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing)，采用 `bank-additional-full.csv`，41,188 行；作者 S. Moro、P. Rita、P. Cortez；数据许可 CC BY 4.0。下载脚本保留来源、行数及 SHA-256 校验值。

**粒度与指标**：一行是一次源观察记录；`subscribed=1` 表示 `y=yes`。转化率为订阅记录数 / 所有筛选后观察记录数。人工行号 `observation_id` 不能用来计算独立客户数。

| 字段 | 含义与处理 |
|---|---|
| age / job / marital / education | 年龄、职业、婚姻、教育类别；unknown 保留为独立类别 |
| default / housing / loan | 信用违约、住房贷款、个人贷款状态；不是授信决策模型 |
| contact | cellular / telephone 联系渠道 |
| month / day_of_week | 最后联系的月份、星期；没有逐行年份或具体日期 |
| duration | 最后通话时长（秒），通话之后才可知，存在预测泄漏风险 |
| campaign | 本次营销中对该客户的联系次数（含最后一次） |
| pdays | 距上次营销联系的天数；999 表示此前未联系，不能当真实 999 天求均值 |
| previous / poutcome | 之前活动联系次数及结果 |
| emp_var_rate / cons_price_idx / cons_conf_idx / euribor3m / nr_employed | 源数据宏观指标；点号被转换为下划线 |
| y / subscribed | 原始 yes/no 标签及其 0/1 派生值 |

**不能回答**：收入、ROI、利润、独立客户留存、逐年逐月环比，以及因果问题。按 month 分组是跨年合并的季节分组，不是时间序列。此数据是历史银行营销样本，不代表当前中国 FinTech 客群。

**清洗选择**：保留全部原始记录，不把可能重复的特征组合当重复客户删除；无稳定 ID，无法判断。将数值字段显式转换类型，保留 unknown，验证记录总数与正例数（4,640）。ETL 不添加模拟业务事实。

**业务使用**：用渠道/客群差异形成后续实验假设，不能把观察性差异写成已经实现的业务提升。
