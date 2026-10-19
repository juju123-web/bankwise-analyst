"""Altair charts for grouped conversion results."""
from __future__ import annotations

import altair as alt
import pandas as pd

from .i18n import tr
from .insights import uncertainty_rows


METRICS = {'observations', 'subscriptions', 'conversion_pct', 'position'}


def grouped_conversion_data(table, interval_rows=None):
    """Return chart-ready grouped results, or None when a chart is not valid.

    Confidence limits come from the same normalized uncertainty rows used by
    the result-area table, so the two displays cannot drift apart.
    """
    columns = table.get('columns', [])
    rows = table.get('rows', [])
    required = {'observations', 'subscriptions', 'conversion_pct'}
    dimensions = [column for column in columns if column not in METRICS]
    if len(rows) <= 1 or not required.issubset(columns) or not dimensions:
        return None

    interval_rows = uncertainty_rows(table) if interval_rows is None else interval_rows
    interval_by_group = {row['group']: row for row in interval_rows}
    output = []
    for row in rows:
        record = dict(zip(columns, row))
        n = record['observations']
        subscriptions = record['subscriptions']
        rate = record['conversion_pct']
        if not isinstance(n, int) or not isinstance(subscriptions, int):
            return None
        if n <= 0 or not 0 <= subscriptions <= n or not isinstance(rate, (int, float)):
            return None
        group = ' / '.join(str(record[column]) for column in dimensions)
        interval = interval_by_group.get(group)
        if interval is None:
            return None
        output.append({
            'group': group,
            'observations': n,
            'subscriptions': subscriptions,
            'conversion_pct': float(rate),
            'ci_low': interval['ci_low'],
            'ci_high': interval['ci_high'],
        })
    return pd.DataFrame(output).sort_values(
        ['conversion_pct', 'group'], ascending=[False, True], ignore_index=True
    )


def grouped_conversion_chart(table, language='zh', overall_rate=11.27, interval_rows=None):
    """Build a horizontal conversion chart with Wilson intervals."""
    data = grouped_conversion_data(table, interval_rows=interval_rows)
    if data is None:
        return None

    group_title = tr('分组', language)
    rate_title = tr('转化率 (%)', language)
    observations_title = tr('观察记录数', language)
    subscriptions_title = tr('订阅数', language)
    lower_title = tr('95% Wilson 下界 (%)', language)
    upper_title = tr('95% Wilson 上界 (%)', language)
    overall_title = tr('总体转化率 (%)', language)
    overall_label = tr('总体', language)
    order = alt.SortField(field='conversion_pct', order='descending')
    y = alt.Y('group:N', sort=order, title=group_title)
    axis_max = max(float(data['ci_high'].max()), float(overall_rate)) * 1.08
    metric_scale = alt.Scale(domain=[0, axis_max], nice=False)

    tooltip = [
        alt.Tooltip('group:N', title=group_title),
        alt.Tooltip('conversion_pct:Q', title=rate_title, format='.2f'),
        alt.Tooltip('observations:Q', title=observations_title, format=','),
        alt.Tooltip('subscriptions:Q', title=subscriptions_title, format=','),
        alt.Tooltip('ci_low:Q', title=lower_title, format='.2f'),
        alt.Tooltip('ci_high:Q', title=upper_title, format='.2f'),
    ]
    base = alt.Chart(data)
    bars = base.mark_bar(color='#2F6B7C', cornerRadiusEnd=3).encode(
        y=y,
        x=alt.X('conversion_pct:Q', title=rate_title, scale=metric_scale),
        tooltip=tooltip,
    )
    intervals = base.mark_rule(color='#243746', strokeWidth=2).encode(
        y=y,
        x=alt.X('ci_low:Q', scale=metric_scale),
        x2=alt.X2('ci_high:Q'),
        tooltip=tooltip,
    )
    reference_data = pd.DataFrame({
        'overall_rate': [float(overall_rate)],
        'reference_label': [f'{overall_label} {overall_rate:.2f}%'],
    })
    reference = alt.Chart(reference_data).mark_rule(
        color='#E69F00', strokeDash=[6, 4], strokeWidth=2
    ).encode(
        x=alt.X('overall_rate:Q', scale=metric_scale),
        tooltip=[alt.Tooltip('overall_rate:Q', title=overall_title, format='.2f')],
    )
    reference_text = alt.Chart(reference_data).mark_text(
        color='#9A6700', align='left', baseline='top', dx=6, dy=6,
    ).encode(
        x=alt.X('overall_rate:Q', scale=metric_scale),
        y=alt.value(0),
        text=alt.Text('reference_label:N'),
        tooltip=[alt.Tooltip('overall_rate:Q', title=overall_title, format='.2f')],
    )

    return (bars + intervals + reference + reference_text).properties(
        title=tr('分组转化率与 95% Wilson 区间', language),
        height=max(220, 34 * len(data)),
    ).configure_view(stroke=None)
