# 学术论文辅助平台

基于大型语言模型(LLM)和多智能体协作的学术论文辅助平台，帮助用户完成学术论文的选题、提纲生成、草稿撰写和引用管理等任务。

## 项目概述

学术论文辅助平台是一个综合性工具，旨在简化和提升学术写作过程。平台利用先进的大型语言模型和多智能体协作技术，为用户提供从选题到最终草稿的全流程支持。

### 核心功能

- **主题推荐与分析**：基于用户兴趣和学术领域推荐研究主题，分析可行性
- **提纲生成**：自动生成论文提纲，支持不同类型论文的结构定制
- **论文草稿生成**：根据提纲生成各章节内容，确保学术风格
- **引用管理**：自动生成符合规范的引用格式，支持多种引用标准
- **学术搜索**：搜索与研究主题相关的学术文献，支持多种搜索源和参数配置，具有高度稳定性和错误恢复能力
- **用户认证**：支持用户注册、登录和权限管理
- **数据持久化**：将用户数据存储在数据库中，确保数据安全和可靠性
- **Token管理**：跟踪和管理用户的Token使用情况

## 快速开始

### 环境要求

- Python 3.10+
- Node.js 16+
- npm 8+
- PostgreSQL 12+

### 安装

1. 克隆仓库

```bash
git clone https://github.com/yourusername/edu-kg.git
cd edu-kg
```

2. 设置环境

```bash
# 创建并激活虚拟环境
python3.10 -m venv eduvenv
source eduvenv/bin/activate  # Linux/macOS
# 或
.\eduvenv\Scripts\activate  # Windows

# 安装依赖
python3.10 start.py --install-deps

# 配置环境变量
cp config/.env.example config/.env
# 编辑 .env 文件，填入必要的 API 密钥和数据库配置

# 创建数据库
psql -U postgres -c "CREATE DATABASE academic_paper_assistant;"
```

3. 启动服务

```bash
# 使用统一启动脚本
python3.10 start.py
```

访问 http://localhost:3000 开始使用平台。

## 文档

详细文档请参阅 `docs` 目录：

- [用户指南](docs/user_guide.md)：安装、配置和使用指南
- [实现状态](docs/implementation_status.md)：当前功能实现状态
- [数据库设计](docs/database_design.md)：数据库模型和关系设计
- [架构设计](docs/architecture.md)：技术架构文档

最新更新文档：

- [学术搜索功能改进](docs/updates/academic_search_improvements.md)：学术搜索功能的稳定性和错误处理改进
- [管理员密码重置指南](docs/admin_password_reset.md)：管理员密码重置工具的使用方法

## 技术栈

### 后端

- FastAPI：高性能 API 框架
- SQLAlchemy：强大的 ORM 框架
- PostgreSQL：关系型数据库
- Alembic：数据库迁移工具
- LiteLLM：统一的 LLM 接口
- Loguru：高级日志系统
- Pydantic：数据验证和设置管理
- JWT：用户认证和授权

### 前端

- Vue.js：渐进式 JavaScript 框架
- Vue Router：前端路由管理
- Pinia：状态管理库
- Element Plus：UI 组件库
- Axios：HTTP 客户端

## 特色

- **多模型支持**：支持 OpenAI、Anthropic、DeepSeek 等多种 LLM 模型
- **多智能体协作**：基于 CAMEL 框架的多智能体协作系统
- **可配置学术搜索**：支持多种学术搜索源和参数配置，具有高度稳定性和错误恢复能力
- **数据库持久化**：使用 PostgreSQL 数据库存储用户数据和应用状态
- **用户认证系统**：基于 JWT 的安全用户认证和授权
- **Token 使用跟踪**：详细记录和统计用户的 Token 使用情况
- **MCP 集成**：预留 Model Context Protocol 集成接口
- **统一启动脚本**：简化开发和部署流程
- **高级日志系统**：支持日志分类、自动切分、压缩和保留策略
- **智能缓存机制**：优化的缓存服务，支持对API请求结果进行缓存，减少重复请求
- **健壮的错误处理**：全面的错误处理和日志记录，提高系统稳定性

## 数据库架构

本项目使用 PostgreSQL 数据库进行数据持久化存储，主要数据模型包括：

- **用户模型 (User)**：存储用户信息和认证数据
- **主题模型 (Topic)**：存储论文主题信息和分析结果
- **提纲模型 (Outline)**：存储论文提纲结构
- **论文模型 (Paper)**：存储论文内容
- **引用模型 (Citation)**：存储论文引用信息
- **Token使用记录模型 (TokenUsage)**：记录用户的Token使用情况

详细的数据库设计请参考[数据库设计文档](docs/database_design.md)。

## 贡献

欢迎贡献代码、报告问题或提出新功能建议。请参阅 [贡献指南](CONTRIBUTING.md) 了解更多信息。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 致谢

感谢所有为本项目做出贡献的开发者和研究人员。
