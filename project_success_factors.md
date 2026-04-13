# 客户支持智能体 (Customer Support Agent) 项目分析与关键成功要素

## 1. 项目概述
本项目是一个基于大语言模型（LLM）的智能客户支持系统。它模拟了真实的人工客服标准作业程序（SOP），通过多轮对话引导用户完成**保修信息核实**、**问题分类**以及**提供解决方案/转接人工**的完整闭环。

## 2. 核心技术栈
- **核心框架**: `LangChain` & `LangGraph` (用于构建基于状态的 Agent 和工作流)。
- **大语言模型 (LLM)**: `DashScope` (调用阿里云通义千问 `qwen3-max` 模型)。
- **状态持久化**: `langgraph.checkpoint.memory.InMemorySaver` (基于 `thread_id` 的多轮对话记忆与状态追踪，为后续无缝切换到 SQLite/Postgres 等持久化方案打下基础)。
- **包管理工具**: `uv` (用于极速依赖安装与虚拟环境管理)。

## 3. 关键设计思想与架构模式

该项目之所以结构清晰且健壮，得益于以下几个核心架构思想：

### 3.1 状态机模式 (State Machine Pattern)
项目没有让大模型“自由发挥”，而是通过 `SupportState` (定义在 [state.py](file:///d:/Java_study/agent/customer-support-agent/agent/state.py)) 将整个对话过程严格划分为离散的阶段：
1. `warranty_collector` (保修收集)
2. `issue_classifier` (问题分类)
3. `resolution_specialist` (解决专家)
这种状态机驱动的设计确保了业务流程的强一致性。

### 3.2 动态中间件拦截 (Dynamic Middleware Interception)
这是项目最亮眼的设计之一。在 [agent.py](file:///d:/Java_study/agent/customer-support-agent/agent/agent.py) 中，使用了 `@wrap_model_call` 装饰器定义了 `apply_step_config` 中间件。
- **动态 Prompt 与工具绑定**: 中间件会在每次调用 LLM 前，根据当前的 `current_step` 动态替换 System Prompt，并**仅注入当前步骤所需的工具**。
- **效果**: 大模型在“保修核实”阶段根本看不到“提供解决方案”的工具，从根本上杜绝了模型“抢跑”或越权操作。

### 3.3 基于工具的状态流转 (Tool-driven State Mutation)
在 [tools.py](file:///d:/Java_study/agent/customer-support-agent/tools/tools.py) 中，工具不仅用于执行特定动作，还承担了**驱动状态机流转**的责任。
- 例如 `record_warranty_status` 工具执行后，不仅记录了状态，还通过返回 `Command(update={"current_step": "issue_classifier", ...})` 直接修改了全局 State，从而平滑过渡到下一个阶段。

### 3.4 自动化上下文管理
在 `create_agent` 时引入了 `SummarizationMiddleware`。当对话 token 达到 4000 时，系统会自动对历史消息进行摘要，并仅保留最近的 10 条消息。这有效解决了长对话导致的 Context Window 溢出和成本剧增问题。

## 4. 促成项目成功的关键因素

1. **极高的可控性与极低的幻觉 (Low Hallucination)**
   - **防抢跑机制**: 通过前置校验机制（`requires: ["warranty_status"]`），如果缺少必要信息，状态机将拒绝进入下一阶段。
   - 结合动态工具分发，模型被死死限制在当前任务上下文中，无法做出偏离 SOP 的回复。
2. **声明式配置 (Declarative Configuration)**
   - 使用 `STEP_CONFIG` 字典统一管理“步骤-提示词-工具-依赖”的映射关系。新增一个业务步骤只需在字典中加一项，完全符合开闭原则（OCP）。
3. **高内聚低耦合的模块化 (High Cohesion, Low Coupling)**
   - `prompts.py`: 纯文本提示词管理。
   - `state.py`: 严格的类型提示 (Type Hinting) 和数据结构。
   - `tools.py`: 具体的业务逻辑执行单元。
   - `agent.py`: 纯粹的编排与中间件逻辑。
   这种分离使得项目非常易于测试、维护和扩展。
4. **面向生产环境的设计考量 (Production-Ready)**
   - 考虑到了真实场景下的异常流（例如超过保修期转接人工 `escalate_to_human`）。
   - 引入了 Thread ID 机制 (在 [main.py](file:///d:/Java_study/agent/customer-support-agent/main.py) 中演示)，使得系统天生支持并发多用户的会话隔离。
