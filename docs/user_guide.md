# 学术论文辅助平台用户指南

本文档提供学术论文辅助平台的安装、配置和使用指南，帮助用户快速上手并充分利用平台功能。

## 目录

- [环境要求](#环境要求)
- [安装指南](#安装指南)
- [启动服务](#启动服务)
- [配置指南](#配置指南)
- [功能使用](#功能使用)
- [常见问题](#常见问题)

## 环境要求

- **操作系统**：支持 Linux、macOS 和 Windows
- **Python**：3.8 或更高版本
- **Node.js**：16.0 或更高版本
- **npm**：8.0 或更高版本
- **内存**：至少 4GB RAM（推荐 8GB 或更多）
- **存储**：至少 2GB 可用空间

## 安装指南

### 1. 克隆代码仓库

```bash
git clone https://github.com/yourusername/edu-kg.git
cd edu-kg
```

### 2. 安装后端依赖

```bash
# 创建并激活虚拟环境
python -m venv eduvenv
source eduvenv/bin/activate  # Linux/macOS
# 或
.\eduvenv\Scripts\activate  # Windows

# 安装依赖
pip install -r backend/requirements.txt
```

### 3. 安装前端依赖

```bash
cd frontend
npm install
cd ..
```

### 4. 配置环境变量

复制示例环境变量文件并进行配置：

```bash
cp config/.env.example config/.env
```

编辑 `.env` 文件，填入必要的配置信息，如 API 密钥等。

## 启动服务

### 使用统一启动脚本

项目提供了统一启动脚本 `start.py`，可以同时启动前端和后端服务：

```bash
# 激活虚拟环境
source eduvenv/bin/activate  # Linux/macOS
# 或
.\eduvenv\Scripts\activate  # Windows

# 启动服务
python start.py
```

启动脚本支持以下参数：

- `--venv`：指定 Python 虚拟环境路径，如果不指定则使用系统 Python
- `--backend-port`：指定后端服务端口，默认为 8000
- `--frontend-port`：指定前端服务端口，默认为 3000
- `--install-deps`：安装依赖（默认不安装）

示例：

```bash
# 使用指定的虚拟环境
python start.py --venv eduvenv

# 指定端口
python start.py --backend-port 8080 --frontend-port 8081

# 安装依赖
python start.py --install-deps
```

### 分别启动服务

也可以分别启动前端和后端服务：

#### 启动后端服务

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 启动前端服务

```bash
cd frontend
npm run dev
```

## 配置指南

### 配置文件结构

项目的配置文件位于 `config` 目录下：

- `default.yaml`：默认配置文件，包含大部分配置项
- `mcp.yaml`：MCP 相关配置
- `.env`：环境变量，包含敏感信息如 API 密钥等

### 主要配置项

#### 1. LLM 配置

在 `default.yaml` 中的 `llm` 部分：

```yaml
llm:
  default_model: "gpt-3.5-turbo"  # 默认使用的模型
  max_tokens: 4096                # 最大 token 数
  temperature: 0.6                # 温度参数
  top_p: 0.9                      # Top-p 参数
  frequency_penalty: 0.0          # 频率惩罚
  presence_penalty: 0.0           # 存在惩罚
  cache_enable: true              # 是否启用缓存
  cache_folder: ".cache/litellm"  # 缓存目录
```

在 `.env` 文件中配置 API 密钥：

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=https://api.openai.com
ANTHROPIC_API_KEY=your_anthropic_api_key
```

#### 2. 学术搜索配置

在 `default.yaml` 中的 `academic_search` 部分：

```yaml
academic_search:
  # 启用的搜索源
  enabled_sources:
    semantic_scholar: true
    arxiv: true
    google_scholar: false  # 默认禁用，容易被IP封禁

  # 默认搜索参数
  default_params:
    limit: 10
    sort_by: "relevance"  # relevance, citations, date
    years: "all"  # all, last_1, last_5, last_10
```

在 `.env` 文件中配置 API 密钥：

```
SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key
```

#### 3. 日志配置

在 `default.yaml` 中的 `logging` 部分：

```yaml
logging:
  level: "INFO"                   # 日志级别
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"  # 日志格式
  file: "logs/app.log"            # 日志文件路径
  max_size: 10485760              # 日志文件最大大小（10MB）
  backup_count: 5                 # 保留的日志文件数量
```

#### 4. MCP 配置

在 `mcp.yaml` 中：

```yaml
mcp:
  enabled: false                  # 是否启用 MCP
  connection_type: "stdio"        # 连接类型：stdio 或 sse
  server_path: ""                 # MCP 服务器可执行文件路径（stdio 模式）
  sse_url: ""                     # MCP 服务器 SSE URL（sse 模式）
  api_key: ""                     # MCP 服务器 API 密钥
```

### 配置优先级

配置项的优先级从高到低为：

1. 命令行参数
2. 环境变量（`.env` 文件）
3. 特定环境配置文件（如 `development.yaml`）
4. 默认配置文件（`default.yaml`）

## 功能使用

### 1. 主题推荐与分析

访问 `/topics` 页面，输入研究领域和兴趣，系统会推荐相关研究主题并分析其可行性。

### 2. 提纲生成

在 `/outlines` 页面，输入研究主题，系统会生成论文提纲，并支持交互式编辑和优化。

### 3. 论文草稿生成

在 `/papers` 页面，选择已有提纲，系统会生成论文草稿，支持分章节生成和编辑。

### 4. 引用管理

在 `/citations` 页面，可以搜索和管理引用，支持多种引用格式。

### 5. 学术搜索

在各功能页面中，可以使用学术搜索功能查找相关文献，支持多种搜索源和过滤条件。

## 常见问题

### 1. 服务启动失败

**问题**：使用 `start.py` 启动服务时报错。

**解决方案**：
- 确保已激活虚拟环境
- 检查端口是否被占用，可以使用 `--backend-port` 和 `--frontend-port` 参数指定其他端口
- 检查日志文件 `logs/app.log` 和 `logs/error.log` 获取详细错误信息

### 2. API 调用失败

**问题**：LLM API 调用失败或返回错误。

**解决方案**：
- 检查 `.env` 文件中的 API 密钥是否正确
- 确认 API 服务是否可用
- 检查网络连接
- 查看 `logs/llm.log` 获取详细错误信息

### 3. 日志文件未生成

**问题**：日志文件未在预期位置生成。

**解决方案**：
- 确保 `logs` 目录存在且有写入权限
- 检查 `default.yaml` 中的日志配置
- 使用绝对路径指定日志文件位置

### 4. 学术搜索无结果

**问题**：学术搜索功能返回空结果。

**解决方案**：
- 检查 `default.yaml` 中的 `academic_search.enabled_sources` 配置
- 确认 Semantic Scholar API 密钥是否正确
- 尝试使用不同的搜索关键词
- 检查网络连接

### 5. MCP 功能不可用

**问题**：MCP 相关功能不可用。

**解决方案**：
- 确认 `mcp.yaml` 中的 `mcp.enabled` 设置为 `true`
- 检查 MCP 服务器是否正确配置和运行
- 查看日志获取详细错误信息
