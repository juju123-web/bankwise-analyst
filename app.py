"""Run: python -m streamlit run app.py"""
import json
import os
import pandas as pd
import streamlit as st
from bankwise.agent import analyze, OpenAIPlanner, WARNINGS
from bankwise.catalog import CATALOG
from bankwise.data import DB, ROOT, prepare
from bankwise.sql import execute, schema, QueryError
from bankwise.insights import uncertainty
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
try:
    initialize_data()
except Exception:
    st.error(t('数据初始化失败，请检查部署日志或运行 python -m bankwise.data。'))
    st.stop()
server_key = setting('OPENAI_API_KEY')
access_code = ''
with st.sidebar:
    st.title('◈ Bankwise')
    st.caption('FINTECH ANALYTICS LAB')
    mode = st.radio(t('分析模式'), [t('预设问题演示'), t('模型自由提问')])
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
    st.markdown(t('**数据范围**\n\n葡萄牙银行营销观察数据\n\n2008–2010 · 非实时业务'))
    st.link_button(t('数据来源与许可 ↗'), 'https://archive.ics.uci.edu/dataset/222/bank+marketing')
    st.caption(t('没有收入、成本、客户唯一 ID 或完整日期。'))
st.caption('BANKING / CAMPAIGN INTELLIGENCE')
st.title(t('把业务问题，变成可核对的分析'))
st.write(t('查询真实银行营销记录，查看 SQL、结果与分析边界。'))
overall = execute(CATALOG['overall']['sql'])['rows'][0]
c1, c2, c3 = st.columns(3)
c1.metric(t('营销观察记录'), f'{overall[0]:,}')
c2.metric(t('定期存款订阅记录'), f'{overall[1]:,}')
c3.metric(t('观察记录转化率'), f'{overall[2]:.2f}%')
st.caption(t('统计口径：订阅记录数 ÷ 全部观察记录数；不是独立客户转化率。'))
analysis_tab, sql_tab, data_tab, learn_tab = st.tabs([t('业务分析'), t('SQL 工作台'), t('数据与口径'), t('学习入口')])

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
        if 'conversion_pct' in frame.columns and len(frame) > 1:
            dims = [col for col in frame.columns if col not in {'observations', 'subscriptions', 'conversion_pct', 'position'}]
            if dims:
                chart = frame.copy()
                chart[t('分组')] = chart[dims].astype(str).agg(' / '.join, axis=1)
                st.bar_chart(chart, x=t('分组'), y='conversion_pct', color='#176b69')
        st.dataframe(frame, hide_index=True, width='stretch')
        intervals = uncertainty(table, language=language)
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
                planner = OpenAIPlanner(key=key, model=model, language=language)
                with st.spinner(t('读取结构、生成并校验 SQL…')):
                    st.session_state['analysis'] = analyze(question, planner=planner, language=language)
            except ValueError as exc:
                st.error(t(str(exc)))
    expected_mode = 'demo' if mode == t('预设问题演示') else 'live'
    if 'analysis' in st.session_state and st.session_state['analysis']['mode'] == expected_mode and st.session_state['analysis'].get('language', 'zh') == language:
        st.caption(t('本次问题：') + st.session_state['analysis']['question'])
        display(st.session_state['analysis'], 'analysis')
with sql_tab:
    st.subheader(t('动手核对 SQL'))
    st.caption(t('单条只读 SELECT · 最多返回 200 行 · 限制执行资源'))
    sql = st.text_area('SQL', CATALOG['channel']['sql'], height=170)
    if st.button(t('执行 SQL')):
        try:
            table = execute(sql)
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
    st.subheader(t('先理解一行数据代表什么'))
    st.write(t('一行是源数据中的一条营销观察记录。系统生成 observation_id 方便定位，不代表真实客户编号。'))
    st.markdown((ROOT / 'docs' / ('DATA_CARD_EN.md' if language == 'en' else 'DATA_CARD.md')).read_text(encoding='utf-8'))
    with st.expander(t('数据库字段')):
        st.dataframe(pd.DataFrame(schema()), hide_index=True)
    manifest = ROOT / 'data' / 'manifest.json'
    if manifest.exists():
        with st.expander(t('数据来源和 SHA-256')):
            st.json(json.loads(manifest.read_text(encoding='utf-8')))
with learn_tab:
    st.subheader(t('先会用，再读懂，最后独立修改'))
    st.write(t('从 docs/STUDY_GUIDE.md 开始。每一节都有对应文件、练习和通过标准。'))
    st.markdown(t('1. 跑三个分析，解释样本量与转化率。\n2. 在 SQL 工作台重写一个分组查询。\n3. 跟踪 agent.py 的状态流转。\n4. 理解只读保护为何不能只靠提示词。\n5. 完成独立练习，再准备面试。'))
    guide = ROOT / 'docs' / ('STUDY_GUIDE_EN.md' if language == 'en' else 'STUDY_GUIDE.md')
    if guide.exists():
        st.download_button(t('下载中文学习指南'), guide.read_text(encoding='utf-8'), ('STUDY_GUIDE_EN.md' if language == 'en' else 'STUDY_GUIDE.md'))
