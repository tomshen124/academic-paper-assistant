# 学术API请求优化

本文档详细说明了学术论文辅助平台对学术API请求的优化措施，包括缓存机制、重试策略和请求限流解决方案。

## 概述

学术论文辅助平台依赖多个外部学术API（如Semantic Scholar、arXiv等）获取学术文献数据。由于这些API通常有请求频率限制，我们实现了一系列优化措施，以提高系统稳定性、减少API调用失败率，并提升用户体验。

## 核心优化措施

1. **缓存机制**：实现内存缓存，减少重复请求
2. **重试策略**：实现智能重试机制，处理临时性故障
3. **请求节流**：控制请求频率，避免触发API限制
4. **错误处理**：改进错误处理，提供更好的用户体验
5. **结果合并**：合并多源搜索结果，减少对单一API的依赖

## 技术实现

### 缓存服务

缓存服务是一个简单但高效的内存缓存实现，用于存储API请求结果，减少重复请求。

```python
class CacheService:
    """简单的内存缓存服务"""
    
    def __init__(self, default_ttl: int = 3600):
        """
        初始化缓存服务
        
        Args:
            default_ttl: 默认缓存过期时间（秒）
        """
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if key not in self.cache:
            return None
            
        cache_item = self.cache[key]
        # 检查是否过期
        if cache_item["expires_at"] < time.time():
            # 过期，删除缓存
            del self.cache[key]
            return None
            
        return cache_item["value"]
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """设置缓存值"""
        if ttl is None:
            ttl = self.default_ttl
            
        expires_at = time.time() + ttl
        self.cache[key] = {
            "value": value,
            "expires_at": expires_at
        }
    
    def cached(self, prefix: str, ttl: Optional[int] = None):
        """
        缓存装饰器，用于缓存异步函数的结果
        
        Args:
            prefix: 缓存键前缀
            ttl: 缓存过期时间（秒）
        """
        def decorator(func: Callable[..., Awaitable[Any]]):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # 生成缓存键
                cache_key = self._generate_key(prefix, args, kwargs)
                
                # 尝试从缓存获取
                cached_value = await self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                # 执行原函数
                result = await func(*args, **kwargs)
                
                # 缓存结果
                await self.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator
```

### 重试策略

为学术API请求实现了智能重试策略，包括指数退避和随机抖动，以处理临时性故障和API限流。

```python
# 发送请求，带增强的重试和延迟机制
max_retries = 5  # 增加重试次数
base_delay = 2  # 初始延迟秒数
max_delay = 60  # 最大延迟秒数

for retry in range(max_retries):
    try:
        # 添加随机延迟，避免多个请求同时发送
        if retry > 0:
            # 指数退避与抖动结合
            delay = min(base_delay * (2 ** retry) + random.uniform(0, 1), max_delay)
            logger.info(f"请求前等待 {delay:.2f} 秒")
            await asyncio.sleep(delay)
        
        # 发送请求
        response = await self.client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # 请求成功，跳出重试循环
        break
        
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        logger.warning(f"请求失败，状态码: {status_code}")
        
        if status_code == 429:  # Too Many Requests
            # 使用更长的延迟
            wait_time = min(base_delay * (2 ** retry) + random.uniform(0, 5), max_delay)
            logger.warning(f"请求限制，等待 {wait_time:.2f} 秒后重试 ({retry+1}/{max_retries})")
            await asyncio.sleep(wait_time)
        elif status_code == 503:  # Service Unavailable
            # 服务不可用，等待后重试
            wait_time = min(base_delay * (2 ** retry) + random.uniform(0, 3), max_delay)
            logger.warning(f"服务不可用，等待 {wait_time:.2f} 秒后重试 ({retry+1}/{max_retries})")
            await asyncio.sleep(wait_time)
        elif retry < max_retries - 1:  # 其他错误，但还有重试机会
            wait_time = min(base_delay * (1.5 ** retry) + random.uniform(0, 1), max_delay)
            logger.warning(f"请求错误，等待 {wait_time:.2f} 秒后重试 ({retry+1}/{max_retries})")
            await asyncio.sleep(wait_time)
        else:
            # 最后一次重试也失败，返回空结果
            logger.error(f"请求失败，所有重试均失败: {str(e)}")
            return []
```

### 缓存装饰器应用

使用缓存装饰器为学术搜索函数添加缓存功能，减少重复请求。

```python
@cache_service.cached(prefix="semantic_scholar_search", ttl=3600)  # 缓存一小时
async def search_semantic_scholar(self, query: str, limit: int = 10, sort_by: str = "relevance", years: str = "all", fields: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """搜索Semantic Scholar"""
    # 函数实现...

@cache_service.cached(prefix="arxiv_search", ttl=3600)  # 缓存一小时
async def search_arxiv(self, query: str, limit: int = 10, sort_by: str = "relevance", categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """搜索arXiv"""
    # 函数实现...

@cache_service.cached(prefix="academic_papers_search", ttl=3600)  # 缓存一小时
async def search_academic_papers(self, query: str, limit: int = None, sources: Optional[List[str]] = None, sort_by: str = None, years: str = None, categories: Optional[List[str]] = None, fields: Optional[List[str]] = None) -> Dict[str, Any]:
    """综合搜索学术论文"""
    # 函数实现...

@cache_service.cached(prefix="paper_details", ttl=86400)  # 缓存24小时
async def get_paper_details(self, paper_id: str, source: str = "semantic_scholar") -> Dict[str, Any]:
    """获取论文详情"""
    # 函数实现...

@cache_service.cached(prefix="research_trends", ttl=86400)  # 缓存24小时
async def get_research_trends(self, field: str) -> List[Dict[str, Any]]:
    """获取研究趋势"""
    # 函数实现...
```

## 优化效果

通过实施上述优化措施，我们取得了以下效果：

1. **减少API调用失败率**：通过智能重试策略，API调用失败率显著降低
2. **提高响应速度**：通过缓存机制，对于重复请求的响应速度大幅提升
3. **减轻API负担**：通过缓存和请求节流，减少了对外部API的请求次数
4. **提升用户体验**：通过更好的错误处理和结果合并，提供了更流畅的用户体验
5. **系统稳定性提高**：整体系统稳定性显著提高，特别是在高负载情况下

## 配置选项

### 缓存配置

缓存服务提供以下配置选项：

- **default_ttl**：默认缓存过期时间（秒），默认为3600秒（1小时）
- **prefix**：缓存键前缀，用于区分不同类型的缓存
- **ttl**：特定缓存的过期时间，可以覆盖默认值

### 重试配置

重试策略提供以下配置选项：

- **max_retries**：最大重试次数，默认为5次
- **base_delay**：初始延迟秒数，默认为2秒
- **max_delay**：最大延迟秒数，默认为60秒

## 使用示例

### 1. 使用缓存装饰器

```python
@cache_service.cached(prefix="my_function", ttl=1800)
async def my_expensive_function(param1, param2):
    # 执行耗时操作
    result = await some_expensive_operation(param1, param2)
    return result
```

### 2. 手动使用缓存

```python
async def get_cached_data(key, fetch_func):
    # 尝试从缓存获取
    cached_data = await cache_service.get(key)
    if cached_data is not None:
        return cached_data
    
    # 获取新数据
    data = await fetch_func()
    
    # 缓存数据
    await cache_service.set(key, data, ttl=3600)
    
    return data
```

### 3. 实现重试逻辑

```python
async def fetch_with_retry(url, max_retries=5):
    base_delay = 2
    max_delay = 60
    
    for retry in range(max_retries):
        try:
            # 添加随机延迟
            if retry > 0:
                delay = min(base_delay * (2 ** retry) + random.uniform(0, 1), max_delay)
                await asyncio.sleep(delay)
            
            # 发送请求
            response = await httpx.AsyncClient().get(url)
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            if retry < max_retries - 1:
                continue
            else:
                raise
```

## 最佳实践

1. **合理设置缓存时间**：根据数据更新频率设置合适的缓存过期时间
2. **使用前缀区分缓存**：为不同类型的数据使用不同的缓存前缀
3. **监控缓存命中率**：定期检查缓存命中率，评估缓存效果
4. **优化重试策略**：根据API特性调整重试次数和延迟时间
5. **实现降级策略**：当所有重试都失败时，提供降级方案，如返回部分结果或缓存数据

## 未来计划

1. **持久化缓存**：将内存缓存升级为持久化缓存（如Redis），支持跨服务实例共享缓存
2. **缓存预热**：实现缓存预热机制，提前缓存热门查询
3. **缓存统计**：添加缓存统计功能，监控缓存使用情况
4. **智能缓存策略**：根据查询频率和数据更新频率动态调整缓存策略
5. **分布式限流**：实现分布式限流机制，在多实例环境中协调API请求
