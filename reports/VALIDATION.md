# 验证记录

2026-09-26 上线更新：GitHub Actions 两次运行成功，Streamlit Community Cloud 在 Python 3.12.14 上启动成功；在线地址 https://bankwise-juju123.streamlit.app/ ，页面执行总体分析得到 41,188 / 4,640 / 11.2654%。云平台自动将 pyarrow 25.0.1 替换为 24.0.0。模型 API 尚待密钥配置。

2026-09-26 部署准备更新：增加服务器密钥访问口令、SQLite 原子每日配额与自动初始化，pytest 共 31 项通过。GitHub 源码已推送；Streamlit 登录未完成，真实 API 尚无密钥。

验证日期：2026-09-25。环境：Windows、Python 3.12.14；依赖版本见 requirements.txt。

| 验证 | 结果 | 能证明什么 |
|---|---|---|
| 真实数据 ETL | 成功：41,188 行、4,640 正例 | 下载、类型转换、SQLite 写入和基本源数据一致性 |
| pytest | 26 passed | 计算、防护、重试控制流程、区间计算、Streamlit 界面集成 |
| 固定演示评测 | 15/15 通过 | 11 个查询与独立 CSV/Python 结果一致，4 个固定拒答案例正确 |
| 浏览器实际打开 | 成功 | 总体指标显示、渠道问题选择、执行后返回 cellular 14.74%、样本量 26,144 |
| 模型 API 调用 | 未执行 | 用户暂时没有密钥；不提供真实模型准确率 |
| GitHub CI / Docker / 云部署 | 未执行 | 配置文件已交付，不能声称已上线 |

第一轮 ETL 在 Windows 遇到 SQLite 连接未关闭导致文件无法替换，已使用 contextlib.closing 显式关闭，重跑成功。

固定评测详情和每个 SQL 结果见 demo-evaluation.json。模型修复使用模拟 planner 测试，不代表真实模型可可靠修复所有错误。
