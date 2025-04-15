# 学术论文辅助平台

基于大型语言模型(LLM)和多智能体协作的学术论文辅助平台，帮助用户完成学术论文的选题、提纲生成、草稿撰写和引用管理等任务。

## 项目概述

学术论文辅助平台是一个综合性工具，旨在简化和提升学术写作过程。平台利用先进的大型语言模型和多智能体协作技术，为用户提供从选题到最终草稿的全流程支持。

### 核心功能

- **主题推荐与分析**：基于用户兴趣和学术领域推荐研究主题，分析可行性
- **提纲生成**：自动生成论文提纲，支持不同类型论文的结构定制
- **论文草稿生成**：根据提纲生成各章节内容，确保学术风格
- **引用管理**：自动生成符合规范的引用格式，支持多种引用标准
- **学术搜索**：搜索与研究主题相关的学术文献，支持多种搜索源和参数配置

## 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- npm 8+

### 安装

1. 克隆仓库

```bash
git clone https://github.com/yourusername/edu-kg.git
cd edu-kg
```

2. 设置环境

```bash
# 创建并激活虚拟环境
python -m venv eduvenv
source eduvenv/bin/activate  # Linux/macOS
# 或
.\eduvenv\Scripts\activate  # Windows

# 安装依赖
python start.py --install-deps

# 配置环境变量
cp config/.env.example config/.env
# 编辑 .env 文件，填入必要的 API 密钥
```

3. 启动服务

```bash
# 使用统一启动脚本
python start.py
```

访问 http://localhost:3000 开始使用平台。

## 文档

详细文档请参阅 `docs` 目录：

- [用户指南](docs/user_guide.md)：安装、配置和使用指南
- [实现状态](docs/implementation_status.md)：当前功能实现状态
- [项目设计](docs/project_design.md)：架构和设计文档

## 技术栈

### 后端

- FastAPI：高性能 API 框架
- LiteLLM：统一的 LLM 接口
- Loguru：高级日志系统
- Pydantic：数据验证和设置管理

### 前端

- Vue.js：渐进式 JavaScript 框架
- Element Plus：UI 组件库
- Axios：HTTP 客户端

## 特色

- **多模型支持**：支持 OpenAI、Anthropic、DeepSeek 等多种 LLM 模型
- **多智能体协作**：基于 CAMEL 框架的多智能体协作系统
- **可配置学术搜索**：支持多种学术搜索源和参数配置
- **MCP 集成**：预留 Model Context Protocol 集成接口
- **统一启动脚本**：简化开发和部署流程

## 贡献

欢迎贡献代码、报告问题或提出新功能建议。请参阅 [贡献指南](CONTRIBUTING.md) 了解更多信息。

## 许可证

本项目采用 [MIT 许可证](LICENSE)。

## 致谢

感谢所有为本项目做出贡献的开发者和研究人员。
