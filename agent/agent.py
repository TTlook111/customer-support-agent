from typing import Callable

from langchain.agents import create_agent
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse, SummarizationMiddleware
from langchain_community.chat_models.tongyi import ChatTongyi
from langgraph.checkpoint.memory import InMemorySaver

from agent.state import SupportState
from prompts.prompts import WARRANTY_COLLECTOR_PROMPT, ISSUE_CLASSIFIER_PROMPT, RESOLUTION_SPECIALIST_PROMPT
from tools.tools import record_warranty_status, record_issue_type, escalate_to_human, provide_solution

# 初始化通义千问大语言模型
model = ChatTongyi(model="qwen3-max")

# 步骤配置：将工作流的步骤名映射到其对应的 (提示词, 工具列表, 所需的状态字段)
STEP_CONFIG = {
    "warranty_collector": {
        "prompt": WARRANTY_COLLECTOR_PROMPT,
        "tools": [record_warranty_status],
        "requires": [],
    },
    "issue_classifier": {
        "prompt": ISSUE_CLASSIFIER_PROMPT,
        "tools": [record_issue_type],
        "requires": ["warranty_status"],
    },
    "resolution_specialist": {
        "prompt": RESOLUTION_SPECIALIST_PROMPT,
        "tools": [provide_solution, escalate_to_human],
        "requires": ["warranty_status", "issue_type"],
    },
}

@wrap_model_call
def apply_step_config(
    request: ModelRequest,
    handler: Callable[[ModelRequest], ModelResponse],
) -> ModelResponse:
    """根据工作流所处的当前步骤，动态配置 Agent（代理）的行为。"""
    
    # 获取当前处于的步骤（如果未设置，说明是第一次交互，默认进入“保修信息核实”步骤）
    current_step = request.state.get("current_step", "warranty_collector")

    # 查找该步骤对应的配置
    step_config = STEP_CONFIG[current_step]

    # 校验进入该步骤所必须依赖的状态是否已存在
    for key in step_config["requires"]:
        if request.state.get(key) is None:
            raise ValueError(f"在进入 {current_step} 步骤之前，必须先收集并设置状态: {key}")

    # 使用当前状态字典中的值，来格式化系统提示词（如填入 warranty_status 变量）
    system_prompt = step_config["prompt"].format(**request.state)

    # 将格式化后的系统提示词和当前步骤专属的工具列表注入到请求中
    request = request.override(
        system_prompt=system_prompt,
        tools=step_config["tools"],
    )

    return handler(request)

# 汇总各个步骤所用到的所有工具列表
all_tools = [
        record_warranty_status,
        record_issue_type,
        provide_solution,
        escalate_to_human,
]

# 创建 Agent 代理，同时挂载步骤配置与对话摘要中间件
agent = create_agent(
    model,
    tools=all_tools,
    state_schema=SupportState,
    middleware=[
        apply_step_config,
        SummarizationMiddleware(
            model=ChatTongyi(model="qwen3-max"),
            trigger=("tokens", 4000),
            keep=("messages", 10)
        )
    ],
    checkpointer=InMemorySaver(),
)
