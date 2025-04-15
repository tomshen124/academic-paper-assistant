# 学术论文辅助平台架构文档

## 项目概述

学术论文辅助平台是一个基于人工智能的系统，旨在帮助研究人员和学生完成学术论文的撰写过程。平台提供主题选择、提纲生成、论文撰写和引用管理等功能。

## 技术栈

- **后端**：FastAPI (Python)
- **前端**：Vue 3 + Element Plus
- **LLM集成**：LiteLLM (支持多种模型如OpenAI, Anthropic等)
- **多智能体协作**：基于CAMEL框架的多智能体系统

## 系统架构

### 后端架构

后端采用模块化设计，主要包含以下组件：

1. **API层**：处理HTTP请求和响应
2. **服务层**：实现业务逻辑
3. **模型层**：定义数据结构
4. **工具层**：提供通用功能

### 前端架构

前端采用Vue 3组件化设计，主要包含以下部分：

1. **视图组件**：用户界面
2. **API模块**：与后端通信
3. **状态管理**：使用Pinia管理应用状态
4. **路由管理**：使用Vue Router管理页面导航

## 配置管理

项目配置采用分层设计，支持不同环境的配置覆盖：

1. **基础配置**：`/config/default.yaml`
2. **环境特定配置**：`/config/development.yaml`, `/config/production.yaml`
3. **敏感信息**：`/config/.env`（不提交到版本控制）

### 配置加载顺序

1. 加载默认配置 (`default.yaml`)
2. 根据环境变量 `ENVIRONMENT` 加载环境特定配置
3. 从 `.env` 文件加载敏感信息和环境变量

## 主要功能模块

### 主题推荐

- **API**: `/api/v1/topics/recommend`
- **服务**: `TopicService`
- **功能**: 根据用户兴趣和学术领域推荐论文主题

### 提纲生成

- **API**: `/api/v1/outlines/generate`
- **服务**: `OutlineService`
- **功能**: 根据论文主题生成结构化提纲

### 论文生成

- **API**: `/api/v1/papers/sections`, `/api/v1/papers/generate`
- **服务**: `PaperService`
- **功能**: 生成论文章节或完整论文

### 引用管理

- **API**: `/api/v1/citations/format`, `/api/v1/citations/extract`
- **服务**: `CitationService`
- **功能**: 提取和格式化引用

### 学术搜索

- **API**: `/api/v1/search/literature`
- **服务**: `AcademicSearchService`
- **功能**: 搜索相关学术文献

### 智能体协作

- **API**: `/api/v1/agents/task`, `/api/v1/agents/plan-and-execute`
- **服务**: `AgentCoordinator`
- **功能**: 协调多个专业智能体完成复杂任务

### Token管理

- **API**: `/api/v1/tokens/usage`
- **服务**: `TokenService`
- **功能**: 跟踪和管理LLM的token使用情况

## 部署架构

### 开发环境

- 后端: `uvicorn main:app --reload`
- 前端: `npm run dev`

### 生产环境

- 后端: Gunicorn + Uvicorn
- 前端: Nginx + 静态文件

## 扩展计划

1. 数据库集成：添加PostgreSQL支持用户数据持久化
2. 用户认证：实现JWT认证系统
3. 高级搜索：增强学术文献搜索功能
4. 协作功能：支持多用户协作编辑论文
