"""Descriptive binomial uncertainty; does not adjust for confounding/repeated people."""
from math import sqrt

def wilson(successes, total, z=1.96):
    if total<=0 or not 0<=successes<=total:
        raise ValueError('Require 0 <= successes <= total and total > 0')
    p = successes/total
    denominator = 1+z*z/total
    center = (p+z*z/(2*total))/denominator
    half = z*sqrt(p*(1-p)/total+z*z/(4*total*total))/denominator
    return max(0.0,100*(center-half)), min(100.0,100*(center+half))

def uncertainty_rows(table):
    """Return one language-neutral Wilson result shared by tables and charts."""
    cols = table['columns']
    if 'observations' not in cols or 'subscriptions' not in cols:
        return []
    output = []
    for row in table['rows']:
        n, k = row[cols.index('observations')], row[cols.index('subscriptions')]
        if not isinstance(n,int) or not isinstance(k,int) or n<=0 or not 0<=k<=n:
            continue
        low,high = wilson(k,n)
        label = ' / '.join(str(row[i]) for i,col in enumerate(cols) if col not in {'observations','subscriptions','conversion_pct','position'}) or 'overall'
        output.append({'group':label, 'observations':n, 'subscriptions':k,
                       'ci_low':round(low,2), 'ci_high':round(high,2),
                       'sample_note':'小样本，谨慎解读' if n<100 else '≥100'})
    return output

def uncertainty(table, language='zh', rows=None):
    rows = uncertainty_rows(table) if rows is None else rows
    output = [{'分组':row['group'], '观察记录数':row['observations'],
               '转化率下界 (%)':row['ci_low'], '转化率上界 (%)':row['ci_high'],
               '样本提示':row['sample_note']} for row in rows]
    if language == 'en':
        from .i18n import tr
        return [{tr(k, language): tr(v, language) if isinstance(v, str) else v for k,v in row.items()} for row in output]
    return output
