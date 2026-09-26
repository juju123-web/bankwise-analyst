# 独立练习提示与核对

先尝试 Study Guide 第 6 节，再看这里。

## 提示

SQL 分组用 `CASE WHEN pdays=999 THEN 'not_previously_contacted' ELSE 'previously_contacted' END`。注意不是 `previous=0`：练习指定的是 pdays 的口径，不应擅自替换。

Python 参考值读取原始 CSV，其中 pdays 是字符串，应先 `int()`。用两个列表或 defaultdict 累积记录，再计算数量和 y=yes 数量。不要从 SQL 结果复制预期数字。

## 一种 SQL 答案

```sql
SELECT CASE WHEN pdays=999 THEN 'not_previously_contacted'
            ELSE 'previously_contacted' END AS prior_contact,
       COUNT(*) AS observations,
       SUM(subscribed) AS subscriptions,
       ROUND(100.0 * AVG(subscribed), 4) AS conversion_pct
FROM bank_contacts
GROUP BY prior_contact
ORDER BY conversion_pct DESC;
```

添加 catalog 项后，界面会自动更新。但 evaluate.py 的 oracle 也必须新增同名结果；如果只加菜单不加 oracle，评测应失败提醒你补验证。

## 自查

两个分组数量之和为 41,188；订阅数之和为 4,640。分组转化率的简单平均通常不等于整体转化率，应按样本量加权。联系历史与转化的关系可能来自先前兴趣、客群选择等混杂，不能直接认定因果。
