from typing import Literal
from typing_extensions import NotRequired
from langchain.agents import AgentState

# 定义可能的工作流步骤枚举
SupportStep = Literal["warranty_collector", "issue_classifier", "resolution_specialist"]

class SupportState(AgentState):
    """客户支持工作流的状态类（State）。"""

    # current_step: 当前所处的工作流步骤
    current_step: NotRequired[SupportStep]
    # warranty_status: 记录客户设备的保修状态，可以是 "in_warranty"（在保修期内）或 "out_of_warranty"（已过保修期）
    warranty_status: NotRequired[Literal["in_warranty", "out_of_warranty"]]
    # issue_type: 记录问题分类，可以是 "hardware"（硬件问题）或 "software"（软件问题）
    issue_type: NotRequired[Literal["hardware", "software"]]
