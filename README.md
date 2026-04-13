# Customer Support Agent 📞

基于 LangChain 框架构建的**客户支持多步状态机 Agent 示例**。

本项目展示了如何使用状态机模式和中间件（Middleware）机制，根据用户对话的进展（即当前状态 `current_step`），动态改变 Agent 的行为（切换系统提示词和可用的工具），从而实现按特定顺序收集客户信息的智能客服工作流。

## 🌟 核心特性

- **多步骤状态机机制**：将客服流程拆分为三个清晰的递进阶段：
  1. `warranty_collector`：核实设备保修状态。
  2. `issue_classifier`：问题类型判定（硬件/软件）。
  3. `resolution_specialist`：提供针对性解决方案或转接人工。
- **动态行为注入**：使用 `@wrap_model_call` 中间件，在每次大模型调用前，依据当前步骤拦截请求，并自动注入与之匹配的 Prompt 和 Tools。
- **记忆与长对话摘要**：集成了 `InMemorySaver` 和 `SummarizationMiddleware`，支持基于 Thread ID 的对话记忆持久化以及长文本摘要截断机制。
- **国产大模型集成**：无缝对接阿里云通义千问（Qwen3-Max）作为核心模型驱动引擎。

## 🛠️ 技术栈

- **编程语言**：Python >= 3.13
- **依赖管理**：[uv](https://docs.astral.sh/uv/)
- **核心框架**：LangChain, LangGraph
- **大语言模型**：DashScope API (通义千问)

## 📂 项目结构

```text
customer-support-agent/
├── agent/
│   ├── agent.py         # 核心代理定义，包含中间件逻辑和状态路由
│   └── state.py         # Agent 状态类 (SupportState) 定义
├── config/
│   └── config.py        # 环境与全局配置加载
├── prompts/
│   └── prompts.py       # 各工作流步骤专用的系统提示词 (Prompt)
├── tools/
│   └── tools.py         # Agent 可供调用的工具集 (Tools)
├── main.py              # 测试与对话交互入口脚本
├── pyproject.toml       # 项目及依赖配置
└── README.md            # 项目说明文档
```

## 🚀 快速开始

### 1. 环境准备

推荐使用 `uv` 进行依赖管理和虚拟环境构建：

```bash
# 安装依赖
uv sync
```

### 2. 环境变量配置

在项目根目录下创建一个 `.env` 文件，并填入你的阿里云 DashScope API 密钥：

```env
# 必须：阿里云大模型 API 密钥
DASHSCOPE_API_KEY="your_api_key_here"

# 可选：如果需要使用 LangSmith 监控追踪执行过程
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY="your_langsmith_api_key"
```

### 3. 运行测试体验

执行 `main.py` 脚本，体验整个智能客服按步骤引导的工作流：

```bash
uv run main.py
```
