#!/usr/bin/env python3
"""
MCP (Model Context Protocol) 集成测试脚本
"""

import asyncio
import json
import sys
import os
import subprocess
from typing import Dict, List, Any, Optional

async def test_mcp_stdio():
    """测试通过stdio连接MCP服务器"""
    print("测试通过stdio连接MCP服务器")
    
    # 启动MCP服务器模拟
    process = await asyncio.create_subprocess_exec(
        "./scripts/mcp_server_mock.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # 创建上下文
    create_context_message = {
        "type": "create_context",
        "id": "test_create_context",
        "config": {
            "name": "测试上下文",
            "description": "这是一个测试上下文",
            "metadata": {
                "test": True,
                "created_by": "test_mcp.py"
            }
        }
    }
    
    # 发送消息
    process.stdin.write((json.dumps(create_context_message) + "\n").encode("utf-8"))
    await process.stdin.drain()
    
    # 读取响应
    response_line = await process.stdout.readline()
    response = json.loads(response_line.decode("utf-8"))
    
    print(f"创建上下文响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
    
    if "context_id" not in response:
        print("创建上下文失败")
        return
    
    context_id = response["context_id"]
    
    # 注册工具
    register_tool_message = {
        "type": "register_tool",
        "id": "test_register_tool",
        "tool_name": "test_tool",
        "tool_config": {
            "name": "test_tool",
            "description": "这是一个测试工具",
            "parameters": {
                "param1": {
                    "type": "string",
                    "description": "参数1"
                },
                "param2": {
                    "type": "integer",
                    "description": "参数2"
                }
            }
        }
    }
    
    # 发送消息
    process.stdin.write((json.dumps(register_tool_message) + "\n").encode("utf-8"))
    await process.stdin.drain()
    
    # 读取响应
    response_line = await process.stdout.readline()
    response = json.loads(response_line.decode("utf-8"))
    
    print(f"注册工具响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
    
    # 执行工具
    execute_tool_message = {
        "type": "execute_tool",
        "id": "test_execute_tool",
        "context_id": context_id,
        "tool_name": "academic_search",
        "tool_params": {
            "query": "人工智能",
            "limit": 3
        }
    }
    
    # 发送消息
    process.stdin.write((json.dumps(execute_tool_message) + "\n").encode("utf-8"))
    await process.stdin.drain()
    
    # 读取响应
    response_line = await process.stdout.readline()
    response = json.loads(response_line.decode("utf-8"))
    
    print(f"执行工具响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
    
    # 获取上下文
    get_context_message = {
        "type": "get_context",
        "id": "test_get_context",
        "context_id": context_id
    }
    
    # 发送消息
    process.stdin.write((json.dumps(get_context_message) + "\n").encode("utf-8"))
    await process.stdin.drain()
    
    # 读取响应
    response_line = await process.stdout.readline()
    response = json.loads(response_line.decode("utf-8"))
    
    print(f"获取上下文响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
    
    # 删除上下文
    delete_context_message = {
        "type": "delete_context",
        "id": "test_delete_context",
        "context_id": context_id
    }
    
    # 发送消息
    process.stdin.write((json.dumps(delete_context_message) + "\n").encode("utf-8"))
    await process.stdin.drain()
    
    # 读取响应
    response_line = await process.stdout.readline()
    response = json.loads(response_line.decode("utf-8"))
    
    print(f"删除上下文响应: {json.dumps(response, ensure_ascii=False, indent=2)}")
    
    # 退出MCP服务器
    exit_message = {
        "type": "exit",
        "id": "test_exit"
    }
    
    # 发送消息
    process.stdin.write((json.dumps(exit_message) + "\n").encode("utf-8"))
    await process.stdin.drain()
    
    # 等待进程结束
    await process.wait()
    
    print("测试完成")

async def main():
    """主函数"""
    # 确保当前目录是项目根目录
    if not os.path.exists("scripts/mcp_server_mock.py"):
        print("请在项目根目录运行此脚本")
        return
    
    # 测试通过stdio连接MCP服务器
    await test_mcp_stdio()

if __name__ == "__main__":
    asyncio.run(main())
