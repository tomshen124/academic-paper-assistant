# 开发指南

本文档提供了学术论文辅助平台的开发指南，包括项目结构、扩展方法和最佳实践。

## 项目结构

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py              # 依赖注入
│   │   └── v1/
│   │       ├── endpoints/       # API端点
│   │       │   ├── topics.py    # 主题相关API
│   │       │   ├── outlines.py  # 提纲相关API
│   │       │   ├── papers.py    # 论文相关API
│   │       │   ├── citations.py # 引用相关API
│   │       │   ├── search.py    # 搜索相关API
│   │       │   ├── agents.py    # 智能体相关API
│   │       │   └── tokens.py    # Token管理API
│   │       └── __init__.py      # API路由注册
│   ├── core/
│   │   ├── config.py            # 配置管理
│   │   └── logger.py            # 日志配置
│   ├── schemas/
│   │   ├── topic.py             # 主题相关模型
│   │   ├── outline.py           # 提纲相关模型
│   │   ├── paper.py             # 论文相关模型
│   │   ├── citation.py          # 引用相关模型
│   │   ├── search.py            # 搜索相关模型
│   │   ├── agent.py             # 智能体相关模型
│   │   └── token.py             # Token相关模型
│   ├── services/
│   │   ├── llm_service.py           # LLM服务
│   │   ├── academic_search_service.py # 学术搜索服务
│   │   ├── topic_service.py         # 主题服务
│   │   ├── outline_service.py       # 提纲服务
│   │   ├── paper_service.py         # 论文服务
│   │   ├── citation_service.py      # 引用服务
│   │   ├── agent_service.py         # 智能体服务
│   │   └── token_service.py         # Token管理服务
│   └── utils/
│       └── token_counter.py         # Token计数工具
├── tests/                          # 测试目录
│   └── services/                   # 服务测试
│       ├── test_token_service.py    # Token服务测试
│       ├── test_llm_service.py      # LLM服务测试
│       └── test_agent_service.py    # 智能体服务测试
├── main.py                          # 主应用入口
├── pytest.ini                       # pytest配置
└── requirements.txt                 # 依赖管理
```

## 核心模块说明

### 1. LLM服务 (llm_service.py)

LLM服务是整个系统的核心，负责与大型语言模型的交互。

**主要功能**:
- 支持多种LLM提供商
- 异步和同步调用
- 模型回退机制
- Token使用追踪

**扩展方法**:
- 添加新的模型支持
- 实现更复杂的提示工程
- 添加更多的模型参数控制

### 2. 学术搜索服务 (academic_search_service.py)

学术搜索服务负责从多个学术数据源搜索和获取文献。

**主要功能**:
- 多源学术搜索
- 结果合并与排序
- 文献详情获取
- 研究趋势分析

**扩展方法**:
- 添加新的学术数据源
- 实现更复杂的排序算法
- 添加全文获取功能

### 3. 主题服务 (topic_service.py)

主题服务负责论文主题的推荐、分析和优化。

**主要功能**:
- 基于研究趋势的选题推荐
- 选题可行性分析
- 选题优化

**扩展方法**:
- 添加更多的选题策略
- 实现基于用户历史的个性化推荐
- 添加更详细的可行性分析维度

### 4. 提纲服务 (outline_service.py)

提纲服务负责论文提纲的生成、优化和验证。

**主要功能**:
- 提纲模板管理
- 提纲生成
- 提纲优化
- 逻辑验证

**扩展方法**:
- 添加更多的提纲模板
- 实现更复杂的逻辑验证
- 添加基于学科的专业化提纲生成

### 5. 论文服务 (paper_service.py)

论文服务负责论文内容的生成和优化。

**主要功能**:
- 章节生成
- 全文生成
- 内容改进

**扩展方法**:
- 实现更细粒度的内容生成
- 添加更多的内容优化策略
- 实现基于反馈的迭代优化

### 6. 引用服务 (citation_service.py)

引用服务负责引用和参考文献的管理。

**主要功能**:
- 引用格式化
- 引用提取
- 参考文献生成

**扩展方法**:
- 添加更多的引用格式
- 实现更准确的引用提取
- 添加引用验证功能

### 7. 智能体服务 (agent_service.py)

智能体服务实现了多智能体协作框架。

**主要功能**:
- 智能体协调
- 工作流执行
- 任务规划

**扩展方法**:
- 添加新的智能体角色
- 实现更复杂的协作策略
- 添加基于反馈的自适应规划

### 8. Token管理服务 (token_service.py)

Token管理服务负责追踪和管理LLM的token使用情况。

**主要功能**:
- 记录token使用
- 生成使用统计
- 按模型、服务和日期分类
- 估算成本

**扩展方法**:
- 添加更多的统计维度
- 实现预算控制
- 添加可视化报表

## 扩展指南

### 添加新的智能体

1. 在 `agent_service.py` 中创建新的智能体类:

```python
class NewAgent(Agent):
    """新的智能体角色"""

    def __init__(self, llm_service=None):
        super().__init__("New Agent", "new_role", llm_service)

    async def act(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """实现智能体的行为"""
        # 实现逻辑
        return {"result": "..."}
```

2. 在 `AgentCoordinator` 中注册新智能体:

```python
def __init__(self):
    # ...
    self.register_agent("new_agent", NewAgent(llm_service))
```

### 添加新的服务

1. 在 `services` 目录中创建新的服务文件:

```python
# new_service.py
from app.core.logger import get_logger

logger = get_logger("new_service")

class NewService:
    """新服务"""

    def __init__(self):
        """初始化服务"""
        logger.info("新服务初始化完成")

    async def some_method(self, param: str) -> Dict[str, Any]:
        """实现服务方法"""
        # 实现逻辑
        return {"result": "..."}

# 创建全局实例
new_service = NewService()
```

2. 在 `deps.py` 中添加依赖注入:

```python
from app.services.new_service import new_service

def get_new_service() -> Generator:
    """获取新服务"""
    yield new_service
```

3. 创建相应的API端点:

```python
# endpoints/new_endpoint.py
from fastapi import APIRouter, Depends
from app.services.new_service import NewService
from app.api.deps import get_new_service

router = APIRouter()

@router.post("/method")
async def some_method(
    request: SomeRequest,
    new_service: NewService = Depends(get_new_service)
):
    """API端点"""
    result = await new_service.some_method(request.param)
    return result
```

4. 在 `api/v1/__init__.py` 中注册路由:

```python
from .endpoints import new_endpoint

# ...
api_router.include_router(new_endpoint.router, prefix="/new", tags=["new"])
```

### 集成新的LLM模型

1. 在 `llm_service.py` 中添加新模型支持:

```python
def __init__(self):
    # ...
    # 添加新模型的API密钥环境变量
    if settings.NEW_MODEL_API_KEY:
        os.environ["NEW_MODEL_API_KEY"] = settings.NEW_MODEL_API_KEY

    # 添加新模型到回退列表
    self.fallback_models.append({"model": "new-model"})
```

2. 在 `config.py` 中添加配置选项:

```python
class Settings(BaseSettings):
    # ...
    NEW_MODEL_API_KEY: Optional[str] = Field(None, description="新模型API密钥")
    # ...
```

## 最佳实践

### 错误处理

所有服务方法应该包含适当的错误处理:

```python
async def some_method(self, param: str) -> Dict[str, Any]:
    try:
        # 实现逻辑
        return {"result": "..."}
    except Exception as e:
        logger.error(f"方法执行失败: {str(e)}")
        # 根据情况决定是返回部分结果还是抛出异常
        return {"error": str(e)}
```

### 日志记录

使用日志器记录关键操作和错误:

```python
# 创建日志器
logger = get_logger("module_name")

# 记录信息
logger.info(f"执行操作: {operation}")

# 记录错误
logger.error(f"操作失败: {str(e)}")

# 记录警告
logger.warning(f"潜在问题: {issue}")

# 记录调试信息
logger.debug(f"详细信息: {details}")
```

### 异步编程

尽可能使用异步方法，特别是对于I/O密集型操作:

```python
async def some_method(self, param: str) -> Dict[str, Any]:
    # 并行执行多个异步任务
    tasks = [
        self.task1(param),
        self.task2(param),
        self.task3(param)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 处理结果
    return {"results": results}
```

### Token优化

优化LLM调用的token使用:

1. 使用 `token_counter` 预估token使用量
2. 裁剪过长的输入
3. 使用缓存避免重复请求
4. 分块处理长文本

```python
# 预估token
tokens = token_counter.count_message_tokens(messages, model)
if tokens > max_tokens:
    # 裁剪消息
    messages = self._truncate_messages(messages, max_tokens)

# 缓存结果
cache_key = f"{model}_{hash(json.dumps(messages))}"
if cache_key in self.cache:
    return self.cache[cache_key]

# 分块处理
chunks = self._split_text(text, chunk_size)
results = []
for chunk in chunks:
    result = await self.process_chunk(chunk)
    results.append(result)
```

### 模块化设计

保持服务之间的清晰边界，避免循环依赖:

```python
# 好的做法
class ServiceA:
    def method_a(self):
        # 实现逻辑
        pass

class ServiceB:
    def __init__(self, service_a):
        self.service_a = service_a

    def method_b(self):
        # 使用service_a
        result = self.service_a.method_a()
        # 处理结果
        return result

# 避免循环依赖
# 不要在ServiceA中直接依赖ServiceB
```

## 测试指南

### 单元测试

为每个服务创建单元测试:

```python
# test_service.py
import pytest
from unittest.mock import patch, MagicMock
from app.services.some_service import SomeService

@pytest.fixture
def service():
    return SomeService()

def test_some_method(service):
    # 准备测试数据
    param = "test"

    # 执行方法
    result = service.some_method(param)

    # 验证结果
    assert "result" in result
    assert result["result"] == expected_value

@pytest.mark.asyncio
async def test_async_method(service):
    # 准备测试数据
    param = "test"

    # 执行异步方法
    result = await service.async_method(param)

    # 验证结果
    assert "result" in result
```

### 模拟LLM调用

使用模拟对象测试依赖LLM的服务:

```python
@pytest.mark.asyncio
async def test_llm_dependent_method():
    # 模拟LLM服务
    mock_llm = MagicMock()
    mock_llm.acompletion.return_value = {
        "choices": [{"message": {"content": "模拟响应"}}],
        "usage": {"total_tokens": 100}
    }

    # 创建使用模拟LLM的服务
    service = SomeService(llm_service=mock_llm)

    # 执行方法
    result = await service.llm_dependent_method("test")

    # 验证结果
    assert "content" in result
    assert result["content"] == "模拟响应"

    # 验证LLM调用
    mock_llm.acompletion.assert_called_once()
```

### 集成测试

创建集成测试验证服务之间的交互:

```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_service_integration():
    # 创建实际服务实例
    service_a = ServiceA()
    service_b = ServiceB(service_a)

    # 执行依赖其他服务的方法
    result = await service_b.method_that_uses_service_a("test")

    # 验证结果
    assert result is not None
    # 更多验证...
```

## 性能优化

### 缓存策略

实现适当的缓存机制:

```python
class CachedService:
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1小时
        self.cache_timestamps = {}

    async def get_data(self, key: str) -> Dict[str, Any]:
        # 检查缓存
        if key in self.cache:
            # 检查TTL
            timestamp = self.cache_timestamps.get(key, 0)
            if time.time() - timestamp < self.cache_ttl:
                return self.cache[key]

        # 获取新数据
        data = await self._fetch_data(key)

        # 更新缓存
        self.cache[key] = data
        self.cache_timestamps[key] = time.time()

        return data

    async def _fetch_data(self, key: str) -> Dict[str, Any]:
        # 实际数据获取逻辑
        pass
```

### 批处理请求

对于多个小请求，考虑使用批处理:

```python
async def process_batch(self, items: List[str]) -> List[Dict[str, Any]]:
    # 将项目分组为批次
    batch_size = 10
    batches = [items[i:i+batch_size] for i in range(0, len(items), batch_size)]

    all_results = []
    for batch in batches:
        # 并行处理批次中的项目
        tasks = [self.process_item(item) for item in batch]
        batch_results = await asyncio.gather(*tasks)
        all_results.extend(batch_results)

    return all_results
```

### 异步I/O优化

使用异步I/O减少等待时间:

```python
async def fetch_multiple_resources(self, urls: List[str]) -> List[Dict[str, Any]]:
    async with httpx.AsyncClient() as client:
        # 创建请求任务
        tasks = [client.get(url) for url in urls]

        # 并行执行所有请求
        responses = await asyncio.gather(*tasks)

        # 处理响应
        results = [response.json() for response in responses]

        return results
```
