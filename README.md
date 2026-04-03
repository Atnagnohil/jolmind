# Jolmind

基于 Langchain 的私人 AI 助手，提供 RESTful API 接口，支持多 LLM 提供商、会话管理、消息持久化与流式对话。

## 技术栈

- **框架**：FastAPI + Uvicorn
- **Agent**：LangChain / LangGraph（ReAct 架构）
- **持久化**：SQLAlchemy + MySQL（业务数据）、SQLite（LangGraph checkpoint）
- **可观测**：LangSmith 链路追踪、Loguru 日志
- **搜索**：Tavily Web Search

## 项目结构

```
src/
├── agent/          # Agent 构建、记忆、提示词、工具
│   └── tools/builtin/  # 内置工具：计算器、网页抓取、文件、时间、搜索
├── api/            # FastAPI 应用、路由、依赖注入
│   └── routers/    # chat / sessions / messages / users / providers / ...
├── config/         # 配置加载
├── db/             # SQLAlchemy 模型与 CRUD
├── providers/      # LLM 提供商注册与适配（OpenAI 兼容）
└── utils/          # 日志、LangSmith 初始化等工具
```

## 快速开始

**环境要求**：Python3，[uv](https://docs.astral.sh/uv/)

```bash
# 安装依赖
uv sync

# 复制并编辑配置
cp example-config.yaml config.yaml

# 启动服务
python main.py
```

服务默认运行在 `http://0.0.0.0:8080`，API 文档见 `http://localhost:8080/docs`。

## 配置

配置文件为项目根目录下的 `config.yaml`，参考 `example-config.yaml`。

| 配置项　　　　　　　 | 说明　　　　　　　　　　　　　　　　　　 |
| ----------------------| ------------------------------------------|
| `llm.default`　　　　| 默认使用的 provider 名称　　　　　　　　 |
| `llm.providers`　　　| LLM 提供商列表，支持任意 OpenAI 兼容接口 |
| `db.url`　　　　　　 | MySQL 连接字符串　　　　　　　　　　　　 |
| `memory.sqlite_path` | LangGraph checkpoint 数据库路径　　　　　|
| `tavily.api_key`　　 | Tavily 搜索 API Key　　　　　　　　　　　|
| `langsmith`　　　　　| LangSmith 链路追踪（可选）　　　　　　　 |

## 内置工具

| 工具            | 说明               |
| --------------- | ------------------ |
| `web_search`    | Tavily 网络搜索    |
| `fetch_webpage` | 抓取网页内容       |
| `file_tools`    | 读写本地工作区文件 |
| `calculator`    | 数学计算           |
| `time_tool`     | 获取当前时间       |
