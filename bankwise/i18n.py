"""Local translations: language changes never call an external service."""
TEXT = {'Bankwise · 银行营销分析': 'Bankwise · Banking Analytics',
 '数据初始化失败，请检查部署日志或运行 python -m bankwise.data。': 'Data initialization failed. Check deployment logs '
                                                'or run python -m bankwise.data.',
 '分析模式': 'Analysis mode',
 '预设问题演示': 'Guided demo',
 '模型自由提问': 'Ask the AI analyst',
 '模型访问口令': 'Model access code',
 '由项目所有者提供。无需输入 API Key。': 'Provided by the project owner. No API key is needed.',
 '已由项目所有者配置模型；公开预设演示始终免费。': 'The owner has configured the model. Guided demos are always free.',
 '仅本次会话使用，不写入文件。': 'Used only in this session; never saved to a file.',
 '模型 ID': 'Model ID',
 '填写你的账户可用模型': 'Enter a model available to your account',
 '请求会将你的问题和表结构发给模型服务。最多两次请求；数据结果由本地程序生成摘要。': 'Your question and table schema are sent to the model '
                                             'provider. Up to two requests; summaries are computed '
                                             'from query results locally.',
 '数据来源与许可 ↗': 'Dataset and license ↗',
 '没有收入、成本、客户唯一 ID 或完整日期。': 'No revenue, costs, unique customer IDs, or complete dates.',
 '把业务问题，变成可核对的分析': 'Turn business questions into verifiable analysis',
 '查询真实银行营销记录，查看 SQL、结果与分析边界。': 'Explore real bank marketing records with transparent SQL, results, '
                               'and limitations.',
 '营销观察记录': 'Marketing observations',
 '定期存款订阅记录': 'Term deposit subscriptions',
 '观察记录转化率': 'Observation conversion rate',
 '统计口径：订阅记录数 ÷ 全部观察记录数；不是独立客户转化率。': 'Metric: subscribed observations / all observations. This is '
                                    'not a unique-customer conversion rate.',
 '业务分析': 'Business analysis',
 'SQL 工作台': 'SQL workbench',
 '数据与口径': 'Data and definitions',
 '学习入口': 'Learning resources',
 '模型查询': 'Live model query',
 '预设 SQL 演示 · 未调用模型': 'Preset SQL demo · No model call',
 '分析结果': 'Analysis results',
 '分组': 'Group',
 '样本量与转化率区间': 'Sample sizes and conversion intervals',
 '95% Wilson 描述性区间，假设观察相互独立；无法识别同一客户重复出现，未调整混杂因素或多重比较。不是因果置信区间。': '95% descriptive Wilson '
                                                                  'intervals assume independent '
                                                                  'observations. Repeated '
                                                                  'customers cannot be identified; '
                                                                  'confounding and multiple '
                                                                  'comparisons are not adjusted '
                                                                  'for. These are not causal '
                                                                  'intervals.',
 '结果超过 200 行，仅展示前 200 行；摘要也仅针对已返回行。': 'Only the first 200 rows are shown. The summary covers '
                                      'returned rows only.',
 '查看执行 SQL': 'View executed SQL',
 '下载结果 CSV': 'Download results CSV',
 '解读边界': 'Interpretation limits',
 '执行轨迹与耗时': 'Execution trace and latency',
 '下载本次分析 JSON': 'Download analysis JSON',
 '从一个明确的问题开始': 'Start with a clear question',
 '选择业务问题': 'Choose a business question',
 '运行分析': 'Run analysis',
 '你的问题': 'Your question',
 '例如：按渠道比较转化率，并显示每组样本量。': "For example: Compare conversion rates by channel and show each group's "
                          'sample size.',
 '提交给模型': 'Ask model',
 '请先输入问题。': 'Enter a question first.',
 '项目所有者尚未配置模型 ID。': 'The project owner has not configured a model ID.',
 '请填写自己的 API Key。': 'Enter your API key.',
 '读取结构、生成并校验 SQL…': 'Inspecting schema, generating and validating SQL…',
 '本次问题：': 'Question: ',
 '动手核对 SQL': 'Inspect and run SQL',
 '单条只读 SELECT · 最多返回 200 行 · 限制执行资源': 'One read-only SELECT · Up to 200 returned rows · Bounded '
                                      'execution',
 '执行 SQL': 'Run SQL',
 '结果已截断至 200 行。': 'Results are truncated to 200 rows.',
 '先理解一行数据代表什么': 'Understand what one row represents',
 '一行是源数据中的一条营销观察记录。系统生成 observation_id 方便定位，不代表真实客户编号。': 'Each row is a source marketing '
                                                         'observation. The generated '
                                                         'observation_id locates a row; it is not '
                                                         'a real customer identifier.',
 '数据库字段': 'Database fields',
 '数据来源和 SHA-256': 'Provenance and SHA-256',
 '先会用，再读懂，最后独立修改': 'Explore, understand, then build independently',
 '从 docs/STUDY_GUIDE.md 开始。每一节都有对应文件、练习和通过标准。': 'Start with docs/STUDY_GUIDE_EN.md. Each section '
                                                'includes source files, exercises, and completion '
                                                'criteria.',
 '下载中文学习指南': 'Download English study guide',
 '请在侧栏或环境变量中设置 API Key 和可用的模型 ID。': 'Set an API key and an available model ID in the sidebar or '
                                    'environment.',
 '请输入 1–2000 字的问题。': 'Enter a question of 1–2,000 characters.',
 '演示模式只支持下拉菜单中的预设问题；自由提问需要启用模型。': 'Demo mode supports only the listed questions. Enable the model '
                                  'to ask custom questions.',
 '按源数据观察记录计算；不是独立客户口径。': 'Calculated per source observation, not per unique customer.',
 '请明确分析口径。': 'Please clarify the metric and scope.',
 '两次尝试后仍未得到可执行查询。请重新表述问题或检查执行轨迹。': 'No executable query after two attempts. Rephrase the question '
                                   'or inspect the execution trace.',
 '转化率描述相关性，不能证明渠道或营销次数造成转化变化。': 'Conversion differences describe associations, not causal effects '
                                'of channels or contact frequency.',
 '月份跨年份合并，不能解释为连续月度趋势；没有收入、成本或客户唯一标识。': 'Months are pooled across years, not a consecutive time '
                                        'series. Revenue, costs, and unique customer IDs are '
                                        'unavailable.',
 'duration 是通话结束后才知道的变量，不能用于联系前的预测或客群选择。': 'Call duration is known only after a call and must not '
                                           'be used for pre-contact prediction or targeting.',
 '数据没有收入、金额或成本字段，不能计算收入或 ROI。': 'The dataset has no revenue, amount, or cost fields. Revenue and '
                                'ROI cannot be calculated.',
 '数据没有稳定的客户 ID；observation_id 只是导入行号，不能去重客户。': 'There is no stable customer ID. observation_id is '
                                               'an imported row number and cannot identify unique '
                                               'customers.',
 '这是观察数据，不能确定因果。可比较渠道转化，但需考虑客群选择偏差。': 'Observational data cannot establish causation. Channel '
                                      'conversion can be compared, but selection bias must be '
                                      'considered.',
 '源数据没有逐行年份和完整日期，不能计算可靠的年月环比。': 'Per-row years and complete dates are missing, so reliable '
                                'month-over-month changes cannot be calculated.',
 '请输入正确的模型访问口令；未配置口令时服务器密钥保持禁用。': 'Enter the correct model access code. Server-key access stays '
                                  'disabled if no code is configured.',
 '本站今日模型提问额度已用完，请明天再试。': "Today's model question allowance has been reached. Try again tomorrow.",
 'OpenAI 返回额度不足（insufficient_quota）。请核对充值账户/组织是否与此 API Key 所属项目一致，以及该组织的余额与用量限制；不要盲目重复充值。': 'OpenAI '
                                                                                            'returned '
                                                                                            'insufficient_quota. '
                                                                                            'Check '
                                                                                            'the '
                                                                                            'API '
                                                                                            "key's "
                                                                                            'organization, '
                                                                                            'prepaid '
                                                                                            'balance, '
                                                                                            'and '
                                                                                            'usage '
                                                                                            'limits '
                                                                                            'before '
                                                                                            'purchasing '
                                                                                            'more '
                                                                                            'credits.',
 'OpenAI 返回请求或 token 速率限制。请稍后重试，并检查模型的项目速率额度。': 'OpenAI returned a request or token rate limit. '
                                                "Try later and check the project's model limits.",
 'OpenAI 要求降低请求速率，请稍后重试。': 'OpenAI requested a slower request rate. Try again later.',
 'OpenAI 拒绝此 API Key，请在 Secrets 中更新有效密钥。': 'OpenAI rejected the API key. Update it in Secrets.',
 '当前模型不存在或此项目无访问权限，请检查 OPENAI_MODEL。': 'The model does not exist or this project lacks access. '
                                       'Check OPENAI_MODEL.',
 '模型请求失败，请检查密钥、模型权限、额度或网络；没有自动切换成演示答案。': 'The model request failed. Check credentials, model '
                                         'access, quota, or connectivity. No demo answer was '
                                         'substituted.',
 '观察记录数': 'Observations',
 '转化率下界 (%)': 'Conversion lower bound (%)',
 '转化率上界 (%)': 'Conversion upper bound (%)',
 '样本提示': 'Sample note',
 '小样本，谨慎解读': 'Small sample: interpret with caution',
 '**数据范围**\n\n葡萄牙银行营销观察数据\n\n2008–2010 · 非实时业务': '**Data scope**\n'
                                                 '\n'
                                                 'Portuguese bank marketing observations\n'
                                                 '\n'
                                                 '2008–2010 · Historical data',
 '1. 跑三个分析，解释样本量与转化率。\n2. 在 SQL 工作台重写一个分组查询。\n3. 跟踪 agent.py 的状态流转。\n4. 理解只读保护为何不能只靠提示词。\n5. 完成独立练习，再准备面试。': '1. '
                                                                                                             'Run '
                                                                                                             'three '
                                                                                                             'analyses '
                                                                                                             'and '
                                                                                                             'explain '
                                                                                                             'sample '
                                                                                                             'sizes '
                                                                                                             'and '
                                                                                                             'conversion '
                                                                                                             'rates.\n'
                                                                                                             '2. '
                                                                                                             'Rewrite '
                                                                                                             'a '
                                                                                                             'grouped '
                                                                                                             'query '
                                                                                                             'in '
                                                                                                             'the '
                                                                                                             'SQL '
                                                                                                             'workbench.\n'
                                                                                                             '3. '
                                                                                                             'Trace '
                                                                                                             'the '
                                                                                                             'state '
                                                                                                             'flow '
                                                                                                             'in '
                                                                                                             'agent.py.\n'
                                                                                                             '4. '
                                                                                                             'Explain '
                                                                                                             'why '
                                                                                                             'prompts '
                                                                                                             'alone '
                                                                                                             'cannot '
                                                                                                             'enforce '
                                                                                                             'read-only '
                                                                                                             'access.\n'
                                                                                                             '5. '
                                                                                                             'Complete '
                                                                                                             'an '
                                                                                                             'independent '
                                                                                                             'exercise '
                                                                                                             'before '
                                                                                                             'preparing '
                                                                                                             'for '
                                                                                                             'interviews.'}

def tr(text, language='zh'):
    return TEXT.get(text, text) if language == 'en' else text

QUESTIONS_EN = {
    'overall': 'What is the overall conversion rate?',
    'channel': 'How do conversion rates differ by contact channel?',
    'job': 'Which job groups have higher conversion rates?',
    'education': 'What is the conversion rate by education level?',
    'month': 'Compare conversion by month (pooled across years)',
    'history': 'How does the previous campaign outcome relate to conversion?',
    'loan': 'How does personal loan status relate to conversion?',
    'frequency': 'How does contact frequency relate to conversion?',
    'age': 'What is the conversion rate by age group?',
    'rank': 'What are the top three jobs within each contact channel?',
    'quality': 'How many unknown values are in key fields?',
    'revenue': 'Why did revenue decline?',
    'customers': 'How many unique customers are there?',
    'causal': 'Does telephone contact cause lower conversion?',
    'trend': 'What is the month-over-month conversion change for March 2010?',
}

def question_text(key, language='zh'):
    from .catalog import CATALOG
    return QUESTIONS_EN[key] if language == 'en' else CATALOG[key]['question']

TEXT['总耗时'] = 'Total latency'
