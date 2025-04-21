# 学术论文辅助平台实现状态

本文档记录了学术论文辅助平台的当前实现状态，包括已完成的功能、架构设计和未来计划。

## 项目概述

学术论文辅助平台是一个基于大型语言模型(LLM)和多智能体协作的系统，旨在帮助用户完成学术论文的选题、提纲生成、草稿撰写和引用管理等任务。平台采用前后端分离架构，后端使用FastAPI，前端使用Vue.js。

## 核心功能

### 1. 主题推荐与分析

- **主题推荐**：基于用户兴趣和学术领域推荐研究主题
- **主题可行性分析**：分析主题的研究价值、难度和创新性
- **主题优化**：根据分析结果提供主题优化建议

### 2. 提纲生成

- **提纲自动生成**：根据研究主题生成论文提纲
- **提纲定制**：支持不同类型论文的提纲结构（研究论文、综述、毕业论文等）
- **提纲优化**：根据用户反馈优化提纲结构和内容

### 3. 论文草稿生成

- **章节内容生成**：根据提纲生成各章节内容
- **内容优化**：提供内容改进建议和修改
- **学术风格调整**：确保内容符合学术写作规范

### 4. 引用管理

- **文献引用**：自动生成符合规范的引用格式
- **参考文献列表**：生成完整的参考文献列表
- **引用格式支持**：支持多种引用格式（APA、MLA、Chicago等）

### 5. 学术搜索

- **文献搜索**：搜索与研究主题相关的学术文献
- **研究趋势分析**：分析研究领域的热点和趋势
- **关键文献推荐**：推荐领域内的重要文献

## 技术架构

### 后端架构

1. **核心服务**
   - `LLMService`：大型语言模型服务，支持多种模型
   - `TopicService`：主题推荐和分析服务
   - `OutlineService`：提纲生成服务
   - `PaperService`：论文生成服务
   - `CitationService`：引用管理服务
   - `AcademicSearchService`：学术搜索服务
   - `AgentService`：多智能体协作服务

2. **API层**
   - RESTful API接口，使用FastAPI框架
   - 按功能模块组织的端点（topics, outlines, papers, citations, search, agents）
   - 请求验证和错误处理

3. **提示词模块**
   - 模块化的提示词设计
   - 按功能分类（topic_prompts, outline_prompts, paper_prompts等）
   - 支持多种语言模型的提示词优化

4. **MCP集成**
   - Model Context Protocol客户端
   - 支持stdio和SSE两种连接方式
   - 工具注册和执行机制
   - 上下文管理

### 前端架构

1. **视图组件**
   - 主题推荐和分析页面
   - 提纲生成和编辑页面
   - 论文生成和编辑页面
   - 引用管理页面
   - 学术搜索页面

2. **API模块**
   - 与后端API对应的调用模块
   - 请求和响应处理
   - 错误处理和重试机制

3. **UI组件**
   - 基于Element Plus的UI组件库
   - 自定义组件（编辑器、提纲树等）
   - 响应式设计

## 当前实现状态

### 已完成功能

1. **基础架构**
   - 后端框架搭建完成
   - 前端框架搭建完成
   - API接口定义完成
   - 提示词模块化完成
   - 统一启动脚本实现完成
   - 日志系统配置完成
   - 数据库设计和集成完成
   - 用户认证系统实现完成

2. **核心服务**
   - LLM服务实现完成，支持多种模型，包括 OpenAI、DeepSeek、Anthropic 和 SiliconFlow 等第三方兼容API
   - 主题推荐和分析服务实现完成
   - 提纲生成服务实现完成
   - 论文生成服务实现完成
   - 引用管理服务实现完成
   - 学术搜索服务实现完成，支持多种搜索源和参数配置
   - 多智能体协作框架实现完成
   - Token管理服务实现完成，支持记录和统计用户的Token使用情况
   - 数据存储架构实现完成，包括数据库存储、Redis缓存和内存存储的合理分层
   - 翻译服务实现完成，支持将英文学术内容翻译成中文
   - 缓存服务实现完成，支持对API请求结果进行缓存，减少重复请求

3. **API端点**
   - 主题相关API实现完成
   - 提纲相关API实现完成
   - 论文相关API实现完成
   - 引用相关API实现完成
   - 搜索相关API实现完成，支持多种搜索参数
   - 智能体相关API实现完成
   - 用户认证API实现完成，支持注册、登录和用户信息管理
   - Token使用记录API实现完成，支持查询和统计Token使用情况
   - 翻译API实现完成，支持内容翻译和批量翻译

4. **配置系统**
   - 集中化配置管理实现完成
   - 多环境配置支持
   - 敏感信息分离存储
   - 数据库配置支持，包括连接池和连接参数

5. **MCP集成**
   - MCP客户端实现完成
   - MCP服务适配器实现完成
   - MCP API端点实现完成
   - MCP测试工具实现完成

### 进行中功能

1. **前端开发**
   - 主题推荐和分析页面开发中
   - 提纲生成和编辑页面开发中
   - 论文生成和编辑页面开发中
   - 用户认证页面开发完成，包括登录和注册页面
   - 用户信息管理页面开发中

2. **LLM服务多模型配置优化**
   - 完善对第三方OpenAI兼容API的支持
   - 优化模型映射机制，增强对不同模型的兼容性
   - 改进错误处理和重试机制
   - 完善模型回退策略

3. **多智能体协作优化**
   - 智能体角色定义和优化
   - 智能体协作流程优化

### 待实现功能

1. **数据存储优化**
   - 智能体记忆持久化
   - 配置管理优化
   - 缓存策略优化

2. **用户管理功能完善**
   - 用户个人资料管理
   - 权限管理系统完善

3. **高级功能**
   - 更多学术数据源集成
   - 更复杂的多智能体协作
   - 领域特定的优化

## LLM服务多模型配置

### 概述

LLM服务是学术论文辅助平台的核心组件，负责与各种大型语言模型进行交互。当前实现支持多种模型和提供商，包括 OpenAI、DeepSeek、Anthropic 和 SiliconFlow 等第三方兼容API。

### 实现组件

1. **LLM服务**
   - 文件：`backend/app/services/llm_service.py`
   - 功能：提供与各种大型语言模型的统一接口
   - 支持模型：OpenAI (gpt-3.5-turbo, gpt-4), DeepSeek (deepseek-chat, deepseek-reasoner), Anthropic (claude-2), SiliconFlow (Qwen/QwQ-32B)
   - 主要方法：acompletion(异步调用), completion(同步调用), acompletion_with_fallbacks(带有回退的异步调用)

2. **模型映射机制**
   - 实现了模型名称映射机制，将简短模型名称映射到LiteLLM需要的完整格式
   - 每个模型都有正确的提供商前缀，如`openai/gpt-3.5-turbo`、`deepseek/deepseek-chat`等

3. **模型特定参数配置**
   - 根据不同模型类型设置特定参数，如API基础URL、API密钥和自定义提供商
   - 对于第三方OpenAI兼容API，使用`custom_llm_provider="openai"`参数指定使用OpenAI兼容的API

4. **错误处理和重试机制**
   - 使用tenacity库实现重试机制，当调用失败时自动重试
   - 实现了模型回退机制，当主模型不可用时尝试其他模型

5. **Token使用记录**
   - 记录每次LLM调用的Token使用情况，包括输入Token、输出Token和总计Token
   - 支持按用户、模型、服务和任务等维度记录和统计Token使用情况

### 配置方法

1. **模型配置**
   - 在`config/default.yaml`文件的`llm`部分进行配置
   - 可以设置默认模型、最大Token数、温度参数等
   - 可以为不同智能体配置不同的模型和参数

2. **API密钥配置**
   - 在`config/.env`文件中配置API密钥和API基础URL
   - 支持多种提供商的API密钥配置，如OPENAI_API_KEY、ANTHROPIC_API_KEY、DEEPSEEK_API_KEY和SILICONFLOW_API_KEY

3. **第三方兼容API配置**
   - 对于第三方OpenAI兼容API，需要配置API基础URL和API密钥
   - 在代码中使用`custom_llm_provider="openai"`参数指定使用OpenAI兼容的API

### 使用方法

1. **异步调用**
   ```python
   response = await llm_service.acompletion(
       model="gpt-3.5-turbo",
       messages=[{"role": "user", "content": "Hello, world!"}],
       max_tokens=100,
       temperature=0.7
   )
   ```

2. **同步调用**
   ```python
   response = llm_service.completion(
       model="deepseek-chat",
       messages=[{"role": "user", "content": "Hello, world!"}],
       max_tokens=100,
       temperature=0.7
   )
   ```

3. **带有回退的调用**
   ```python
   response = await llm_service.acompletion_with_fallbacks(
       messages=[{"role": "user", "content": "Hello, world!"}],
       max_tokens=100,
       temperature=0.7
   )
   ```

### 注意事项

- 对于第三方OpenAI兼容API，需要正确配置API基础URL和自定义提供商参数
- 对于不同的模型提供商，可能需要不同的参数和配置
- 当添加新的模型时，需要在`MODEL_MAPPINGS`字典中添加相应的映射
- 当使用新的模型提供商时，需要在`acompletion`和`completion`方法中添加相应的特定参数处理

## MCP集成详情

### 概述

MCP (Model Context Protocol) 是一个用于模型上下文管理的协议，我们已经在项目中预留了MCP集成接口，以便未来可以利用MCP服务器生态中的工具来增强平台功能。

### 实现组件

1. **MCP客户端**
   - 文件：`backend/app/services/mcp_client.py`
   - 功能：提供与MCP服务器通信的接口
   - 支持连接方式：stdio和SSE
   - 主要方法：创建上下文、更新上下文、执行工具等

2. **MCP配置**
   - 文件：`config/mcp.yaml`
   - 内容：MCP相关配置选项
   - 选项：连接类型、服务器路径、API密钥等

3. **MCP服务适配器**
   - 文件：`backend/app/services/mcp_adapter.py`
   - 功能：将现有服务与MCP集成
   - 主要方法：注册工具、执行论文工作流等

4. **MCP API端点**
   - 文件：`backend/app/api/v1/endpoints/mcp.py`
   - 功能：提供MCP相关的API接口
   - 端点：创建上下文、执行工具、执行论文工作流等

5. **MCP测试工具**
   - 文件：`scripts/mcp_server_mock.py`和`scripts/test_mcp.py`
   - 功能：模拟MCP服务器和测试MCP集成

### 使用方法

1. **启用MCP功能**
   - 修改`config/mcp.yaml`文件，将`mcp.enabled`设置为`true`
   - 配置连接类型、服务器路径等选项

2. **使用stdio连接**
   - 将`mcp.connection_type`设置为`stdio`
   - 将`mcp.server_path`设置为MCP服务器可执行文件的路径

3. **使用SSE连接**
   - 将`mcp.connection_type`设置为`sse`
   - 将`mcp.sse_url`设置为MCP服务器的SSE URL

4. **测试MCP集成**
   - 运行`./scripts/test_mcp.py`脚本测试MCP集成

### 注意事项

- MCP功能默认是禁用的，需要在配置文件中启用
- MCP集成是可选的，不会影响现有功能
- 如果MCP服务器不可用，系统会优雅地降级，继续使用现有功能

## 项目结构

```
edu-kg/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── auth.py
│   │   │       │   ├── users.py
│   │   │       │   ├── topics.py
│   │   │       │   ├── outlines.py
│   │   │       │   ├── papers.py
│   │   │       │   ├── citations.py
│   │   │       │   ├── search.py
│   │   │       │   ├── agents.py
│   │   │       │   ├── tokens.py
│   │   │       │   ├── translation.py
│   │   │       │   └── mcp.py
│   │   │       └── __init__.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logger.py
│   │   │   ├── settings.py
│   │   │   └── prompts/
│   │   │       ├── topic_prompts.py
│   │   │       ├── outline_prompts.py
│   │   │       ├── paper_prompts.py
│   │   │       ├── citation_prompts.py
│   │   │       ├── search_prompts.py
│   │   │       ├── agent_prompts.py
│   │   │       └── base.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── base_class.py
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── topic.py
│   │   │   ├── outline.py
│   │   │   ├── paper.py
│   │   │   ├── citation.py
│   │   │   ├── token_usage.py
│   │   │   ├── import_record.py
│   │   │   └── statistics.py
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   ├── auth.py
│   │   │   ├── topics.py
│   │   │   ├── outlines.py
│   │   │   ├── papers.py
│   │   │   ├── citations.py
│   │   │   ├── search.py
│   │   │   ├── agents.py
│   │   │   ├── token.py
│   │   │   ├── translation.py
│   │   │   └── mcp.py
│   │   ├── services/
│   │   │   ├── llm_service.py
│   │   │   ├── topic_service.py
│   │   │   ├── outline_service.py
│   │   │   ├── paper_service.py
│   │   │   ├── citation_service.py
│   │   │   ├── academic_search_service.py
│   │   │   ├── agent_service.py
│   │   │   ├── statistics_service.py
│   │   │   ├── translation_service.py
│   │   │   ├── cache_service.py
│   │   │   ├── mcp_client.py
│   │   │   └── mcp_adapter.py
│   │   └── main.py
│   └── requirements.txt
├── config/
│   ├── default.yaml
│   ├── mcp.yaml
│   └── .env.example
├── docs/
│   ├── README.md
│   ├── project_design.md
│   ├── implementation_status.md
│   └── user_guide.md
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── index.ts
│   │   │   └── modules/
│   │   │       ├── auth.ts
│   │   │       ├── topics.ts
│   │   │       ├── outlines.ts
│   │   │       ├── papers.ts
│   │   │       ├── citations.ts
│   │   │       ├── search.ts
│   │   │       ├── agents.ts
│   │   │       └── mcp.ts
│   │   ├── components/
│   │   ├── views/
│   │   │   ├── auth/
│   │   │   ├── topics/
│   │   │   ├── outlines/
│   │   │   ├── papers/
│   │   │   └── citations/
│   │   ├── types/
│   │   │   ├── user.ts
│   │   │   ├── auth.ts
│   │   │   ├── topics.ts
│   │   │   ├── outlines.ts
│   │   │   ├── papers.ts
│   │   │   ├── citations.ts
│   │   │   ├── search.ts
│   │   │   ├── agents.ts
│   │   │   ├── translation.ts
│   │   │   └── mcp.ts
│   │   └── App.vue
│   ├── package.json
│   └── vite.config.ts
├── logs/           # 日志目录
│   ├── app.log     # 应用日志
│   ├── error.log   # 错误日志
│   └── llm.log     # LLM调用日志
├── scripts/
│   ├── mcp_server_mock.py
│   └── test_mcp.py
├── start.py      # 统一启动脚本
└── .gitignore
```

## 未来计划

1. **短期计划**
   - 完成前端页面开发
   - 优化LLM服务多模型配置，提高对不同模型的兼容性
   - 优化多智能体协作流程
   - 增强学术搜索功能
   - 完善翻译功能，支持更多语言对
   - 将内存缓存升级为持久化缓存（如Redis）

2. **中期计划**
   - 完善前端与数据库的集成
   - 完善用户管理功能
   - 增加更多学术数据源
   - 实现专业术语库，提高翻译准确性
   - 实现分布式限流机制，在多实例环境中协调API请求

3. **长期计划**
   - 支持更多语言和学科
   - 集成更多MCP生态工具
   - 开发高级分析功能
   - 集成中文学术资源API（如百度学术、万方数据等）
   - 实现智能翻译记忆功能，避免重复翻译相同内容

## 统一启动脚本

项目提供了统一启动脚本 `start.py`，可以同时启动前端和后端服务，简化了开发和部署过程。

### 环境要求

- **Python**：3.10 或更高版本
- **Node.js**：16.0 或更高版本
- **npm**：8.0 或更高版本
- **PostgreSQL**：12.0 或更高版本（如果使用数据库功能）

### 脚本功能

- 检查必要的工具和依赖
- 安装前端和后端依赖
- 启动后端 FastAPI 服务
- 启动前端 Vue 开发服务
- 优雅地处理服务关闭

### 脚本参数

- `--venv`：指定 Python 虚拟环境路径，如果不指定则使用默认的 eduvenv 虚拟环境
- `--backend-port`：指定后端服务端口（默认为 8000）
- `--frontend-port`：指定前端服务端口（默认为 3000）
- `--install-deps`：安装依赖（默认不安装）

## 日志系统

项目实现了完善的日志系统，使用 loguru 库进行日志管理，支持多种日志级别和输出目标。日志系统支持自动切分和压缩，确保日志文件不会无限增长。

### 日志类型

- **应用日志**（`logs/app_{time:YYYY-MM-DD}.log`）：记录应用的一般信息和操作，按日期切分
- **错误日志**（`logs/error_{time:YYYY-MM-DD}.log`）：只记录错误级别的日志，按日期切分
- **LLM 调用日志**（`logs/llm_{time:YYYY-MM-DD}.log`）：记录 LLM 调用相关的信息，按日期切分
- **API 请求日志**（`logs/api_{time:YYYY-MM-DD}.log`）：记录 API 请求相关的信息，按日期切分
- **用户活动日志**（`logs/user_activity_{time:YYYY-MM-DD}.log`）：记录用户活动相关的信息，按日期切分

### 日志配置

日志配置在 `backend/app/core/logger.py` 文件中进行设置，支持以下配置项：

- **日志级别**：支持 INFO、DEBUG、WARNING 等级别，可在 `config/default.yaml` 文件中配置
- **日志格式**：可自定义日志格式，包括时间、级别、模块、函数、行号等信息
- **日志文件路径**：默认存储在项目根目录的 `logs` 目录中
- **日志切分**：支持按日期和文件大小切分，默认当日志文件超过 1MB 时自动切分
- **日志保留**：默认保留 30 天的日志文件，超过时间的日志文件会被自动删除
- **日志压缩**：支持将日志文件压缩为 zip 格式，减少磁盘空间占用

### 日志分类和过滤

日志系统支持根据不同的标签将日志分类到不同的文件中：

- **LLM 日志**：使用 `get_llm_logger` 函数创建的日志器会将日志写入 LLM 日志文件
- **API 日志**：使用 `get_api_logger` 函数创建的日志器会将日志写入 API 日志文件
- **用户活动日志**：使用 `get_user_activity_logger` 函数创建的日志器会将日志写入用户活动日志文件

### 日志使用示例

```python
# 获取一般日志器
from app.core.logger import get_logger
logger = get_logger("my_module")
logger.info("This is an info message")
logger.error("This is an error message")

# 获取 LLM 日志器
from app.core.logger import get_llm_logger
llm_logger = get_llm_logger("llm_service")
llm_logger.info("LLM request: {}", request_data)

# 获取 API 日志器
from app.core.logger import get_api_logger
api_logger = get_api_logger("api_endpoint")
api_logger.info("API request: {}", request.url)
```

## 结论

学术论文辅助平台已经完成了大部分核心功能的开发，包括主题推荐、提纲生成、论文生成和引用管理等功能。后端服务和API端点已经基本完成，前端界面正在开发中。数据库设计和用户认证系统已经实现，使用PostgreSQL数据库进行数据持久化存储，并使用JWT进行用户认证和授权。项目目前处于可用状态，下一步需要完善前端与数据库的集成，将本地存储的数据迁移到数据库中。

项目已经实现了统一启动脚本和完善的日志系统，简化了开发和部署过程，提高了系统的可维护性和可靠性。学术搜索功能的增强使用户可以更灵活地配置搜索源和参数，获得更精确的搜索结果。

新增的翻译功能使平台能够支持将英文学术内容翻译成中文，大大提高了对中文用户的友好性。通过使用大型语言模型进行翻译，确保了学术术语的准确性和翻译质量。同时，实现的缓存服务和学术 API 请求优化显著提高了系统的性能和稳定性，解决了 API 限流问题，减少了重复请求。

MCP集成的预留为未来扩展提供了可能性，使平台能够轻松地利用MCP服务器生态中的工具和功能来增强其能力。随着翻译功能和缓存服务的加入，平台向着更加国际化和高性能的方向发展，为用户提供更加全面和高效的学术论文辅助服务。
