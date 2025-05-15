"""
测试MCP简化实现
"""

import asyncio
import sys
import os
import json

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.mcp_adapter_simple import mcp_adapter_simple
from backend.app.core.logger import get_logger

logger = get_logger("test_mcp_simple")

async def test_mcp():
    """测试MCP功能"""
    logger.info("开始测试MCP功能")
    
    # 初始化MCP适配器
    success = await mcp_adapter_simple.initialize()
    if not success:
        logger.error("MCP适配器初始化失败")
        return
        
    try:
        # 测试推荐主题
        logger.info("测试推荐主题...")
        topics = await mcp_adapter_simple.recommend_topics(
            user_interests="人工智能在医疗领域的应用",
            academic_field="计算机科学",
            academic_level="master"
        )
        logger.info(f"推荐主题结果: {json.dumps(topics, ensure_ascii=False, indent=2)}")
        
        # 测试生成提纲
        if topics:
            topic = topics[0].get("title", "人工智能在医疗领域的应用")
            logger.info(f"测试生成提纲，主题: {topic}...")
            outline = await mcp_adapter_simple.generate_outline(
                topic=topic,
                academic_field="计算机科学",
                paper_type="research",
                academic_level="master"
            )
            logger.info(f"生成提纲结果: {json.dumps(outline, ensure_ascii=False, indent=2)}")
            
        # 测试获取提示模板
        logger.info("测试获取提示模板...")
        prompt = await mcp_adapter_simple.get_prompt(
            name="topic_brainstorm",
            arguments={
                "user_interests": "人工智能在医疗领域的应用",
                "academic_field": "计算机科学"
            }
        )
        logger.info(f"获取提示模板结果: {json.dumps(prompt, ensure_ascii=False, indent=2)}")
        
        # 测试读取资源
        logger.info("测试读取资源...")
        content, mime_type = await mcp_adapter_simple.read_resource("topics://计算机科学")
        logger.info(f"读取资源结果: {content.decode('utf-8')}, MIME类型: {mime_type}")
        
    except Exception as e:
        logger.error(f"测试MCP功能时出错: {str(e)}")
    finally:
        # 关闭MCP适配器
        await mcp_adapter_simple.shutdown()
        logger.info("测试完成")

if __name__ == "__main__":
    asyncio.run(test_mcp())
