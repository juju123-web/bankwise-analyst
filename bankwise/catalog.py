"""Explicit demo questions, not a pretend language model."""
RATE = 'ROUND(100.0 * AVG(subscribed), 4)'
def grouped(field, order='conversion_pct DESC'):
    return f'SELECT {field}, COUNT(*) AS observations, SUM(subscribed) AS subscriptions, {RATE} AS conversion_pct FROM bank_contacts GROUP BY {field} ORDER BY {order}'

CATALOG = {
    'overall': {'question': '整体转化率是多少？', 'sql': f'SELECT COUNT(*) AS observations, SUM(subscribed) AS subscriptions, {RATE} AS conversion_pct FROM bank_contacts'},
    'channel': {'question': '各联系渠道的转化率有什么差异？', 'sql': grouped('contact')},
    'job': {'question': '哪些职业群体的转化率较高？', 'sql': grouped('job')},
    'education': {'question': '不同教育程度的转化率是多少？', 'sql': grouped('education')},
    'month': {'question': '按月份汇总转化率（跨年合并）', 'sql': grouped('month', "CASE month WHEN 'jan' THEN 1 WHEN 'feb' THEN 2 WHEN 'mar' THEN 3 WHEN 'apr' THEN 4 WHEN 'may' THEN 5 WHEN 'jun' THEN 6 WHEN 'jul' THEN 7 WHEN 'aug' THEN 8 WHEN 'sep' THEN 9 WHEN 'oct' THEN 10 WHEN 'nov' THEN 11 ELSE 12 END")},
    'history': {'question': '上次营销结果与本次转化有什么关系？', 'sql': grouped('poutcome')},
    'loan': {'question': '个人贷款状态与转化率有什么关系？', 'sql': grouped('loan')},
    'frequency': {'question': '联系次数与转化率有什么关系？', 'sql': f"SELECT CASE WHEN campaign=1 THEN '1' WHEN campaign BETWEEN 2 AND 3 THEN '2-3' WHEN campaign BETWEEN 4 AND 5 THEN '4-5' ELSE '6+' END AS contact_bucket, COUNT(*) AS observations, SUM(subscribed) AS subscriptions, {RATE} AS conversion_pct FROM bank_contacts GROUP BY contact_bucket ORDER BY contact_bucket"},
    'age': {'question': '各年龄段的转化率是多少？', 'sql': f"SELECT CASE WHEN age<30 THEN '<30' WHEN age<45 THEN '30-44' WHEN age<60 THEN '45-59' ELSE '60+' END AS age_band, COUNT(*) AS observations, SUM(subscribed) AS subscriptions, {RATE} AS conversion_pct FROM bank_contacts GROUP BY age_band ORDER BY age_band"},
    'rank': {'question': '每个渠道内转化率最高的三个职业是什么？', 'sql': f'WITH segments AS (SELECT contact, job, COUNT(*) AS observations, {RATE} AS conversion_pct FROM bank_contacts GROUP BY contact, job HAVING COUNT(*)>=100), ranked AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY contact ORDER BY conversion_pct DESC, job) AS position FROM segments) SELECT * FROM ranked WHERE position<=3 ORDER BY contact, position'},
    'quality': {'question': '关键字段有多少 unknown？', 'sql': "SELECT SUM(CASE WHEN job='unknown' THEN 1 ELSE 0 END) AS job_unknown, SUM(CASE WHEN education='unknown' THEN 1 ELSE 0 END) AS education_unknown, SUM(CASE WHEN loan='unknown' THEN 1 ELSE 0 END) AS loan_unknown FROM bank_contacts"},
    'revenue': {'question': '收入为什么下降？', 'reason': '数据没有收入、金额或成本字段，不能计算收入或 ROI。'},
    'customers': {'question': '有多少独立客户？', 'reason': '数据没有稳定的客户 ID；observation_id 只是导入行号，不能去重客户。'},
    'causal': {'question': '电话联系导致转化率降低吗？', 'reason': '这是观察数据，不能确定因果。可比较渠道转化，但需考虑客群选择偏差。'},
    'trend': {'question': '2010年3月的环比转化率？', 'reason': '源数据没有逐行年份和完整日期，不能计算可靠的年月环比。'},
}
