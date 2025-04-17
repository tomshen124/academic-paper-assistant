# LiteLLM服务使用指南

## 概述

LiteLLM服务是学术论文辅助平台的核心组件，用于统一处理与各种大型语言模型的交互。该服务基于LiteLLM库，支持多种模型和提供商，包括OpenAI、DeepSeek、Anthropic和SiliconFlow等。

通过使用LiteLLM的模型注册和映射功能，我们可以轻松支持各种模型，包括使用OpenAI兼容API的第三方模型。

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
```

### 模型映射配置

模型映射在`backend/app/services/litellm_config.py`文件中配置：

```python
model_mappings = {
    # OpenAI模型
    "gpt-3.5-turbo": {
        "litellm_params": {
            "model": "openai/gpt-3.5-turbo",
            "api_key": settings.OPENAI_API_KEY,
            "api_base": settings.OPENAI_API_BASE
        }
    },
    # 其他模型配置...
}
```

要添加新的模型，只需在此字典中添加新的条目。

## 使用方法

### 异步调用

```python
from app.services.litellm_service import litellm_service

# 异步调用
response = await litellm_service.acompletion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, world!"}],
    max_tokens=100,
    temperature=0.7
)
```

### 同步调用

```python
from app.services.litellm_service import litellm_service

# 同步调用
response = litellm_service.completion(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello, world!"}],
    max_tokens=100,
    temperature=0.7
)
```

### 带有回退的调用

```python
from app.services.litellm_service import litellm_service

# 带有回退的调用
response = await litellm_service.acompletion_with_fallbacks(
    messages=[{"role": "user", "content": "Hello, world!"}],
    max_tokens=100,
    temperature=0.7
)
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

4. **SiliconFlow模型**
   - `Qwen/QwQ-32B`

## 错误处理

LiteLLM服务实现了完善的错误处理机制：

1. **重试机制**：使用tenacity库实现重试机制，当调用失败时自动重试
2. **异常处理**：捕获并记录所有异常，提供详细的错误信息
3. **回退机制**：当主模型不可用时，自动尝试回退模型

## 日志记录

LiteLLM服务实现了详细的日志记录：

1. **请求日志**：记录每次LLM请求的详细信息，包括模型、消息数等
2. **响应日志**：记录每次LLM响应的详细信息，包括Token使用情况等
3. **错误日志**：记录所有错误和异常，便于调试和问题排查

## Token使用记录

LiteLLM服务与Token服务集成，记录每次LLM调用的Token使用情况：

1. **记录维度**：按用户、模型、服务和任务等维度记录Token使用情况
2. **使用统计**：支持统计总Token使用量、平均Token使用量等
3. **成本估算**：根据不同模型的价格，估算Token使用成本

## 添加新模型

要添加新的模型，只需在`backend/app/services/litellm_config.py`文件中的`model_mappings`字典中添加新的条目：

```python
model_mappings = {
    # 现有模型...
    
    # 新模型
    "new-model-name": {
        "litellm_params": {
            "model": "provider/model-name",
            "api_key": settings.NEW_PROVIDER_API_KEY,
            "api_base": settings.NEW_PROVIDER_API_URL,
            # 其他参数...
        }
    }
}
```

然后在`.env`文件中添加相应的API密钥和API基础URL：

```
NEW_PROVIDER_API_KEY=your_new_provider_api_key
NEW_PROVIDER_API_URL=https://api.new-provider.com/v1
```

最后在`app/core/config.py`中添加相应的配置项：

```python
NEW_PROVIDER_API_KEY: Optional[str] = Field(None, description="New Provider API密钥")
NEW_PROVIDER_API_URL: str = "https://api.new-provider.com/v1"
```

## 测试

可以使用`backend/tests/test_litellm_service.py`文件中的测试用例来测试LiteLLM服务：

```bash
# 运行所有测试
pytest backend/tests/test_litellm_service.py

# 运行特定测试
pytest backend/tests/test_litellm_service.py::test_acompletion
```

## 故障排除

如果遇到问题，请检查以下几点：

1. **API密钥**：确保已正确设置API密钥
2. **API基础URL**：确保API基础URL正确，包括是否需要`/v1`后缀
3. **模型名称**：确保使用正确的模型名称
4. **网络连接**：确保可以连接到API服务器
5. **日志**：查看日志文件中的详细错误信息
