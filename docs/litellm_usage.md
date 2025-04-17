# LiteLLM 使用指南

## 概述

本项目使用 LiteLLM 库来统一处理与各种大型语言模型的交互。通过 LiteLLM 的模型注册和映射功能，我们可以轻松支持多种模型，包括使用 OpenAI 兼容 API 的第三方模型。

## 支持的模型

当前支持以下模型提供商：

1. **OpenAI**
   - `gpt-3.5-turbo`
   - `gpt-4`

2. **DeepSeek**
   - `deepseek-chat`
   - `deepseek-reasoner`

3. **Anthropic**
   - `claude-2`

4. **SiliconFlow**
   - `Qwen/QwQ-32B`

5. **阿里云**
   - `qwen-turbo`
   - `qwen-plus`

## 配置方法

### 环境变量配置

在 `.env` 文件中配置 API 密钥和 API 基础 URL：

```
# OpenAI API密钥
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com/v1  # 可选，如果使用代理或自托管模型

# Anthropic API密钥
ANTHROPIC_API_KEY=your_anthropic_api_key

# DeepSeek API密钥
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_API_URL=https://api.deepseek.com/v1/chat/completions

# SiliconFlow API密钥
SILICONFLOW_API_KEY=your_siliconflow_api_key
SILICONFLOW_API_URL=https://api.siliconflow.com/v1/chat/completions

# 阿里云 API密钥
ALIYUN_API_KEY=your_aliyun_api_key
ALIYUN_API_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 默认模型配置

在 `config/default.yaml` 文件中配置默认模型和参数：

```yaml
llm:
  # 默认模型配置
  default_model: "deepseek-chat"  # 默认使用的模型
  max_tokens: 2000                # 最大token数
  temperature: 0.7                # 温度参数
  top_p: 0.9                      # Top-p参数
  frequency_penalty: 0.0          # 频率惩罚
  presence_penalty: 0.0           # 存在惩罚
```

## 使用方法

### 在代码中使用

```python
from app.services.llm_service import llm_service

# 异步调用
async def example_async():
    response = await llm_service.acompletion(
        model="deepseek-chat",  # 可选，如果不提供则使用默认模型
        messages=[
            {"role": "user", "content": "你好，请介绍一下自己。"}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    # 获取响应内容
    content = response["choices"][0]["message"]["content"]
    print(content)
    
    # 获取token使用情况
    usage = response["usage"]
    print(f"输入tokens: {usage['prompt_tokens']}")
    print(f"输出tokens: {usage['completion_tokens']}")
    print(f"总tokens: {usage['total_tokens']}")

# 同步调用
def example_sync():
    response = llm_service.completion(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "你好，请介绍一下自己。"}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    # 获取响应内容
    content = response["choices"][0]["message"]["content"]
    print(content)

# 带有回退的调用
async def example_with_fallbacks():
    response = await llm_service.acompletion_with_fallbacks(
        messages=[
            {"role": "user", "content": "你好，请介绍一下自己。"}
        ],
        max_tokens=1000,
        temperature=0.7
    )
    
    # 获取响应内容
    content = response["choices"][0]["message"]["content"]
    print(content)
```

## 错误处理

LLM 服务实现了完善的错误处理机制：

1. **重试机制**：使用 tenacity 库实现重试机制，当调用失败时自动重试
2. **异常处理**：捕获并记录所有异常，提供详细的错误信息
3. **回退机制**：当主模型不可用时，自动尝试回退模型

## 日志记录

LLM 服务实现了详细的日志记录：

1. **请求日志**：记录每次 LLM 请求的详细信息，包括模型、消息数等
2. **响应日志**：记录每次 LLM 响应的详细信息，包括 Token 使用情况等
3. **错误日志**：记录所有错误和异常，便于调试和问题排查

## 测试

可以使用 `backend/test_litellm.py` 脚本来测试 LiteLLM 配置是否正确：

```bash
cd edu-kg
python backend/test_litellm.py
```

这个脚本会尝试使用所有可用的模型，并打印响应结果和 Token 使用情况。

## 故障排除

如果遇到问题，请检查以下几点：

1. **API 密钥**：确保已正确设置 API 密钥
2. **API 基础 URL**：确保 API 基础 URL 正确，包括是否需要 `/v1` 后缀
3. **模型名称**：确保使用正确的模型名称
4. **网络连接**：确保可以连接到 API 服务器
5. **日志**：查看日志文件中的详细错误信息

## 添加新的模型提供商

要添加新的模型提供商，需要修改以下文件：

1. `backend/app/services/litellm_config.py`：添加新的模型映射
2. `backend/app/core/config.py`：添加新的配置项
3. `.env.example`：添加新的环境变量示例

例如，要添加一个新的模型提供商 "NewProvider"：

```python
# 在 litellm_config.py 中添加
if settings.NEW_PROVIDER_API_KEY:
    model_mappings.update({
        "new-model": {
            "litellm_params": {
                "model": "openai/gpt-3.5-turbo",  # 使用OpenAI兼容格式
                "api_key": settings.NEW_PROVIDER_API_KEY,
                "api_base": settings.NEW_PROVIDER_API_URL,
                "custom_llm_provider": "openai"  # 指定使用OpenAI兼容API
            }
        }
    })
```

```python
# 在 config.py 中添加
NEW_PROVIDER_API_KEY: Optional[str] = Field(None, description="NewProvider API密钥")
NEW_PROVIDER_API_URL: str = "https://api.newprovider.com/v1"
```

```
# 在 .env.example 中添加
# NewProvider API密钥
NEW_PROVIDER_API_KEY=your_new_provider_api_key
NEW_PROVIDER_API_URL=https://api.newprovider.com/v1
```
