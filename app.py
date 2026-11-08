"""Run: python -m streamlit run app.py"""
import json
import os
import hashlib
from bankwise.uploads import create_dataset
import pandas as pd
import streamlit as st
from bankwise.agent import analyze, OpenAIPlanner, WARNINGS
from bankwise.catalog import CATALOG
from bankwise.data import DB, ROOT, prepare
from bankwise.sql import execute, schema, QueryError
from bankwise.insights import uncertainty, uncertainty_rows
from bankwise.charts import grouped_conversion_chart
from bankwise.access import authorize_server_key, reserve_question
from bankwise.i18n import tr, question_text
language = st.sidebar.selectbox('Language / 语言', ['zh', 'en'], format_func=lambda value: 'English' if value == 'en' else '中文', key='language')

def t(text):
    return tr(text, language)
st.set_page_config(page_title=t('Bankwise · 银行营销分析'), page_icon='◈', layout='wide')
st.markdown('<style>\n.stApp {background:#f5f7fa} .block-container {max-width:1200px;padding-top:2.6rem}\nh1,h2,h3 {color:#152b47} [data-testid="stMetric"] {background:white;border:1px solid #dce5ee;border-radius:12px;padding:18px}\n[data-testid="stSidebar"] {background:#eaf0f6} .stButton>button[kind="primary"] {background:#176b69;border:0}\n</style>', unsafe_allow_html=True)

@st.cache_resource
def initialize_data():
    if not DB.exists():
        prepare()

def setting(name, default=''):
    try:
        return str(st.secrets.get(name, os.getenv(name, default)))
    except FileNotFoundError:
        return os.getenv(name, default)
dataset_source = st.sidebar.radio('数据来源 / Dataset', ['UCI 银行营销演示 / Demo', '自定义银行数据 / Custom'], key='dataset_source')
custom = dataset_source == '自定义银行数据 / Custom'
if not custom:
    try:
        initialize_data()
    except Exception:
        st.error(t('数据初始化失败，请检查部署日志或运行 python -m bankwise.data。'))
        st.stop()
db = DB
dataset_notes = None
if custom:
    with st.sidebar:
        entry = st.radio('导入方式 / Import', ['上传 CSV / Upload', '粘贴 CSV / Paste'])
        if entry == '上传 CSV / Upload':
            uploaded = st.file_uploader('银行数据 CSV（UTF-8，最多 10 MB）', type=['csv'])
            payload = uploaded.getvalue() if uploaded is not None else b''
        else:
            pasted = st.text_area('粘贴含表头的 CSV / CSV with headers', max_chars=10_000_000, key='pasted_csv')
            payload = pasted.encode('utf-8')
        dataset_notes = st.text_area('数据说明 / Dataset notes',
            placeholder='例如：每行是一笔交易；amount 单位为人民币；空值表示未知。请说明字段含义和指标口径。', max_chars=4000)
        st.caption('请仅导入有权使用的数据。问题、字段名及数据说明会发给模型；不会发送原始数据行。')
    if not payload:
        st.info('请上传或粘贴银行相关 CSV 数据。 / Upload or paste banking CSV data.')
        st.stop()
    digest = hashlib.sha256(payload).hexdigest()
    if st.session_state.get('upload_digest') != digest:
        try:
            dataset = create_dataset(payload)
        except ValueError as exc:
            st.error(str(exc))
            st.stop()
        old = st.session_state.get('custom_dataset')
        st.session_state['custom_dataset'] = dataset
        st.session_state['upload_digest'] = digest
        if old:
            old['owner'].cleanup()
    dataset = st.session_state['custom_dataset']
    db = dataset['db']
context = (str(db), dataset_notes, language)
if st.session_state.get('dataset_context') != context:
    for state_key in ('analysis', 'sql_result', 'sql_error', 'sql_input'):
        st.session_state.pop(state_key, None)
    st.session_state['dataset_context'] = context
server_key = setting('OPENAI_API_KEY')
access_code = ''
with st.sidebar:
    st.title('◈ Bankwise')
    st.caption('FINTECH ANALYTICS LAB')
    mode = st.radio(t('分析模式'), [t('模型自由提问')] if custom else [t('预设问题演示'), t('模型自由提问')])
    key = model = None
    if mode == t('模型自由提问'):
        if server_key:
            access_code = st.text_input(t('模型访问口令'), type='password', help=t('由项目所有者提供。无需输入 API Key。'))
            model = setting('OPENAI_MODEL')
            st.caption(t('已由项目所有者配置模型；公开预设演示始终免费。'))
        else:
            key = st.text_input('OpenAI API Key', type='password', help=t('仅本次会话使用，不写入文件。'))
            model = st.text_input(t('模型 ID'), value=setting('OPENAI_MODEL'), placeholder=t('填写你的账户可用模型'))
        st.caption(t('请求会将你的问题和表结构发给模型服务。最多两次请求；数据结果由本地程序生成摘要。'))
    st.divider()
    if custom:
        st.caption('当前分析使用本次会话导入的银行数据。 / Session banking dataset')
    else:
        st.markdown(t('**数据范围**\n\n葡萄牙银行营销观察数据\n\n2008–2010 · 非实时业务'))
        st.link_button(t('数据来源与许可 ↗'), 'https://archive.ics.uci.edu/dataset/222/bank+marketing')
        st.caption(t('没有收入、成本、客户唯一 ID 或完整日期。'))
st.caption('BANKING / CAMPAIGN INTELLIGENCE')
st.title(t('把业务问题，变成可核对的分析'))
st.write('查询当前银行数据，查看 SQL、结果与分析边界。' if custom else t('查询真实银行营销记录，查看 SQL、结果与分析边界。'))
if custom:
    overall = None
    c1, c2 = st.columns(2)
    c1.metric('数据行数 / Rows', f"{dataset['rows']:,}")
    c2.metric('字段数 / Columns', dataset['columns'])
else:
    overall = execute(CATALOG['overall']['sql'])['rows'][0]
    c1, c2, c3 = st.columns(3)
    c1.metric(t('营销观察记录'), f'{overall[0]:,}')
    c2.metric(t('定期存款订阅记录'), f'{overall[1]:,}')
    c3.metric(t('观察记录转化率'), f'{overall[2]:.2f}%')
    st.caption(t('统计口径：订阅记录数 ÷ 全部观察记录数；不是独立客户转化率。'))
analysis_tab, data_tab = st.tabs([t('业务分析'), t('数据与口径')])

def display(result, prefix):
    st.caption(t('模型查询') if result['mode'] == 'live' else t('预设 SQL 演示 · 未调用模型'))
    if result['status'] != 'ok':
        (st.error if result['status'] == 'error' else st.info)(result['explanation'])
    else:
        st.subheader(t('分析结果'))
        st.write(result['summary'])
        st.caption(result['explanation'])
        table = result['table']
        frame = pd.DataFrame(table['rows'], columns=table['columns'])
        interval_rows = [] if custom else uncertainty_rows(table)
        chart = None if custom else grouped_conversion_chart(
            table, language=language, overall_rate=overall[2], interval_rows=interval_rows
        )
        if chart is not None:
            st.altair_chart(chart, width='stretch')
        st.dataframe(frame, hide_index=True, width='stretch')
        intervals = [] if custom else uncertainty(table, language=language, rows=interval_rows)
        if intervals:
            with st.expander(t('样本量与转化率区间')):
                st.dataframe(pd.DataFrame(intervals), hide_index=True, width='stretch')
                st.caption(t('95% Wilson 描述性区间，假设观察相互独立；无法识别同一客户重复出现，未调整混杂因素或多重比较。不是因果置信区间。'))
        if table['truncated']:
            st.warning(t('结果超过 200 行，仅展示前 200 行；摘要也仅针对已返回行。'))
        with st.expander(t('查看执行 SQL'), expanded=False):
            st.code(result['sql'], language='sql')
        st.download_button(t('下载结果 CSV'), frame.to_csv(index=False).encode('utf-8-sig'), 'bankwise-result.csv', 'text/csv', key=prefix + 'csv')
        with st.expander(t('解读边界')):
            for warning in result['warnings']:
                st.write('• ' + warning)
    with st.expander(t('执行轨迹与耗时')):
        st.json(result['trace'])
        st.caption(f"{t('总耗时')} {result['elapsed_ms']} ms")
        if 'usage' in result:
            st.json(result['usage'])
    st.download_button(t('下载本次分析 JSON'), json.dumps(result, ensure_ascii=False, indent=2), 'bankwise-analysis.json', 'application/json', key=prefix + 'json')
with analysis_tab:
    st.subheader(t('从一个明确的问题开始'))
    if mode == t('预设问题演示'):
        selected = st.selectbox(t('选择业务问题'), list(CATALOG), format_func=lambda key: question_text(key, language))
        if st.button(t('运行分析'), type='primary'):
            st.session_state['analysis'] = analyze(question_text(selected, language), demo_id=selected, language=language)
    else:
        question = st.text_area(t('你的问题'), placeholder=t('例如：按渠道比较转化率，并显示每组样本量。'), max_chars=2000)
        if st.button(t('提交给模型'), type='primary'):
            try:
                if not question.strip():
                    raise ValueError(t('请先输入问题。'))
                if server_key:
                    authorize_server_key(setting('BANKWISE_ACCESS_CODE'), access_code)
                    if not model:
                        raise ValueError(t('项目所有者尚未配置模型 ID。'))
                    reserve_question(limit=int(setting('BANKWISE_DAILY_QUESTIONS', '30')))
                    key = server_key
                elif not key:
                    raise ValueError(t('请填写自己的 API Key。'))
                planner = OpenAIPlanner(key=key, model=model, language=language, dataset_notes=dataset_notes)
                with st.spinner(t('读取结构、生成并校验 SQL…')):
                    st.session_state['analysis'] = analyze(question, planner=planner, language=language, db=db, custom=custom)
            except ValueError as exc:
                st.error(t(str(exc)))
    expected_mode = 'demo' if mode == t('预设问题演示') else 'live'
    if 'analysis' in st.session_state and st.session_state['analysis']['mode'] == expected_mode and st.session_state['analysis'].get('language', 'zh') == language:
        st.caption(t('本次问题：') + st.session_state['analysis']['question'])
        display(st.session_state['analysis'], 'analysis')
with data_tab, st.expander(t('SQL 工作台')):
    st.caption(t('单条只读 SELECT · 最多返回 200 行 · 限制执行资源'))
    sql = st.text_area('SQL', 'SELECT * FROM bank_contacts LIMIT 20' if custom else CATALOG['channel']['sql'], height=170, key='sql_input')
    if st.button(t('执行 SQL')):
        try:
            table = execute(sql, db=db)
            st.session_state['sql_result'] = table
            st.session_state.pop('sql_error', None)
        except QueryError as exc:
            st.session_state['sql_error'] = str(exc)
            st.session_state.pop('sql_result', None)
    if 'sql_error' in st.session_state:
        st.error(st.session_state['sql_error'])
    if 'sql_result' in st.session_state:
        table = st.session_state['sql_result']
        st.dataframe(pd.DataFrame(table['rows'], columns=table['columns']), hide_index=True)
        if table['truncated']:
            st.warning(t('结果已截断至 200 行。'))
with data_tab:
    st.subheader(t('数据与口径'))
    if custom:
        st.write('请核对字段类型和数据说明；不会自动假定客户、金额或转化率的含义。')
        st.dataframe(dataset['preview'], hide_index=True)
        st.write(dataset_notes or '尚未填写数据说明；含义不明确的问题需要进一步澄清。')
        st.caption('SQL 查询中的内部表名为 bank_contacts，字段名保留原样。空单元格作为 NULL；日期保留原文，带前导零的编号保留为文本。')
    else:
        st.write(t('一行是源数据中的一条营销观察记录。系统生成 observation_id 方便定位，不代表真实客户编号。'))
        st.markdown((ROOT / 'docs' / ('DATA_CARD_EN.md' if language == 'en' else 'DATA_CARD.md')).read_text(encoding='utf-8'))
        manifest = ROOT / 'data' / 'manifest.json'
        if manifest.exists():
            with st.expander(t('数据来源和 SHA-256')):
                st.json(json.loads(manifest.read_text(encoding='utf-8')))
    with st.expander(t('数据库字段')):
        st.dataframe(pd.DataFrame(schema(db)), hide_index=True)
st.divider()
repository = 'https://github.com/juju123-web/bankwise-analyst'
guide_name = 'STUDY_GUIDE_EN.md' if language == 'en' else 'STUDY_GUIDE.md'
guide_label = 'Study guide' if language == 'en' else '学习指南'
source_label = 'Source code' if language == 'en' else '项目源码'
st.caption(f'[{source_label}]({repository}) · [{guide_label}]({repository}/blob/main/docs/{guide_name})')
