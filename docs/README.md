# 学术论文辅助平台

学术论文辅助平台是一个基于人工智能的系统，旨在帮助学生完成从选题到初稿生成的学术论文写作全过程。该平台利用大型语言模型(LLM)、多智能体协作和学术搜索工具，为用户提供智能化的学术写作支持。

## 项目概述

### 核心功能

1. **论文选题辅助**
   - 研究趋势分析
   - 选题推荐
   - 可行性评估
   - 选题优化

2. **提纲生成与优化**
   - 结构模板推荐
   - 提纲自动生成
   - 逻辑关系优化
   - 内容建议

3. **学术文献搜索**
   - 多源学术搜索
   - 文献筛选与排序
   - 关键点提取
   - 研究空白识别

4. **论文初稿生成**
   - 章节内容生成
   - 全文生成
   - 内容优化
   - 学术风格保证

5. **引用与参考文献管理**
   - 引用格式化
   - 参考文献生成
   - 引用提取
   - 多种引用格式支持

6. **多智能体协作**
   - 任务规划
   - 研究智能体
   - 写作智能体
   - 编辑智能体

## 技术架构

### 后端架构

```
[API网关] --> [核心服务模块] --> [LLM集成层] --> [外部API]
                  |
                  v
            [多智能体系统]
```

### 核心服务模块

1. **LLM服务**
   - 使用LiteLLM支持多种模型
   - 模型回退机制
   - Token使用追踪
   - 缓存机制

2. **学术搜索服务**
   - 多源学术搜索
   - 结果合并与排序
   - 文献详情获取
   - 研究趋势分析

3. **主题推荐服务**
   - 基于研究趋势的选题推荐
   - 选题可行性分析
   - 选题优化

4. **提纲生成服务**
   - 提纲模板管理
   - 提纲生成
   - 提纲优化
   - 逻辑验证

5. **论文生成服务**
   - 章节生成
   - 全文生成
   - 内容改进

6. **引用服务**
   - 引用格式化
   - 引用提取
   - 参考文献生成

7. **智能体服务**
   - 智能体协调
   - 工作流执行
   - 任务规划

## API文档

### 主题API

- `POST /api/v1/topics/recommend`: 推荐论文主题
- `POST /api/v1/topics/analyze`: 分析主题可行性
- `POST /api/v1/topics/refine`: 优化论文主题

### 提纲API

- `POST /api/v1/outlines/generate`: 生成论文提纲
- `POST /api/v1/outlines/optimize`: 优化论文提纲
- `POST /api/v1/outlines/templates`: 获取提纲模板
- `POST /api/v1/outlines/validate`: 验证提纲逻辑

### 论文API

- `POST /api/v1/papers/sections`: 生成论文章节
- `POST /api/v1/papers/generate`: 生成完整论文
- `POST /api/v1/papers/improve`: 改进论文章节

### 引用API

- `POST /api/v1/citations/format`: 格式化引用
- `POST /api/v1/citations/extract`: 提取引用
- `POST /api/v1/citations/bibliography`: 生成参考文献列表
- `GET /api/v1/citations/styles`: 获取支持的引用样式

### 搜索API

- `POST /api/v1/search/literature`: 搜索学术文献
- `POST /api/v1/search/paper`: 获取论文详情
- `POST /api/v1/search/trends`: 获取研究趋势

### 智能体API

- `POST /api/v1/agents/task`: 执行智能体任务
- `POST /api/v1/agents/workflow`: 执行工作流
- `POST /api/v1/agents/plan`: 生成任务计划
- `POST /api/v1/agents/plan-and-execute`: 规划并执行任务

### Token管理API

- `GET /api/v1/tokens/usage`: 获取token使用情况
- `POST /api/v1/tokens/export`: 导出token使用数据
- `POST /api/v1/tokens/reset`: 重置token使用数据

## 使用指南

### 环境设置

1. 安装依赖:
```bash
cd backend
pip install -r requirements.txt
```

2. 配置环境变量:
创建 `.env` 文件，设置必要的API密钥:
```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 启动服务

```bash
cd backend
uvicorn main:app --reload
```

### API使用示例

**推荐论文主题**:
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/topics/recommend",
    json={
        "user_interests": "人工智能在医疗诊断中的应用",
        "academic_field": "计算机科学",
        "academic_level": "undergraduate"
    }
)
topics = response.json()
```

**生成论文提纲**:
```python
response = requests.post(
    "http://localhost:8000/api/v1/outlines/generate",
    json={
        "topic": "深度学习在医学影像分析中的应用",
        "paper_type": "综述",
        "academic_field": "计算机科学",
        "academic_level": "undergraduate",
        "length": "5000words"
    }
)
outline = response.json()
```

**生成论文章节**:
```python
response = requests.post(
    "http://localhost:8000/api/v1/papers/sections",
    json={
        "topic": "深度学习在医学影像分析中的应用",
        "outline": outline,
        "section_id": "1"
    }
)
section = response.json()
```

## 多智能体协作

本系统采用多智能体协作框架，通过不同角色的智能体协同工作，提高生成内容的质量。

### 智能体角色

1. **研究智能体**
   - 负责文献搜索和分析
   - 提供研究计划
   - 识别研究空白

2. **写作智能体**
   - 负责内容生成
   - 保证学术风格
   - 整合研究材料

3. **编辑智能体**
   - 负责内容优化
   - 改进语言表达
   - 确保逻辑连贯

### 工作流示例

```
[用户请求] -> [任务规划] -> [研究智能体] -> [写作智能体] -> [编辑智能体] -> [最终结果]
```

## 开发指南

### 项目结构

```
backend/
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── endpoints/
│   │       └── __init__.py
│   ├── core/
│   │   ├── config.py
│   │   └── logger.py
│   ├── schemas/
│   │   ├── topic.py
│   │   ├── outline.py
│   │   ├── paper.py
│   │   ├── citation.py
│   │   ├── search.py
│   │   └── agent.py
│   ├── services/
│   │   ├── llm_service.py
│   │   ├── academic_search_service.py
│   │   ├── topic_service.py
│   │   ├── outline_service.py
│   │   ├── paper_service.py
│   │   ├── citation_service.py
│   │   └── agent_service.py
│   └── utils/
│       └── token_counter.py
├── main.py
└── requirements.txt
```

### 扩展指南

1. **添加新的智能体**:
   - 在 `agent_service.py` 中创建新的智能体类
   - 实现 `act` 方法
   - 在 `AgentCoordinator` 中注册新智能体

2. **添加新的服务**:
   - 在 `services` 目录中创建新的服务文件
   - 在 `deps.py` 中添加依赖注入
   - 创建相应的API端点

3. **集成新的LLM模型**:
   - 在 `llm_service.py` 中添加新模型支持
   - 更新 `config.py` 中的配置选项

## 文档列表

- [architecture.md](architecture.md) - 系统架构文档
- [database_design.md](database_design.md) - 数据库设计文档
- [data_storage.md](data_storage.md) - 数据存储架构文档
- [implementation_status.md](implementation_status.md) - 实现状态文档
- [api.md](api.md) - API文档
- [litellm_service.md](litellm_service.md) - LiteLLM服务文档
- [user_guide.md](user_guide.md) - 用户指南
- [translation_service.md](translation_service.md) - 翻译服务文档
- [translation_guide.md](translation_guide.md) - 翻译功能使用指南
- [api_optimization.md](api_optimization.md) - API优化文档
- [api_optimization_guide.md](api_optimization_guide.md) - API优化实现与使用指南
- [logging_system.md](logging_system.md) - 日志系统文档

## 未来计划

1. **数据存储优化**
   - 智能体记忆持久化
   - 配置管理优化
   - 缓存策略优化

2. **前端开发**
   - 交互式编辑界面
   - 可视化展示
   - 用户友好的工作流

3. **高级功能**
   - 更多学术数据源集成
   - 更复杂的多智能体协作
   - 领域特定的优化

4. **性能优化**
   - 批处理请求
   - 异步任务队列
   - 分布式部署
