#!/usr/bin/env python3
# Harness: the loop -- the model's first connection to the real world.
"""
s01_agent_loop.py - The Agent Loop

The entire secret of an AI coding agent in one pattern:

    while stop_reason == "tool_use":
        response = LLM(messages, tools)
        execute tools
        append results

    +----------+      +-------+      +---------+
    |   User   | ---> |  LLM  | ---> |  Tool   |
    |  prompt  |      |       |      | execute |
    +----------+      +---+---+      +----+----+
                          ^               |
                          |   tool_result |
                          +---------------+
                          (loop continues)

This is the core loop: feed tool results back to the model
until the model decides to stop. Production agents layer
policy, hooks, and lifecycle controls on top.
"""

import os
import subprocess

from anthropic import Anthropic
from dotenv import load_dotenv

# 读取 .env 中的环境变量，便于从本地配置 API 地址、模型名等参数
load_dotenv(override=True)

# 如果配置了自定义的 Anthropic 兼容服务地址，就移除官方鉴权 token 变量，
# 避免本地代理/兼容后端和官方鉴权方式发生冲突
if os.getenv("ANTHROPIC_BASE_URL"):
    os.environ.pop("ANTHROPIC_AUTH_TOKEN", None)

# 创建模型客户端。这里通常连接的是远程 LLM 服务，而不是本机本体模型
client = Anthropic(base_url=os.getenv("ANTHROPIC_BASE_URL"))
# 具体使用哪个模型，由环境变量 MODEL_ID 指定
MODEL = os.environ["MODEL_ID"]

# SYSTEM 提示词告诉模型：你当前是一个 coding agent，工作目录在哪，优先用 bash 解决问题
SYSTEM = f"You are a coding agent at {os.getcwd()}. Use bash to solve tasks. Act, don't explain."

# 这里定义 agent 暴露给模型的全部工具。
# s01 故意只给一个最小工具：bash。
# 模型如果要“动手”，就只能通过调用这个工具来执行 shell 命令。
TOOLS = [{
    "name": "bash",
    "description": "Run a shell command.",
    "input_schema": {
        "type": "object",
        "properties": {"command": {"type": "string"}},
        "required": ["command"],
    },
}]


def run_bash(command: str) -> str:
    # 最基础的危险命令拦截。这里只是演示级防护，不是完整安全方案。
    dangerous = ["rm -rf /", "sudo", "shutdown", "reboot", "> /dev/"]
    if any(d in command for d in dangerous):
        return "Error: Dangerous command blocked"
    try:
        # 真正执行 shell 命令：
        # - shell=True: 允许按 shell 命令解释执行
        # - cwd=os.getcwd(): 在当前项目目录里执行
        # - capture_output=True: 捕获 stdout/stderr
        # - text=True: 返回字符串而不是字节
        # - timeout=120: 最多执行 120 秒
        r = subprocess.run(command, shell=True, cwd=os.getcwd(),
                           capture_output=True, text=True, timeout=120)
        # 合并标准输出和错误输出，方便统一返回给模型
        out = (r.stdout + r.stderr).strip()
        # 限制返回长度，避免一次工具输出过长把上下文撑爆
        return out[:50000] if out else "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Timeout (120s)"


# -- The core pattern: a while loop that calls tools until the model stops --
def agent_loop(messages: list):
    # messages 是整个对话历史。
    # 这个函数不会新建历史，而是在传入的历史上持续追加内容。
    while True:
        # 调用 LLM：
        # - messages: 到目前为止的完整上下文
        # - system: 给模型的全局行为说明
        # - tools: 模型可调用的工具清单
        response = client.messages.create(
            model=MODEL, system=SYSTEM, messages=messages,
            tools=TOOLS, max_tokens=8000,
        )
        # 把模型这一轮的回复加入历史。
        # 注意：response.content 里可能既有普通文本，也有 tool_use 块。
        messages.append({"role": "assistant", "content": response.content})
        # 如果这轮没有触发工具调用，说明模型认为任务已经完成，
        # 或者它只想直接返回文字答案，此时整个 agent loop 结束。
        if response.stop_reason != "tool_use":
            return
        # 如果 stop_reason == "tool_use"，就说明模型这轮要求调用工具。
        # 这里逐个执行工具，并把结果收集起来，再回传给模型。
        results = []
        for block in response.content:
            if block.type == "tool_use":
                # 打印将要执行的命令，便于在终端里观察 agent 的行为
                print(f"\033[33m$ {block.input['command']}\033[0m")
                output = run_bash(block.input["command"])
                # 只在终端预览前 200 个字符，完整内容仍会回传给模型
                print(output[:200])
                # tool_result 必须带上 tool_use_id，
                # 这样模型才能知道这个结果对应的是哪一次工具调用。
                results.append({"type": "tool_result", "tool_use_id": block.id,
                                "content": output})
        # 把工具执行结果作为“用户消息”追加回历史中。
        # 对模型来说，这相当于外部世界把执行结果反馈给了它。
        # 然后 while 循环继续，模型会基于这些结果决定下一步。
        messages.append({"role": "user", "content": results})


if __name__ == "__main__":
    # history 保存整场会话历史，因此用户可以连续提多个问题，
    # 后续问题会继承前面的上下文。
    history = []
    while True:
        try:
            # 读取用户输入
            query = input("\033[36ms01 >> \033[0m")
        except (EOFError, KeyboardInterrupt):
            break
        # 输入 q / exit / 空行时退出程序
        if query.strip().lower() in ("q", "exit", ""):
            break
        # 把用户这一轮问题追加到历史中
        history.append({"role": "user", "content": query})
        # 进入 agent loop，让模型在“思考 -> 调工具 -> 看结果 -> 继续”中循环，
        # 直到它自己停止调用工具。
        agent_loop(history)
        # agent_loop 结束后，history 的最后一条通常是模型最后一次 assistant 回复
        response_content = history[-1]["content"]
        # 只有当最后一条内容是列表时，下面这段打印逻辑才会尝试输出文字块。
        # response.content 在 Anthropic SDK 中通常是内容块列表。
        if isinstance(response_content, list):
            for block in response_content:
                if hasattr(block, "text"):
                    print(block.text)
        print()
