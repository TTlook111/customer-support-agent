from typing import Literal

from langgraph.types import Command
from langchain.messages import ToolMessage
from langchain.tools import tool, ToolRuntime

from agent.state import SupportState


@tool
def record_warranty_status(
    status: Literal["in_warranty", "out_of_warranty"],
    runtime: ToolRuntime[None, SupportState],
) -> Command:
    """记录客户的设备保修状态，并进入问题分类阶段。"""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"保修状态已记录为: {status}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "warranty_status": status,
            "current_step": "issue_classifier",
        }
    )


@tool
def record_issue_type(
    issue_type: Literal["hardware", "software"],
    runtime: ToolRuntime[None, SupportState],
) -> Command:
    """记录客户的问题类型，并进入解决方案专家阶段。"""
    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"问题类型已记录为: {issue_type}",
                    tool_call_id=runtime.tool_call_id,
                )
            ],
            "issue_type": issue_type,
            "current_step": "resolution_specialist",
        }
    )


@tool
def escalate_to_human(reason: str) -> str:
    """因特定原因，将当前案件升级/转接给人工支持专家。"""
    # 在实际的生产系统中，这里通常会创建工单或通知人工客服等
    return f"已升级至人工客服。原因: {reason}"


@tool
def provide_solution(solution: str) -> str:
    """为客户遇到的问题提供解决步骤。"""
    return f"已提供解决方案: {solution}"
