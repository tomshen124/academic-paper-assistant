# 学术论文辅助平台数据库设计文档

## 1. 概述

本文档描述了学术论文辅助平台的数据库设计，包括数据库模型、关系和字段说明。

## 2. 数据库模型

### 2.1 用户模型 (User)

用户模型存储系统用户的基本信息和认证信息。

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 用户ID | 主键 |
| email | String | 用户邮箱 | 唯一，非空 |
| username | String | 用户名 | 唯一，非空 |
| hashed_password | String | 密码哈希 | 非空 |
| is_active | Boolean | 是否激活 | 默认为True |
| is_superuser | Boolean | 是否为超级用户 | 默认为False |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### 2.2 主题模型 (Topic)

主题模型存储用户的论文主题信息。

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 主题ID | 主键 |
| user_id | Integer | 用户ID | 外键，非空 |
| title | String | 主题标题 | 非空 |
| research_question | Text | 研究问题 | 可空 |
| academic_field | String | 学术领域 | 非空 |
| academic_level | String | 学术级别 | 非空 |
| feasibility | String | 可行性评估 | 可空 |
| innovation | Text | 创新性评估 | 可空 |
| methodology | Text | 方法论评估 | 可空 |
| resources | Text | 资源评估 | 可空 |
| expected_outcomes | Text | 预期成果 | 可空 |
| keywords | JSON | 关键词列表 | 可空 |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### 2.3 提纲模型 (Outline)

提纲模型存储用户的论文提纲信息。

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 提纲ID | 主键 |
| user_id | Integer | 用户ID | 外键，非空 |
| topic_id | Integer | 主题ID | 外键，非空 |
| title | String | 提纲标题 | 非空 |
| abstract | Text | 摘要 | 可空 |
| keywords | JSON | 关键词列表 | 可空 |
| sections | JSON | 章节结构 | 非空 |
| paper_type | String | 论文类型 | 非空 |
| academic_field | String | 学术领域 | 非空 |
| academic_level | String | 学术级别 | 非空 |
| length | String | 预期长度 | 可空 |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### 2.4 论文模型 (Paper)

论文模型存储用户的论文内容。

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 论文ID | 主键 |
| user_id | Integer | 用户ID | 外键，非空 |
| outline_id | Integer | 提纲ID | 外键，非空 |
| title | String | 论文标题 | 非空 |
| abstract | Text | 摘要 | 可空 |
| keywords | JSON | 关键词列表 | 可空 |
| content | Text | 论文内容 | 非空 |
| status | String | 状态 | 默认为"draft" |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### 2.5 引用模型 (Citation)

引用模型存储论文中的引用信息。

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 引用ID | 主键 |
| paper_id | Integer | 论文ID | 外键，非空 |
| title | String | 引用文献标题 | 非空 |
| authors | JSON | 作者列表 | 可空 |
| year | String | 发表年份 | 可空 |
| source | String | 来源 | 可空 |
| url | String | URL | 可空 |
| citation_text | Text | 格式化的引用文本 | 非空 |
| citation_style | String | 引用样式 | 默认为"apa" |
| created_at | DateTime | 创建时间 | 自动生成 |
| updated_at | DateTime | 更新时间 | 自动更新 |

### 2.6 Token使用记录模型 (TokenUsage)

Token使用记录模型存储用户的Token使用情况。

| 字段名 | 类型 | 说明 | 约束 |
|-------|------|------|------|
| id | Integer | 记录ID | 主键 |
| user_id | Integer | 用户ID | 外键，非空 |
| model | String | 模型名称 | 非空 |
| service | String | 服务名称 | 非空 |
| task | String | 任务名称 | 非空 |
| prompt_tokens | Integer | 输入tokens数量 | 非空 |
| completion_tokens | Integer | 输出tokens数量 | 非空 |
| total_tokens | Integer | 总共tokens数量 | 非空 |
| estimated_cost | Float | 估算成本 | 非空 |
| timestamp | DateTime | 时间戳 | 自动生成 |

## 3. 数据库关系

### 3.1 用户与主题

- 一个用户可以有多个主题
- 关系类型：一对多
- 外键：Topic.user_id -> User.id
- 级联删除：当用户被删除时，相关的主题也会被删除

### 3.2 用户与提纲

- 一个用户可以有多个提纲
- 关系类型：一对多
- 外键：Outline.user_id -> User.id
- 级联删除：当用户被删除时，相关的提纲也会被删除

### 3.3 主题与提纲

- 一个主题可以有多个提纲
- 关系类型：一对多
- 外键：Outline.topic_id -> Topic.id
- 级联删除：当主题被删除时，相关的提纲也会被删除

### 3.4 用户与论文

- 一个用户可以有多个论文
- 关系类型：一对多
- 外键：Paper.user_id -> User.id
- 级联删除：当用户被删除时，相关的论文也会被删除

### 3.5 提纲与论文

- 一个提纲可以有多个论文
- 关系类型：一对多
- 外键：Paper.outline_id -> Outline.id
- 级联删除：当提纲被删除时，相关的论文也会被删除

### 3.6 论文与引用

- 一个论文可以有多个引用
- 关系类型：一对多
- 外键：Citation.paper_id -> Paper.id
- 级联删除：当论文被删除时，相关的引用也会被删除

### 3.7 用户与Token使用记录

- 一个用户可以有多个Token使用记录
- 关系类型：一对多
- 外键：TokenUsage.user_id -> User.id
- 级联删除：当用户被删除时，相关的Token使用记录也会被删除

## 4. 索引设计

为了提高查询性能，我们在以下字段上创建了索引：

1. User.email
2. User.username
3. Topic.user_id
4. Outline.user_id
5. Outline.topic_id
6. Paper.user_id
7. Paper.outline_id
8. Citation.paper_id
9. TokenUsage.user_id
10. TokenUsage.timestamp

## 5. 数据库迁移

数据库迁移使用Alembic工具管理，迁移脚本位于`backend/alembic/versions/`目录下。

## 6. 数据库初始化

数据库初始化脚本位于`backend/app/db/init_db.py`，它会创建所有表并初始化超级用户。

## 7. 数据库配置

数据库配置信息存储在`.env`文件中，包括：

- DATABASE_HOST：数据库主机
- DATABASE_PORT：数据库端口
- DATABASE_USER：数据库用户名
- DATABASE_PASSWORD：数据库密码
- DATABASE_NAME：数据库名称

## 8. 数据库连接池配置

数据库连接池配置存储在`config/default.yaml`文件中，包括：

- pool_size：连接池大小
- max_overflow：最大溢出连接数
- pool_timeout：连接池超时时间
- pool_recycle：连接回收时间
