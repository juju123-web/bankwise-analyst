# Bankwise · FinTech Business Analyst Agent

用真实银行营销数据，把中文业务问题转成可审查的 SQL、图表和描述统计。为 **SQL + Python + Data Agent** 求职作品设计。

项目提供两个明确区分的模式：

源码仓库：[juju123-web/bankwise-analyst](https://github.com/juju123-web/bankwise-analyst)。当前已推送源码；Streamlit 上线等待账户登录完成。

- **预设演示**：15 个固定问题，直接执行经过验证的 SQL；无需密钥。这不是自然语言模型。
- **模型自由提问**：通过 OpenAI Responses API 生成 SQL，校验并执行，失败后最多修复一次。需要自己的 API Key 和模型 ID；当前交付未进行真实付费 API 测试。

## 5 分钟启动

需要 Python 3.12，首次安装与下载需要网络。在本文件所在目录运行：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m bankwise.data
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Windows 也可运行 `./start.ps1`。macOS/Linux 将 Python 路径换成 `.venv/bin/python`。打开终端显示的本地网址（通常为 http://localhost:8501）。已交付目录包含下载后的数据，重复执行 ETL 会从缓存重建数据库。

## 第一次展示

1. 打开“业务分析”，运行“各联系渠道的转化率有什么差异”。
2. 展开 SQL，解释分母、分子、浮点除法；查看样本量和 Wilson 区间。
3. 运行“每个渠道内转化率最高的三个职业”，解释 CTE、窗口函数和样本量门槛。
4. 运行“收入为什么下降”，展示系统承认数据缺失。
5. 到 SQL 工作台执行 `DELETE FROM bank_contacts`，展示查询被拒绝、数据仍保持只读。

## 数据与业务问题

采用 [UCI Bank Marketing](https://archive.ics.uci.edu/dataset/222/bank+marketing) 的 `bank-additional-full.csv`，41,188 条观察、4,640 条订阅，CC BY 4.0；作者 S. Moro、P. Rita、P. Cortez。转换字段名、保留 unknown、生成观察行号和 0/1 标签；没有合成业务数据。

重点分析：渠道、职业、年龄段、教育、历史营销结果、联系频次，以及数据质量。数据没有收入、成本、独立客户 ID 或逐行年份，因此不支持 ROI、客户留存、可靠年月环比或因果结论。详见 [数据卡](docs/DATA_CARD.md)。

## 验证

```powershell
python -m pytest -q
python -m bankwise.evaluate
```

评测直接读取原始 CSV，用 Python 独立计算答案，对照 SQL 结果。固定演示集共 15 题（11 个查询、4 个拒答），报告在 `reports/demo-evaluation.json`。**演示通过率不等于模型准确率。** 测试还覆盖危险 SQL、执行预算、截断、空结果、错误修复、隐去服务错误中的敏感内容和 Streamlit 页面操作。

## 启用模型

未配置服务端密钥时，侧栏选择“模型自由提问”，输入个人密钥和账户可用的模型 ID；密钥仅在会话内使用。云端可通过 Secrets 设置 `OPENAI_API_KEY`、`OPENAI_MODEL`，此时还必须设置 `BANKWISE_ACCESS_CODE`，访问者需输入口令；默认每日最多 30 个问题，跨会话共享当前实例的额度。配置与计数持久性边界见部署文档。不要把密钥提交到 GitHub。实现使用 [OpenAI Responses API 官方说明](https://developers.openai.com/api/docs/quickstart)。

每个问题最多两次请求，每次最多 1,600 个输出 token、40 秒请求超时。结果摘要由本地程序基于实际返回值生成，数据库行不发送给模型。schema、问题以及失败 SQL/错误可能发送给服务；`store=False`。Token usage 随结果记录，不虚构费用。

```powershell
# 已通过环境变量配置后运行；会产生 API 用量
python -m bankwise.evaluate --live
```

Live 评测是 15 个固定问题的严格结果比对；为了可自动核对，会指定输出列顺序。拒答只检查状态，不能代替人工审查解释质量。模型可能写出语法正确但口径错误的 SQL，必须审核；SQL 防护保障只读，不保证业务正确。

## 代码地图

| 文件 | 职责 |
|---|---|
| `app.py` | 四个页面区块、图表、会话状态、结果导出 |
| `bankwise/data.py` | 下载、数据验证、类型转换、SQLite 原子替换 |
| `bankwise/catalog.py` | 固定问题与参考 SQL |
| `bankwise/sql.py` | AST 校验、SQLite authorizer、只读连接、资源上限 |
| `bankwise/agent.py` | 模型适配器、两次尝试的状态流程、确定性摘要 |
| `bankwise/insights.py` | Python Wilson 区间与样本量提示 |
| `bankwise/evaluate.py` | 独立 CSV 参考答案、演示/模型评测 |
| `tests/` | 单元与界面集成测试 |

## 完成标准与交付边界

- 已实现：真实数据 ETL、本地网页、11 类 SQL 查询、4 类明确拒答、图表、SQL 工作台、JSON/CSV 导出、区间统计、测试、评测、中文学习指南、面试材料。
- 已提供但未外部验证：模型 API 接入、GitHub Actions 配置、Dockerfile、公开部署步骤。
- 已完成 GitHub 源码发布；尚未完成真实模型评测和公开网站发布，需要后续密钥与 Streamlit 登录。不能把本地网址写成公共 Demo。
- 不属于本版：生产权限系统、多租户、实时银行数据、PostgreSQL、金融风控或自动营销决策。

这是单用户、可运行的求职学习项目。为易读和可验证使用 SQLite 与有限状态流程，不为了堆技术引入不必要的 Agent 框架。架构与权衡见 [ARCHITECTURE](docs/ARCHITECTURE.md)。

## 学习和发布

从 [中文 Study Guide](docs/STUDY_GUIDE.md) 开始；准备展示参考 [面试与演示指南](docs/INTERVIEW.md)，部署参考 [DEPLOYMENT](docs/DEPLOYMENT.md)。建议理解后再将能力写进简历。

代码采用 MIT 许可。原始数据单独遵循 CC BY 4.0，转载需保留来源及作者署名。
