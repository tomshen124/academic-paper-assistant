# 日志系统文档

本文档详细介绍了学术论文辅助平台的日志系统设计和实现。日志系统使用 Loguru 库实现，支持多种日志级别、输出目标、自动切分和压缩功能。

## 日志系统概述

日志系统是应用程序的重要组成部分，用于记录系统运行状态、错误信息和用户活动等。良好的日志系统可以帮助开发者快速定位问题、分析系统性能和监控用户行为。

我们的日志系统具有以下特点：

1. **分类记录**：根据不同的日志类型（应用日志、错误日志、LLM调用日志等）分别记录到不同的文件中
2. **自动切分**：支持按日期和文件大小自动切分日志文件，避免单个日志文件过大
3. **压缩存储**：自动将旧的日志文件压缩为zip格式，减少磁盘空间占用
4. **保留策略**：自动删除超过保留期限的日志文件，避免日志文件无限增长
5. **格式化输出**：支持自定义日志格式，包括时间、级别、模块、函数、行号等信息
6. **多级别支持**：支持DEBUG、INFO、WARNING、ERROR、CRITICAL等多种日志级别
7. **控制台输出**：同时将日志输出到控制台，方便开发调试

## 日志类型

系统支持以下几种类型的日志：

1. **应用日志**（`logs/app_{time:YYYY-MM-DD}.log`）：记录应用的一般信息和操作，按日期切分
2. **错误日志**（`logs/error_{time:YYYY-MM-DD}.log`）：只记录错误级别的日志，按日期切分
3. **LLM调用日志**（`logs/llm_{time:YYYY-MM-DD}.log`）：记录LLM调用相关的信息，按日期切分
4. **API请求日志**（`logs/api_{time:YYYY-MM-DD}.log`）：记录API请求相关的信息，按日期切分
5. **用户活动日志**（`logs/user_activity_{time:YYYY-MM-DD}.log`）：记录用户活动相关的信息，按日期切分

## 日志配置

日志系统的配置在 `backend/app/core/logger.py` 文件中定义。主要配置项包括：

1. **日志级别**：默认为INFO级别，可在配置文件中修改
2. **日志格式**：默认格式包括时间、级别、模块、函数、行号和消息内容
3. **日志文件路径**：默认存储在项目根目录的 `logs` 目录中
4. **日志切分策略**：
   - 按日期切分：使用 `{time:YYYY-MM-DD}` 格式在文件名中包含日期
   - 按大小切分：当日志文件超过1MB时自动切分
5. **日志保留策略**：默认保留30天的日志文件
6. **日志压缩策略**：自动将旧的日志文件压缩为zip格式

## 日志系统实现

### 日志初始化

日志系统在应用启动时通过 `setup_logging()` 函数初始化：

```python
def setup_logging():
    """配置日志系统"""
    # 移除默认的处理器
    logger.remove()

    # 添加控制台输出
    logger.add(
        sys.stdout,
        format=LOG_FORMAT,
        level=settings.LOG_LEVEL,
        colorize=True
    )

    # 添加文件输出
    logger.add(
        LOG_PATH / "app_{time:YYYY-MM-DD}.log",
        format=LOG_FORMAT,
        level=settings.LOG_LEVEL,
        rotation="1 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )

    # 添加错误日志
    logger.add(
        LOG_PATH / "error_{time:YYYY-MM-DD}.log",
        format=LOG_FORMAT,
        level="ERROR",
        rotation="1 MB",
        retention="30 days",
        compression="zip",
        encoding="utf-8"
    )

    # 添加其他类型的日志...
```

### 日志器获取

系统提供了几种不同类型的日志器，用于记录不同类型的日志：

```python
def get_logger(name):
    """获取命名日志器"""
    return logger.bind(name=name)

def get_llm_logger(name):
    """获取LLM日志器"""
    return logger.bind(name=name, llm=True)

def get_api_logger(name):
    """获取API日志器"""
    return logger.bind(name=name, api=True)

def get_user_activity_logger(name):
    """获取用户活动日志器"""
    return logger.bind(name=name, user_activity=True)
```

### 日志拦截器

系统实现了一个日志拦截器，用于将标准库的日志重定向到Loguru：

```python
class InterceptHandler(logging.Handler):
    def emit(self, record):
        # 获取对应的 loguru 级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用者
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )
```

## 日志使用示例

### 基本用法

```python
from app.core.logger import get_logger

logger = get_logger("my_module")
logger.info("这是一条信息日志")
logger.error("这是一条错误日志")
logger.debug("这是一条调试日志")
```

### 记录LLM调用日志

```python
from app.core.logger import get_llm_logger

llm_logger = get_llm_logger("llm_service")
llm_logger.info("LLM请求: {}", request_data)
llm_logger.info("LLM响应: {}", response_data)
```

### 记录API请求日志

```python
from app.core.logger import get_api_logger

api_logger = get_api_logger("api_endpoint")
api_logger.info("API请求: {}", request.url)
api_logger.info("API响应: {}", response.status_code)
```

### 记录用户活动日志

```python
from app.core.logger import get_user_activity_logger

user_logger = get_user_activity_logger("user_service")
user_logger.info("用户 {} 登录", user.username)
user_logger.info("用户 {} 执行操作: {}", user.username, action)
```

## 日志文件管理

### 日志文件位置

所有日志文件都存储在项目根目录的 `logs` 目录中。

### 日志文件命名

日志文件按照以下格式命名：
- 应用日志：`app_{YYYY-MM-DD}.log`
- 错误日志：`error_{YYYY-MM-DD}.log`
- LLM调用日志：`llm_{YYYY-MM-DD}.log`
- API请求日志：`api_{YYYY-MM-DD}.log`
- 用户活动日志：`user_activity_{YYYY-MM-DD}.log`

当日志文件超过1MB时，会自动创建新的日志文件，命名格式为：`{原文件名}.1`、`{原文件名}.2`等。

### 日志文件压缩

超过当前日期的日志文件会被自动压缩为zip格式，命名格式为：`{原文件名}.zip`。

### 日志文件清理

超过30天的日志文件会被自动删除，以避免日志文件占用过多磁盘空间。

## 配置选项

### 日志级别

可以在 `config/default.yaml` 文件中配置日志级别：

```yaml
logging:
  level: INFO  # 可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### 日志格式

可以在 `backend/app/core/logger.py` 文件中修改日志格式：

```python
LOG_FORMAT = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
```

### 日志切分和保留策略

可以在 `backend/app/core/logger.py` 文件中修改日志切分和保留策略：

```python
logger.add(
    LOG_PATH / "app_{time:YYYY-MM-DD}.log",
    format=LOG_FORMAT,
    level=settings.LOG_LEVEL,
    rotation="1 MB",  # 修改切分大小
    retention="30 days",  # 修改保留时间
    compression="zip",
    encoding="utf-8"
)
```

## 最佳实践

1. **使用适当的日志级别**：
   - DEBUG：详细的调试信息，仅在开发环境使用
   - INFO：一般信息，记录正常操作
   - WARNING：警告信息，可能的问题但不影响系统运行
   - ERROR：错误信息，影响功能但不导致系统崩溃
   - CRITICAL：严重错误，可能导致系统崩溃

2. **结构化日志**：使用结构化的日志格式，便于日志分析和处理

3. **避免敏感信息**：不要在日志中记录敏感信息，如密码、API密钥等

4. **使用上下文**：使用日志上下文记录相关信息，如用户ID、请求ID等

5. **异常处理**：在捕获异常时记录详细的异常信息和堆栈跟踪

## 结论

本文档详细介绍了学术论文辅助平台的日志系统设计和实现。通过使用Loguru库和自定义配置，我们实现了一个功能强大、易于使用的日志系统，支持多种日志级别、输出目标、自动切分和压缩功能。这些功能使得系统运行更加稳定，问题定位更加迅速，系统监控更加全面。
