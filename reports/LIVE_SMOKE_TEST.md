# 线上真实 API 冒烟测试

2026-09-26，通过 https://bankwise-juju123.streamlit.app/ 的模型自由提问入口执行。密钥保留在托管平台，未读取或导出。此前返回 insufficient_quota；用户补充 API 余额后调用成功。

## 1. 渠道统计：通过

请求按 contact 输出 observations、subscriptions、conversion_pct，百分比四位小数并降序。

模型 SQL：

```sql
SELECT contact, COUNT(*) AS observations, SUM(subscribed) AS subscriptions,
ROUND(100.0 * AVG(subscribed), 4) AS conversion_pct
FROM bank_contacts GROUP BY contact ORDER BY conversion_pct DESC;
```

| contact | observations | subscriptions | conversion_pct |
|---|---:|---:|---:|
| cellular | 26144 | 3853 | 14.7376 |
| telephone | 15044 | 787 | 5.2313 |

数值与独立 CSV 参考答案一致。界面标记为模型查询，成功显示图表和 SQL。模型解释中的“客户订阅比例”措辞不够严谨，应按观察记录口径解读，不能推断独立客户转化率。

## 2. 不支持的收入/ROI：通过

请求计算总收入与 ROI，并明确要求无字段时不要估算。模型回答源数据没有收入或成本字段，无法计算，不进行估算。

## 范围

这是两个明确问题的端到端冒烟测试，不是完整 15 题 live benchmark，也不能据此声称模型准确率为 100%。
