# LLM服务使用指南

## 概述

LLM服务是学术论文辅助平台的核心组件，用于统一处理与各种大型语言模型的交互。该服务基于适配器模式实现，支持多种模型和提供商，包括OpenAI、DeepSeek、Anthropic、阿里云千问和SiliconFlow等。

通过使用适配器模式，我们可以轻松支持各种模型，包括使用OpenAI兼容API的第三方模型。

## 配置方法

### 环境变量配置

在`.env`文件中配置API密钥和API基础URL：

```
# OpenAI配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1

# DeepSeek配置
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.com/v1

# SiliconFlow配置
SILICONFLOW_API_KEY=your_siliconflow_api_key
SILICONFLOW_API_URL=https://api.siliconflow.com/v1

# 阿里云千问配置
ALIYUN_API_KEY=your_aliyun_api_key
ALIYUN_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 模型提供商映射配置

模型提供商映射在`config/default.yaml`文件中配置：

```yaml
llm:
  # 模型提供商映射
  model_providers:
    gpt-3.5-turbo: "openai"        # OpenAI模型
    gpt-4: "openai"                # OpenAI GPT-4模型
    claude-2: "anthropic"          # Anthropic Claude模型
    deepseek-chat: "deepseek"      # DeepSeek聊天模型
    deepseek-reasoner: "deepseek"  # DeepSeek推理模型
    Qwen/QwQ-32B: "siliconflow"    # SiliconFlow平台上的模型
    qwen-turbo: "qwen"             # 阿里云模型
    qwen-plus: "qwen"              # 阿里云模型
    siliconflow: "siliconflow"     # SiliconFlow平台
```

## 使用方法

### 异步调用

```python
from app.services.llm_service import llm_service

# 异步调用
response = await llm_service.acompletion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, world!"}],
    max_tokens=100,
    temperature=0.7
)
```

### 同步调用

```python
from app.services.llm_service import llm_service

# 同步调用
response = llm_service.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, world!"}],
    max_tokens=100,
    temperature=0.7
)
```

### 带有回退的调用

```python
from app.services.llm_service import llm_service

# 带有回退的调用
response = await llm_service.acompletion_with_fallbacks(
    messages=[{"role": "user", "content": "Hello, world!"}],
    max_tokens=100,
    temperature=0.7
)
```

### 流式调用

```python
from app.services.llm_service import llm_service

# 流式调用
async for chunk in llm_service.acompletion_streaming(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, world!"}],
    max_tokens=100,
    temperature=0.7
):
    print(chunk)
```

## 支持的模型

当前支持以下模型：

1. **OpenAI模型**
   - `gpt-3.5-turbo`
   - `gpt-4`

2. **DeepSeek模型**
   - `deepseek-chat`
   - `deepseek-reasoner`

3. **Anthropic模型**
   - `claude-2`

4. **阿里云千问模型**
   - `qwen-turbo`
   - `qwen-plus`

5. **SiliconFlow模型**
   - `Qwen/QwQ-32B`
   - `siliconflow`

## 错误处理

LLM服务实现了完善的错误处理机制：

1. **重试机制**：使用tenacity库实现重试机制，当调用失败时自动重试
2. **异常处理**：捕获并记录所有异常，提供详细的错误信息
3. **回退机制**：当主模型不可用时，自动尝试回退模型

## 日志记录

LLM服务实现了详细的日志记录：

1. **请求日志**：记录每次LLM请求的详细信息，包括模型、消息数等
2. **响应日志**：记录每次LLM响应的详细信息，包括Token使用情况等
3. **错误日志**：记录所有错误和异常，便于调试和问题排查

## Token使用记录

LLM服务与Token服务集成，记录每次LLM调用的Token使用情况：

1. **记录维度**：按用户、模型、服务和任务等维度记录Token使用情况
2. **使用统计**：支持统计总Token使用量、平均Token使用量等
3. **成本估算**：根据不同模型的价格，估算Token使用成本

## 添加新模型

要添加新的模型，需要完成以下步骤：

1. 在`config/default.yaml`中添加新的模型提供商映射
2. 在`backend/app/core/config.py`中添加新的配置项
3. 在`.env.example`中添加新的环境变量示例
4. 如果需要，创建新的适配器实现

例如，要添加一个新的模型提供商 "NewProvider"：

```yaml
# 在 config/default.yaml 中添加
llm:
  model_providers:
    # 现有模型...
    new-model: "new_provider"  # 新模型
```

```python
# 在 backend/app/core/config.py 中添加
NEW_PROVIDER_API_KEY: Optional[str] = Field(None, description="New Provider API密钥")
NEW_PROVIDER_API_URL: str = "https://api.new-provider.com/v1"
```

```
# 在 .env.example 中添加
NEW_PROVIDER_API_KEY=your_new_provider_api_key
NEW_PROVIDER_API_URL=https://api.new-provider.com/v1
```

```python
# 创建新的适配器实现
# backend/app/services/llm/new_provider_adapter.py
from typing import Dict, List, Any, Optional, Union, AsyncGenerator
import litellm
from app.core.logger import get_llm_logger
from app.services.llm.base_adapter import BaseLLMAdapter

logger = get_llm_logger("new_provider_adapter")

class NewProviderAdapter(BaseLLMAdapter):
    """NewProvider适配器，处理NewProvider API调用"""
    
    def __init__(self, api_key: str, api_base: Optional[str] = None):
        self.api_key = api_key
        self.api_base = api_base
        
    # 实现必要的方法...
```

```python
# 在 backend/app/services/llm/adapter_factory.py 中注册新适配器
from app.services.llm.new_provider_adapter import NewProviderAdapter

# 在 create_adapter 方法中添加
elif provider == "new_provider":
    return NewProviderAdapter(
        api_key=config.get("api_key", settings.NEW_PROVIDER_API_KEY),
        api_base=config.get("api_base", settings.NEW_PROVIDER_API_URL)
    )
```

## 故障排除

如果遇到问题，请检查以下几点：

1. **API密钥**：确保已正确设置API密钥
2. **API基础URL**：确保API基础URL正确，包括是否需要`/v1`后缀
3. **模型名称**：确保使用正确的模型名称
4. **网络连接**：确保可以连接到API服务器
5. **日志**：查看日志文件中的详细错误信息
