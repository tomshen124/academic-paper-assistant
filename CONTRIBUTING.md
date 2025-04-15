# 贡献指南

感谢您对学术论文辅助平台的关注！我们欢迎各种形式的贡献，包括但不限于代码贡献、文档改进、问题报告和功能建议。本指南将帮助您了解如何参与项目开发。

## 行为准则

请尊重所有项目参与者，保持专业和友好的交流态度。

## 如何贡献

### 报告问题

如果您发现了 bug 或有改进建议，请通过 GitHub Issues 提交问题报告。提交问题时，请尽可能详细地描述：

1. 问题的具体表现
2. 复现步骤
3. 预期行为
4. 实际行为
5. 环境信息（操作系统、Python 版本、Node.js 版本等）
6. 相关日志或截图

### 提交代码

1. Fork 本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建一个 Pull Request

### 代码风格

- **Python 代码**：遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- **JavaScript/TypeScript 代码**：遵循 [Airbnb JavaScript 风格指南](https://github.com/airbnb/javascript)
- **Vue 组件**：遵循 [Vue 风格指南](https://v3.cn.vuejs.org/style-guide/)

### 提交信息规范

请使用清晰、具体的提交信息，遵循以下格式：

```
<类型>(<范围>): <描述>

[可选的详细描述]

[可选的关闭 issue]
```

类型包括：
- `feat`：新功能
- `fix`：修复 bug
- `docs`：文档更新
- `style`：代码风格调整（不影响代码功能）
- `refactor`：代码重构
- `perf`：性能优化
- `test`：测试相关
- `chore`：构建过程或辅助工具的变动

例如：
```
feat(search): 添加学术搜索源配置功能

- 添加搜索源选择界面
- 实现搜索参数自定义
- 优化搜索结果展示

Closes #123
```

## 开发流程

1. **安装依赖**

```bash
python start.py --install-deps
```

2. **启动开发服务器**

```bash
python start.py
```

3. **运行测试**

```bash
cd backend
pytest
```

4. **构建前端**

```bash
cd frontend
npm run build
```

## 文档贡献

如果您想改进文档，可以编辑 `docs` 目录下的相关文件，或者添加新的文档。文档使用 Markdown 格式编写。

## 功能建议

如果您有新功能建议，请先通过 GitHub Issues 提交功能请求，描述该功能的用途和预期行为。这样可以避免重复工作，并确保新功能符合项目的整体方向。

## 许可证

通过贡献代码，您同意您的贡献将在项目的 MIT 许可证下发布。
