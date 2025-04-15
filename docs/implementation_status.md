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

2. **核心服务**
   - LLM服务实现完成，支持多种模型
   - 主题推荐和分析服务实现完成
   - 提纲生成服务实现完成
   - 论文生成服务实现完成
   - 引用管理服务实现完成
   - 学术搜索服务实现完成，支持多种搜索源和参数配置
   - 多智能体协作框架实现完成

3. **API端点**
   - 主题相关API实现完成
   - 提纲相关API实现完成
   - 论文相关API实现完成
   - 引用相关API实现完成
   - 搜索相关API实现完成，支持多种搜索参数
   - 智能体相关API实现完成

4. **配置系统**
   - 集中化配置管理实现完成
   - 多环境配置支持
   - 敏感信息分离存储

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

2. **多智能体协作优化**
   - 智能体角色定义和优化
   - 智能体协作流程优化

### 待实现功能

1. **数据持久化**
   - 用户项目的保存和恢复
   - 历史记录管理

2. **用户认证系统**
   - 用户注册和登录
   - 权限管理

3. **高级功能**
   - 更多学术数据源集成
   - 更复杂的多智能体协作
   - 领域特定的优化

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
│   │   │       │   ├── topics.py
│   │   │       │   ├── outlines.py
│   │   │       │   ├── papers.py
│   │   │       │   ├── citations.py
│   │   │       │   ├── search.py
│   │   │       │   ├── agents.py
│   │   │       │   ├── tokens.py
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
│   │   │   └── base_class.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── import_record.py
│   │   │   └── statistics.py
│   │   ├── schemas/
│   │   │   ├── topics.py
│   │   │   ├── outlines.py
│   │   │   ├── papers.py
│   │   │   ├── citations.py
│   │   │   ├── search.py
│   │   │   ├── agents.py
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
│   │   │       ├── topics.ts
│   │   │       ├── outlines.ts
│   │   │       ├── papers.ts
│   │   │       ├── citations.ts
│   │   │       ├── search.ts
│   │   │       ├── agents.ts
│   │   │       └── mcp.ts
│   │   ├── components/
│   │   ├── views/
│   │   │   ├── topics/
│   │   │   ├── outlines/
│   │   │   ├── papers/
│   │   │   └── citations/
│   │   ├── types/
│   │   │   ├── topics.ts
│   │   │   ├── outlines.ts
│   │   │   ├── papers.ts
│   │   │   ├── citations.ts
│   │   │   ├── search.ts
│   │   │   ├── agents.ts
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
   - 优化多智能体协作流程
   - 增强学术搜索功能

2. **中期计划**
   - 实现数据持久化
   - 添加用户认证系统
   - 增加更多学术数据源

3. **长期计划**
   - 支持更多语言和学科
   - 集成更多MCP生态工具
   - 开发高级分析功能

## 统一启动脚本

项目提供了统一启动脚本 `start.py`，可以同时启动前端和后端服务，简化了开发和部署过程。

### 脚本功能

- 检查必要的工具和依赖
- 安装前端和后端依赖
- 启动后端 FastAPI 服务
- 启动前端 Vue 开发服务
- 优雅地处理服务关闭

### 脚本参数

- `--venv`：指定 Python 虚拟环境路径
- `--backend-port`：指定后端服务端口（默认为 8000）
- `--frontend-port`：指定前端服务端口（默认为 3000）
- `--install-deps`：安装依赖（默认不安装）

## 日志系统

项目实现了完善的日志系统，使用 loguru 库进行日志管理，支持多种日志级别和输出目标。

### 日志类型

- **应用日志**（`logs/app.log`）：记录应用的一般信息和操作
- **错误日志**（`logs/error.log`）：只记录错误级别的日志
- **LLM 调用日志**（`logs/llm.log`）：记录 LLM 调用相关的信息

### 日志配置

日志配置在 `default.yaml` 文件的 `logging` 部分进行设置，支持以下配置项：

- 日志级别（INFO、DEBUG、WARNING 等）
- 日志格式
- 日志文件路径
- 日志文件大小和备份数量

## 结论

学术论文辅助平台已经完成了大部分核心功能的开发，包括主题推荐、提纲生成、论文生成和引用管理等功能。后端服务和API端点已经基本完成，前端界面正在开发中。项目目前处于可用状态，但仍需完善数据持久化和用户认证等功能，以提供更完整的用户体验。

项目已经实现了统一启动脚本和完善的日志系统，简化了开发和部署过程，提高了系统的可维护性和可靠性。学术搜索功能的增强使用户可以更灵活地配置搜索源和参数，获得更精确的搜索结果。

MCP集成的预留为未来扩展提供了可能性，使平台能够轻松地利用MCP服务器生态中的工具和功能来增强其能力。
