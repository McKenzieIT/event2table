#!/usr/bin/env python3
"""
通过Anthropic API调用Claude并执行文档整合
解决Claude CLI --print模式在cron中挂起的问题
"""

import os
import sys
import json
import re
import subprocess
import requests
from pathlib import Path
from datetime import datetime

# 配置
API_KEY = "d897d6ccfec24181a55049a5b59cd2c8.L3EdkD3YdLog6TPc"
API_BASE_URL = "https://open.bigmodel.cn/api/anthropic/v1/messages"
PROJECT_DIR = Path("/Users/mckenzie/Documents/event2table")
LOG_FILE = PROJECT_DIR / "logs" / "update-docs-scheduled.log"
ERROR_LOG = PROJECT_DIR / "logs" / "update-docs-scheduled-error.log"

# 完整任务prompt
TASK_PROMPT = """请使用update-docs skill执行以下文档整合任务：

1. 扫描docs/目录下的所有markdown文件
2. 识别重复或相似的文档
3. 将重复文档中的关键经验提取到docs/lessons-learned/对应的经验文档中
4. 将处理过的旧文档归档到docs/archive/目录下
5. 更新CLAUDE.md中的经验文档索引

重要：
- 不能因为token或时间限制而忽略重要经验
- 必须完整执行所有步骤
- 保留所有有价值的文档内容

请直接开始执行，不要只给建议。使用Bash工具来操作文件。"""

def log(message, error=False):
    """记录日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_msg = f"[{timestamp}] {message}\n"
    print(log_msg, end="")

    log_file = ERROR_LOG if error else LOG_FILE
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_msg)

def call_claude_api():
    """调用Claude API"""
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    data = {
        "model": "glm-4.7",
        "max_tokens": 8192,
        "messages": [
            {
                "role": "user",
                "content": TASK_PROMPT
            }
        ],
        "tools": [
            {
                "name": "Bash",
                "description": "Execute bash commands to perform file operations",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute"
                        }
                    },
                    "required": ["command"]
                }
            }
        ]
    }

    try:
        log("调用Claude API...")
        response = requests.post(API_BASE_URL, headers=headers, json=data, timeout=300)
        response.raise_for_status()
        result = response.json()
        return result
    except Exception as e:
        log(f"API调用失败: {e}", error=True)
        raise

def execute_tool_use(tool_use):
    """执行工具调用"""
    function_name = tool_use.get("name")
    function_input = tool_use.get("input", {})

    if function_name == "Bash":
        command = function_input.get("command")
        log(f"执行命令: {command}")

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=PROJECT_DIR
            )

            output = result.stdout or result.stderr
            # 截断过长的输出
            if len(output) > 10000:
                output = output[:10000] + "\n... (输出过长，已截断)"
            log(f"命令输出: {output[:200]}...")

            # 返回tool_result消息
            return {
                "role": "user",
                "content": output or "命令执行成功"
            }
        except Exception as e:
            log(f"命令执行失败: {e}", error=True)
            return {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.get("id"),
                        "content": f"错误: {str(e)}"
                    }
                ]
            }

    return None

def process_conversation():
    """处理对话并执行工具调用"""
    headers = {
        "x-api-key": API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    messages = [
        {
            "role": "user",
            "content": TASK_PROMPT
        }
    ]

    max_iterations = 10  # 防止无限循环
    iteration = 0
    max_message_history = 6  # 限制消息历史大小，防止token过多

    while iteration < max_iterations:
        iteration += 1
        log(f"=== 迭代 {iteration} ===")

        try:
            # 调用API
            log(f"准备API请求，消息数: {len(messages)}")
            data = {
                "model": "glm-4.7",
                "max_tokens": 8192,
                "messages": messages,
                "tools": [
                    {
                        "name": "Bash",
                        "description": "Execute bash commands",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "command": {"type": "string"}
                            },
                            "required": ["command"]
                        }
                    }
                ]
            }

            log(f"发送API请求（迭代 {iteration}）...")
            response = requests.post(API_BASE_URL, headers=headers, json=data, timeout=60)
            response.raise_for_status()
            result = response.json()
            log(f"API响应收到，状态码: {response.status_code}")

            # 处理响应
            assistant_message = {
                "role": "assistant",
                "content": result.get("content", [])
            }
            messages.append(assistant_message)

            # 检查是否有工具调用
            tool_calls = [block for block in result.get("content", []) if block.get("type") == "tool_use"]

            if not tool_calls:
                log("没有更多工具调用，任务完成")
                break

            # 执行所有工具调用
            for tool_use in tool_calls:
                result_message = execute_tool_use(tool_use)
                if result_message:
                    messages.append(result_message)

            # 限制消息历史大小（保留最近的消息，成对保留）
            # messages格式: [user, assistant, user(tool_result), assistant, ...]
            if len(messages) > max_message_history:
                # 确保保留完整的对话对
                messages = messages[-max_message_history:]
                log(f"消息历史已修剪到 {len(messages)} 条")

        except requests.exceptions.Timeout as e:
            log(f"API请求超时（迭代 {iteration}）: {e}", error=True)
            log("超时后继续执行...", error=True)
            # 超时后不中断，继续下一次迭代或结束
            break
        except requests.exceptions.RequestException as e:
            log(f"API请求失败（迭代 {iteration}）: {e}", error=True)
            # 尝试获取响应内容
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.text[:500]
                    log(f"API错误详情: {error_detail}", error=True)
                except:
                    pass
            break
        except Exception as e:
            log(f"处理失败（迭代 {iteration}）: {e}", error=True)
            import traceback
            log(traceback.format_exc(), error=True)
            break

    log(f"=== 完成，共 {iteration} 次迭代 ===")

def main():
    """主函数"""
    log("=" * 50)
    log("🚀 开始执行Claude API文档整合任务")
    log("=" * 50)

    try:
        process_conversation()

        log("=" * 50)
        log("✅ 文档整合任务完成")
        log("=" * 50)

        return 0

    except Exception as e:
        log(f"❌ 任务执行失败: {e}", error=True)
        import traceback
        log(traceback.format_exc(), error=True)
        return 1

if __name__ == "__main__":
    sys.exit(main())
