# 发布与复现

已部署到 Streamlit Community Cloud：https://bankwise-juju123.streamlit.app/ 。源码：https://github.com/juju123-web/bankwise-analyst ，分支 main、入口 app.py、Python 3.12。线上已核对总体查询：41,188 条观察、4,640 条订阅、11.2654% 转化率。模型自由提问仍等待 API Key 配置与真实调用验证。

## 已准备的云端配置（2026-09-26）

- 入口 `app.py`，Python 3.12，依赖从 requirements.txt 安装。
- 仓库携带 UCI 原始公开 ZIP，启动时自动生成数据库，无需访问者手动初始化。
- `.streamlit/config.toml` 配置主题并关闭使用统计；`.streamlit/secrets.example.toml` 是不含凭证的模板。
- 服务端有 API Key 时，必须配置并输入 BANKWISE_ACCESS_CODE 才能使用；缺少口令默认拒绝。
- 服务端密钥默认每天最多接收 30 个问题，每题最多两次 API 尝试；失败请求也计入。计数通过 SQLite 事务跨会话共享。
- 每日上限使用 UTC，计数仅保存在当前托管实例磁盘；云端重建/更换磁盘会清零，因此这不是跨部署持久限额，也不是美元硬上限。API 官方账户的付费管理需单独配置。

在 Cloud 的 Secrets 设置中填入四个模板字段，不提交到 GitHub。实际充值和密钥创建由账户所有者完成，不在聊天中粘贴密钥。

## GitHub

在自己准备发布的目录初始化 Git，检查 `.gitignore` 后提交。代码、文档、测试与演示评测报告可以提交；密钥、`.env`、虚拟环境不要提交。数据文件默认忽略，使用下载脚本重建；源码中已保留 UCI CC BY 4.0 署名。

```sh
git init
git add .
git status
git commit -m "Build Bankwise banking analytics project"
```

再通过你的 GitHub 账户新建仓库并添加其实际 remote 地址。`.github/workflows/tests.yml` 提供 Python 3.12 测试、真实数据下载与固定案例评测；UCI 网络失败会使 CI 失败，应区别于代码回归。

## 本地 Docker（需要另装 Docker）

```sh
docker build -t bankwise .
docker run --rm -p 8501:8501 bankwise
```

构建时下载数据，运行时以非 root 用户启动。这里未安装/运行 Docker，因此镜像尚未实测。API 密钥不写进镜像。

## 公开演示部署

可在支持 Python 容器的托管服务上部署 Dockerfile，开放 8501 端口，使用 HTTPS。或在支持 Streamlit 的托管平台上选仓库和 `app.py`。具体界面以平台当前说明为准。

公开求职展示提供预设演示。已添加口令与按实例每日问题限额保护服务端 API Key；这是小规模作品演示控制，不是完整用户认证或多租户配额系统。使用者输入的个人密钥只用于其 Streamlit 会话，不写入磁盘，但托管端仍能处理该请求。

## 发布验收

1. 新环境可以下载数据并启动页面。
2. 固定问题、SQL 保护、结果导出、拒答工作正常。
3. 运行测试和固定评测，保留结果。
4. 如启用模型，单独运行 live 评测并人工检查 SQL 语义；不要拿 demo 报告代替。
5. README 放真实公共链接；不要用 localhost 充当公共 Demo。
