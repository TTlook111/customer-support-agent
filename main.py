"""
客户支持状态机示例 (Customer Support State Machine Example)

这个示例展示了状态机模式。
单个代理（Agent）根据 current_step（当前步骤）状态动态改变其行为，
从而构建了一个用于按顺序收集客户信息的状态机。
"""

from langchain_core.utils.uuid import uuid7
from langchain.messages import HumanMessage

import config.config  # 载入环境变量配置
from agent.agent import agent

# ============================================================================
# 测试工作流
# ============================================================================

if __name__ == "__main__":
    thread_id = str(uuid7())
    # 设置运行配置，其中 thread_id 用于记忆持久化与状态追踪
    config_obj = {"configurable": {"thread_id": thread_id}}

    print("--- 用户: 你好，我的手机屏幕碎了 ---")
    result = agent.invoke(
        {"messages": [HumanMessage("你好，我的手机屏幕碎了")]},
        config_obj
    )

    print("--- 用户: 是的，还在保修期内 ---")
    result = agent.invoke(
        {"messages": [HumanMessage("是的，还在保修期内")]},
        config_obj
    )

    print("--- 用户: 手机摔了一下，屏幕物理破裂了 ---")
    result = agent.invoke(
        {"messages": [HumanMessage("手机摔了一下，屏幕物理破裂了")]},
        config_obj
    )

    print("--- 用户: 我该怎么办？ ---")
    result = agent.invoke(
        {"messages": [HumanMessage("我该怎么办？")]},
        config_obj
    )
    
    print("\n--- 最终的对话消息记录 ---")
    for msg in result['messages']:
        msg.pretty_print()
