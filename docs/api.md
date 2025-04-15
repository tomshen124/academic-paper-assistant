# API文档

本文档详细说明了学术论文辅助平台的API接口。

## 基础信息

- **基础URL**: `http://localhost:8000`
- **API版本**: v1
- **API前缀**: `/api/v1`

## 认证

目前API不需要认证。未来版本可能会添加认证机制。

## 错误处理

所有API错误返回标准JSON格式:

```json
{
  "message": "错误信息"
}
```

HTTP状态码:
- `200`: 成功
- `400`: 请求错误
- `404`: 资源不存在
- `500`: 服务器错误

## API端点

### 主题API

#### 推荐论文主题

- **URL**: `/api/v1/topics/recommend`
- **方法**: `POST`
- **描述**: 根据用户兴趣和学术领域推荐论文主题

**请求体**:
```json
{
  "user_interests": "人工智能在医疗诊断中的应用",
  "academic_field": "计算机科学",
  "academic_level": "undergraduate"
}
```

**响应**:
```json
[
  {
    "title": "基于深度学习的医学影像诊断系统",
    "research_question": "如何利用深度学习技术提高医学影像诊断的准确性？",
    "feasibility": "中",
    "innovation": "将最新的深度学习模型应用于医学影像分析",
    "methodology": "实验研究，模型比较",
    "resources": "医学影像数据集，计算资源",
    "expected_outcomes": "一个准确率更高的医学影像诊断模型",
    "keywords": ["深度学习", "医学影像", "诊断系统", "人工智能", "计算机辅助诊断"]
  },
  // 更多主题...
]
```

#### 分析主题可行性

- **URL**: `/api/v1/topics/analyze`
- **方法**: `POST`
- **描述**: 分析论文主题的可行性

**请求体**:
```json
{
  "topic": "基于深度学习的医学影像诊断系统",
  "academic_field": "计算机科学",
  "academic_level": "undergraduate"
}
```

**响应**:
```json
{
  "difficulty": "中等难度",
  "resources": "需要医学影像数据集和GPU计算资源",
  "time_estimate": "3-6个月",
  "research_gaps": "现有研究在小样本学习和模型解释性方面存在不足",
  "challenges": "获取高质量标注数据，模型泛化能力",
  "suggestions": "可以缩小研究范围到特定类型的医学影像",
  "overall_score": 7,
  "recommendation": "该主题对于本科生来说具有一定挑战性但可行，建议在导师指导下进行"
}
```

#### 优化论文主题

- **URL**: `/api/v1/topics/refine`
- **方法**: `POST`
- **描述**: 根据反馈优化论文主题

**请求体**:
```json
{
  "topic": "基于深度学习的医学影像诊断系统",
  "feedback": "主题太宽泛，希望专注于肺部CT图像分析",
  "academic_field": "计算机科学",
  "academic_level": "undergraduate"
}
```

**响应**:
```json
{
  "refined_title": "基于深度学习的肺部CT图像肺结节检测系统",
  "research_question": "如何利用深度学习技术提高肺部CT图像中肺结节的检测准确率？",
  "scope": "专注于肺部CT图像中的肺结节检测",
  "methodology": "使用CNN和Transformer模型进行实验比较",
  "keywords": ["深度学习", "肺部CT", "肺结节检测", "计算机辅助诊断", "医学影像分析"],
  "improvements": "将研究范围从一般医学影像缩小到肺部CT图像的肺结节检测，更加具体和可行"
}
```

### 提纲API

#### 生成论文提纲

- **URL**: `/api/v1/outlines/generate`
- **方法**: `POST`
- **描述**: 生成论文提纲

**请求体**:
```json
{
  "topic": "基于深度学习的肺部CT图像肺结节检测系统",
  "paper_type": "实验研究",
  "academic_field": "计算机科学",
  "academic_level": "undergraduate",
  "length": "5000words"
}
```

**响应**:
```json
{
  "title": "基于深度学习的肺部CT图像肺结节检测系统",
  "abstract": "本研究提出了一种基于深度学习的肺部CT图像肺结节检测系统...",
  "keywords": ["深度学习", "肺部CT", "肺结节检测", "计算机辅助诊断", "医学影像分析"],
  "sections": [
    {
      "id": "1",
      "title": "引言",
      "purpose": "介绍研究背景、问题和意义",
      "content_points": ["肺癌早期诊断的重要性", "计算机辅助诊断的发展", "深度学习在医学影像中的应用"],
      "expected_length": "500字",
      "subsections": []
    },
    // 更多章节...
  ]
}
```

#### 优化论文提纲

- **URL**: `/api/v1/outlines/optimize`
- **方法**: `POST`
- **描述**: 优化论文提纲

**请求体**:
```json
{
  "outline": {
    // 原始提纲内容
  },
  "feedback": "方法部分需要更详细，结果分析部分可以增加与现有方法的比较"
}
```

**响应**:
```json
{
  // 优化后的提纲内容
}
```

#### 获取提纲模板

- **URL**: `/api/v1/outlines/templates`
- **方法**: `POST`
- **描述**: 获取提纲模板

**请求体**:
```json
{
  "paper_type": "实验研究",
  "academic_field": "计算机科学"
}
```

**响应**:
```json
[
  {
    "name": "标准实验研究模板",
    "suitable_for": "涉及系统实现和实验评估的研究",
    "structure": [
      {
        "title": "引言",
        "subsections": ["研究背景", "问题陈述", "研究目的", "论文结构"]
      },
      // 更多章节...
    ],
    "features": ["清晰的实验设计", "详细的方法描述", "全面的结果分析"]
  },
  // 更多模板...
]
```

#### 验证提纲逻辑

- **URL**: `/api/v1/outlines/validate`
- **方法**: `POST`
- **描述**: 验证提纲逻辑

**请求体**:
```json
{
  "outline": {
    // 提纲内容
  }
}
```

**响应**:
```json
{
  "completeness": {
    "score": 8,
    "issues": ["缺少研究局限性讨论"],
    "suggestions": ["在讨论部分添加研究局限性章节"]
  },
  "coherence": {
    "score": 9,
    "issues": [],
    "suggestions": []
  },
  "balance": {
    "score": 7,
    "issues": ["方法部分比重过大"],
    "suggestions": ["适当减少方法细节，增加结果分析内容"]
  },
  "methodology": {
    "score": 8,
    "issues": ["评估指标不够全面"],
    "suggestions": ["增加更多评估指标，如特异性和敏感性"]
  },
  "overall_assessment": "整体结构合理，逻辑清晰，但需要在平衡性和完整性方面做些调整",
  "overall_score": 8
}
```

### 论文API

#### 生成论文章节

- **URL**: `/api/v1/papers/sections`
- **方法**: `POST`
- **描述**: 生成论文章节

**请求体**:
```json
{
  "topic": "基于深度学习的肺部CT图像肺结节检测系统",
  "outline": {
    // 提纲内容
  },
  "section_id": "2.1",
  "literature": [
    // 可选的相关文献
  ]
}
```

**响应**:
```json
{
  "section_id": "2.1",
  "title": "相关工作",
  "content": "近年来，深度学习在医学影像分析领域取得了显著进展...",
  "token_usage": {
    "prompt_tokens": 1200,
    "completion_tokens": 800,
    "total_tokens": 2000
  }
}
```

#### 生成完整论文

- **URL**: `/api/v1/papers/generate`
- **方法**: `POST`
- **描述**: 生成完整论文

**请求体**:
```json
{
  "topic": "基于深度学习的肺部CT图像肺结节检测系统",
  "outline": {
    // 提纲内容
  },
  "literature": [
    // 可选的相关文献
  ]
}
```

**响应**:
```json
{
  "title": "基于深度学习的肺部CT图像肺结节检测系统",
  "abstract": "本研究提出了一种基于深度学习的肺部CT图像肺结节检测系统...",
  "keywords": ["深度学习", "肺部CT", "肺结节检测", "计算机辅助诊断", "医学影像分析"],
  "sections": {
    "1": {
      "title": "引言",
      "content": "肺癌是全球死亡率最高的癌症之一..."
    },
    // 更多章节...
  },
  "token_usage": 15000
}
```

#### 改进论文章节

- **URL**: `/api/v1/papers/improve`
- **方法**: `POST`
- **描述**: 改进论文章节

**请求体**:
```json
{
  "topic": "基于深度学习的肺部CT图像肺结节检测系统",
  "section_id": "3.2",
  "current_content": "本研究使用了卷积神经网络进行特征提取...",
  "feedback": "需要更详细地描述网络架构和参数设置",
  "literature": [
    // 可选的相关文献
  ]
}
```

**响应**:
```json
{
  "section_id": "3.2",
  "improved_content": "本研究使用了基于ResNet-50的卷积神经网络进行特征提取。网络架构包括5个卷积块，每个卷积块包含3个卷积层...",
  "token_usage": {
    "prompt_tokens": 1500,
    "completion_tokens": 1000,
    "total_tokens": 2500
  }
}
```

### 引用API

#### 格式化引用

- **URL**: `/api/v1/citations/format`
- **方法**: `POST`
- **描述**: 格式化引用

**请求体**:
```json
{
  "content": "深度学习在医学影像分析中取得了显著进展(Wang, 2020)。根据Smith(2019)的研究...",
  "literature": [
    {
      "title": "Deep Learning in Medical Imaging Analysis",
      "authors": ["Wang, L.", "Zhang, Y."],
      "year": "2020",
      "venue": "Journal of Medical Imaging",
      "url": "https://example.com/paper1"
    },
    // 更多文献...
  ],
  "style": "apa"
}
```

**响应**:
```json
{
  "formatted_content": "深度学习在医学影像分析中取得了显著进展(Wang & Zhang, 2020)。根据Smith和Johnson(2019)的研究...",
  "references": [
    {
      "id": "wang2020",
      "formatted_citation": "(Wang & Zhang, 2020)",
      "original_text": "(Wang, 2020)"
    },
    // 更多引用...
  ],
  "bibliography": [
    "Wang, L., & Zhang, Y. (2020). Deep Learning in Medical Imaging Analysis. Journal of Medical Imaging. https://example.com/paper1",
    // 更多参考文献...
  ]
}
```

#### 提取引用

- **URL**: `/api/v1/citations/extract`
- **方法**: `POST`
- **描述**: 从内容中提取引用

**请求体**:
```json
{
  "content": "深度学习在医学影像分析中取得了显著进展(Wang, 2020)。根据Smith(2019)的研究，卷积神经网络在肺结节检测中表现优异[3]。"
}
```

**响应**:
```json
{
  "citations": [
    {
      "text": "(Wang, 2020)",
      "position": "开头",
      "author": "Wang",
      "year": "2020"
    },
    {
      "text": "Smith(2019)",
      "position": "中间",
      "author": "Smith",
      "year": "2019"
    },
    {
      "text": "[3]",
      "position": "结尾",
      "author": null,
      "year": null
    }
  ],
  "total_count": 3
}
```

#### 生成参考文献列表

- **URL**: `/api/v1/citations/bibliography`
- **方法**: `POST`
- **描述**: 生成参考文献列表

**请求体**:
```json
{
  "literature": [
    {
      "title": "Deep Learning in Medical Imaging Analysis",
      "authors": ["Wang, L.", "Zhang, Y."],
      "year": "2020",
      "venue": "Journal of Medical Imaging",
      "url": "https://example.com/paper1"
    },
    // 更多文献...
  ],
  "style": "apa"
}
```

**响应**:
```json
{
  "bibliography": [
    "Wang, L., & Zhang, Y. (2020). Deep Learning in Medical Imaging Analysis. Journal of Medical Imaging. https://example.com/paper1",
    // 更多参考文献...
  ]
}
```

#### 获取支持的引用样式

- **URL**: `/api/v1/citations/styles`
- **方法**: `GET`
- **描述**: 获取支持的引用样式

**响应**:
```json
{
  "styles": {
    "apa": "APA (American Psychological Association) 第7版",
    "mla": "MLA (Modern Language Association) 第8版",
    "chicago": "Chicago 第17版",
    "harvard": "Harvard 引用格式",
    "ieee": "IEEE 引用格式",
    "vancouver": "Vancouver 引用格式"
  }
}
```

### 搜索API

#### 搜索学术文献

- **URL**: `/api/v1/search/literature`
- **方法**: `POST`
- **描述**: 搜索学术文献

**请求体**:
```json
{
  "query": "deep learning lung nodule detection",
  "limit": 10
}
```

**响应**:
```json
{
  "results": [
    {
      "title": "Deep Learning for Lung Nodule Detection and Classification",
      "authors": ["Smith, J.", "Johnson, R."],
      "year": "2021",
      "abstract": "本研究提出了一种基于深度学习的肺结节检测和分类方法...",
      "url": "https://example.com/paper1",
      "venue": "IEEE Transactions on Medical Imaging",
      "citations": 45,
      "source": "semantic_scholar"
    },
    // 更多结果...
  ],
  "total": 10,
  "query": "deep learning lung nodule detection"
}
```

#### 获取论文详情

- **URL**: `/api/v1/search/paper`
- **方法**: `POST`
- **描述**: 获取论文详情

**请求体**:
```json
{
  "paper_id": "12345",
  "source": "semantic_scholar"
}
```

**响应**:
```json
{
  "title": "Deep Learning for Lung Nodule Detection and Classification",
  "authors": ["Smith, J.", "Johnson, R."],
  "year": "2021",
  "abstract": "本研究提出了一种基于深度学习的肺结节检测和分类方法...",
  "url": "https://example.com/paper1",
  "venue": "IEEE Transactions on Medical Imaging",
  "citations": 45,
  "references": [
    // 参考文献列表
  ],
  "source": "semantic_scholar"
}
```

#### 获取研究趋势

- **URL**: `/api/v1/search/trends`
- **方法**: `POST`
- **描述**: 获取研究趋势

**请求体**:
```json
{
  "field": "医学影像分析"
}
```

**响应**:
```json
{
  "trends": [
    {
      "title": "Recent Advances in Medical Image Analysis with Deep Learning",
      "abstract": "本综述总结了深度学习在医学影像分析领域的最新进展...",
      "year": "2022",
      "url": "https://example.com/paper1",
      "citations": 120
    },
    // 更多趋势...
  ],
  "field": "医学影像分析"
}
```

### 智能体API

#### 执行智能体任务

- **URL**: `/api/v1/agents/task`
- **方法**: `POST`
- **描述**: 执行智能体任务

**请求体**:
```json
{
  "agent_id": "research",
  "task": "分析深度学习在肺结节检测中的应用",
  "context": {
    // 可选的上下文信息
  }
}
```

**响应**:
```json
{
  "result": {
    "research_question": "深度学习如何提高肺结节检测的准确性？",
    "search_terms": ["深度学习", "肺结节检测", "医学影像分析"],
    "research_areas": ["计算机视觉", "医学影像", "深度学习"],
    "methodology": "文献综述和实验比较",
    "expected_outcomes": "对现有方法的系统性评估和未来研究方向的建议"
  }
}
```

#### 执行工作流

- **URL**: `/api/v1/agents/workflow`
- **方法**: `POST`
- **描述**: 执行工作流

**请求体**:
```json
{
  "workflow": [
    {
      "agent": "research",
      "task": "分析深度学习在肺结节检测中的应用"
    },
    {
      "agent": "writing",
      "task": "撰写肺结节检测研究现状章节"
    }
  ],
  "context": {
    // 可选的初始上下文
  }
}
```

**响应**:
```json
{
  "workflow_results": [
    {
      "agent": "research",
      "task": "分析深度学习在肺结节检测中的应用",
      "result": {
        // 研究结果
      }
    },
    {
      "agent": "writing",
      "task": "撰写肺结节检测研究现状章节",
      "result": {
        "content": "近年来，深度学习在肺结节检测领域取得了显著进展..."
      }
    }
  ],
  "final_context": {
    // 最终上下文
  }
}
```

#### 生成任务计划

- **URL**: `/api/v1/agents/plan`
- **方法**: `POST`
- **描述**: 生成任务计划

**请求体**:
```json
{
  "goal": "完成一篇关于深度学习在肺结节检测中应用的综述论文",
  "context": {
    // 可选的上下文信息
  }
}
```

**响应**:
```json
{
  "workflow": [
    {
      "agent": "research",
      "task": "收集和分析深度学习在肺结节检测中的最新研究"
    },
    {
      "agent": "research",
      "task": "识别主要的研究方向和挑战"
    },
    {
      "agent": "writing",
      "task": "撰写研究背景和现状章节"
    },
    {
      "agent": "writing",
      "task": "撰写方法比较章节"
    },
    {
      "agent": "writing",
      "task": "撰写未来展望章节"
    },
    {
      "agent": "editing",
      "task": "优化论文结构和语言表达"
    }
  ]
}
```

#### 规划并执行任务

- **URL**: `/api/v1/agents/plan-and-execute`
- **方法**: `POST`
- **描述**: 规划并执行任务

**请求体**:
```json
{
  "goal": "完成一篇关于深度学习在肺结节检测中应用的综述论文",
  "context": {
    // 可选的上下文信息
  }
}
```

**响应**:
```json
{
  "workflow_results": [
    // 工作流执行结果
  ],
  "final_context": {
    // 最终上下文，包含生成的内容
  }
}
```

### Token管理API

#### 获取token使用情况

- **URL**: `/api/v1/tokens/usage`
- **方法**: `GET`
- **描述**: 获取token使用情况

**查询参数**:
- `include_recent`: 是否包含最近记录 (boolean, 默认false)
- `recent_limit`: 最近记录数量限制 (integer, 默认10)

**响应**:
```json
{
  "summary": {
    "total_usage": {
      "prompt_tokens": 5000,
      "completion_tokens": 2000,
      "total_tokens": 7000,
      "total_cost": 0.14,
      "total_requests": 50
    },
    "averages": {
      "tokens_per_request": 140,
      "cost_per_request": 0.0028,
      "tokens_per_hour": 700,
      "cost_per_hour": 0.014
    },
    "by_model": {
      "gpt-3.5-turbo": {
        "prompt_tokens": 3000,
        "completion_tokens": 1000,
        "total_tokens": 4000,
        "estimated_cost": 0.06,
        "requests": 30
      },
      "gpt-4": {
        "prompt_tokens": 2000,
        "completion_tokens": 1000,
        "total_tokens": 3000,
        "estimated_cost": 0.08,
        "requests": 20
      }
    },
    "by_service": {
      "topic_service": {
        "prompt_tokens": 1000,
        "completion_tokens": 500,
        "total_tokens": 1500,
        "estimated_cost": 0.03,
        "requests": 10
      },
      // 更多服务...
    },
    "by_day": {
      "2023-06-01": {
        "prompt_tokens": 2500,
        "completion_tokens": 1000,
        "total_tokens": 3500,
        "estimated_cost": 0.07,
        "requests": 25
      },
      // 更多日期...
    },
    "uptime_seconds": 3600,
    "uptime_hours": 1
  },
  "recent_records": [
    {
      "timestamp": "2023-06-01T12:00:00.000Z",
      "day": "2023-06-01",
      "model": "gpt-4",
      "service": "paper_service",
      "task": "generate_section",
      "prompt_tokens": 500,
      "completion_tokens": 200,
      "total_tokens": 700,
      "estimated_cost": 0.02
    },
    // 更多记录...
  ]
}
```

#### 导出token使用数据

- **URL**: `/api/v1/tokens/export`
- **方法**: `POST`
- **描述**: 导出token使用数据

**请求体**:
```json
{
  "format": "json"
}
```

**响应**:
```json
{
  "data": "{\"导出的JSON数据\": ...}",
  "format": "json"
}
```

#### 重置token使用数据

- **URL**: `/api/v1/tokens/reset`
- **方法**: `POST`
- **描述**: 重置token使用数据

**响应**:
```json
{
  "message": "Token使用数据已重置",
  "previous_summary": {
    // 之前的使用摘要
  }
}
```
