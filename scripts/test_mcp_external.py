"""
测试连接到外部MCP服务器
"""

import asyncio
import sys
import os
import json
import argparse

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.mcp_external_client import mcp_external_client
from backend.app.core.logger import get_logger

logger = get_logger("test_mcp_external")

async def test_mcp_external(server_type: str, **kwargs):
    """测试连接到外部MCP服务器
    
    Args:
        server_type: 服务器类型，支持'stdio'、'http'、'claude'
        **kwargs: 连接参数
    """
    logger.info(f"开始测试连接到外部MCP服务器，类型: {server_type}")
    
    # 连接到外部MCP服务器
    connected = await mcp_external_client.connect_to_server(server_type, **kwargs)
    if not connected:
        logger.error("连接到外部MCP服务器失败")
        return
    
    try:
        # 列出可用的工具
        logger.info("列出可用的工具...")
        tools = await mcp_external_client.list_tools()
        logger.info(f"可用工具: {json.dumps(tools, ensure_ascii=False, indent=2)}")
        
        # 列出可用的资源
        logger.info("列出可用的资源...")
        resources = await mcp_external_client.list_resources()
        logger.info(f"可用资源: {json.dumps(resources, ensure_ascii=False, indent=2)}")
        
        # 列出可用的提示模板
        logger.info("列出可用的提示模板...")
        prompts = await mcp_external_client.list_prompts()
        logger.info(f"可用提示模板: {json.dumps(prompts, ensure_ascii=False, indent=2)}")
        
        # 如果有工具，尝试调用第一个工具
        if tools:
            tool = tools[0]
            tool_name = tool.get("name")
            tool_args = {}
            
            # 获取工具参数
            for param in tool.get("parameters", []):
                param_name = param.get("name")
                param_type = param.get("type")
                
                # 根据参数类型设置默认值
                if param_type == "string":
                    tool_args[param_name] = "test"
                elif param_type == "integer" or param_type == "number":
                    tool_args[param_name] = 1
                elif param_type == "boolean":
                    tool_args[param_name] = True
                elif param_type == "array":
                    tool_args[param_name] = []
                elif param_type == "object":
                    tool_args[param_name] = {}
            
            logger.info(f"调用工具: {tool_name}，参数: {json.dumps(tool_args, ensure_ascii=False)}")
            result = await mcp_external_client.call_tool(tool_name, tool_args)
            logger.info(f"工具调用结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
        # 如果有资源，尝试读取第一个资源
        if resources:
            resource = resources[0]
            uri_template = resource.get("uri_template")
            
            # 替换URI模板中的参数
            uri = uri_template
            for param in resource.get("parameters", []):
                param_name = param.get("name")
                # 简单替换，实际使用时需要根据参数类型设置合适的值
                uri = uri.replace(f"{{{param_name}}}", "test")
            
            logger.info(f"读取资源: {uri}")
            content, mime_type = await mcp_external_client.read_resource(uri)
            logger.info(f"资源内容: {content.decode('utf-8', errors='ignore')[:200]}...")
            logger.info(f"MIME类型: {mime_type}")
        
        # 如果有提示模板，尝试获取第一个提示模板
        if prompts:
            prompt = prompts[0]
            prompt_name = prompt.get("name")
            prompt_args = {}
            
            # 获取提示模板参数
            for param in prompt.get("arguments", []):
                param_name = param.get("name")
                # 简单设置，实际使用时需要根据参数描述设置合适的值
                prompt_args[param_name] = "test"
            
            logger.info(f"获取提示模板: {prompt_name}，参数: {json.dumps(prompt_args, ensure_ascii=False)}")
            result = await mcp_external_client.get_prompt(prompt_name, prompt_args)
            logger.info(f"提示模板内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
        
    except Exception as e:
        logger.error(f"测试连接到外部MCP服务器时出错: {str(e)}")
    finally:
        # 断开连接
        await mcp_external_client.disconnect()
        logger.info("测试完成")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="测试连接到外部MCP服务器")
    parser.add_argument("--type", choices=["stdio", "http", "claude"], default="stdio", help="服务器类型")
    parser.add_argument("--command", help="服务器命令（仅用于stdio类型）")
    parser.add_argument("--args", nargs="*", help="命令行参数（仅用于stdio类型）")
    parser.add_argument("--url", help="服务器URL（仅用于http类型）")
    
    args = parser.parse_args()
    
    kwargs = {}
    if args.type == "stdio" and args.command:
        kwargs["command"] = args.command
        if args.args:
            kwargs["args"] = args.args
    elif args.type == "http" and args.url:
        kwargs["url"] = args.url
    
    asyncio.run(test_mcp_external(args.type, **kwargs))
