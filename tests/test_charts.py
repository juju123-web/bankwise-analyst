import pytest

from bankwise.catalog import CATALOG
from bankwise.charts import grouped_conversion_chart, grouped_conversion_data
from bankwise.insights import uncertainty_rows
from bankwise.sql import execute


@pytest.mark.parametrize('key', ['channel', 'job', 'education', 'month', 'age'])
def test_grouped_demo_chart_matches_table_and_shared_intervals(key):
    table = execute(CATALOG[key]['sql'])
    data = grouped_conversion_data(table)
    assert data is not None
    assert data['conversion_pct'].tolist() == sorted(
        data['conversion_pct'].tolist(), reverse=True
    )
    first = data.iloc[0]
    shared = {row['group']: row for row in uncertainty_rows(table)}[first['group']]
    assert first['ci_low'] == shared['ci_low']
    assert first['ci_high'] == shared['ci_high']


def test_single_value_result_does_not_render_chart():
    table = execute(CATALOG['overall']['sql'])
    assert grouped_conversion_data(table) is None
    assert grouped_conversion_chart(table) is None


def test_chart_has_bilingual_labels_and_reference_line():
    table = execute(CATALOG['channel']['sql'])
    zh = grouped_conversion_chart(table, language='zh', overall_rate=11.2654).to_dict()
    en = grouped_conversion_chart(table, language='en', overall_rate=11.2654).to_dict()
    assert zh['title'] == '分组转化率与 95% Wilson 区间'
    assert en['title'] == 'Conversion rate by group with 95% Wilson intervals'
    assert len(en['layer']) == 4
    assert en['layer'][2]['mark']['strokeDash'] == [6, 4]
    assert en['layer'][3]['mark']['type'] == 'text'
    assert en['layer'][0]['encoding']['x']['scale']['domain'][0] == 0
    assert en['layer'][0]['encoding']['x']['scale']['domain'][1] > max(
        row['ci_high'] for row in uncertainty_rows(table)
    )
    assert en['layer'][0]['encoding']['y']['sort']['order'] == 'descending'
    tooltip_fields = {
        item['field'] for item in en['layer'][0]['encoding']['tooltip']
    }
    assert {'observations', 'subscriptions'}.issubset(tooltip_fields)
    reference_sets = [
        rows for rows in en['datasets'].values()
        if rows and 'reference_label' in rows[0]
    ]
    assert reference_sets[0][0]['reference_label'] == 'Overall 11.27%'
    assert en['datasets'] != {}
