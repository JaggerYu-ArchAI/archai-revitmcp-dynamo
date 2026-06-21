# ArchAI - Revit AI 设计助手

![ArchAI Logo](https://img.shields.io/badge/ArchAI-AI%20for%20BIM-blue)

> 基于Dynamo/Revit平台的AI设计助手，集成大语言模型能力，助力建筑信息模型智能化设计。

[![English](https://img.shields.io/badge/English-README-blue)](README.md)

---

## 🎬 项目演示

[![ArchAI演示视频](https://img.shields.io/badge/Bilibili-%E6%BC%94%E7%A4%BA%E8%A7%86%E9%A2%91-orange)](https://www.bilibili.com/video/BV1s25i6mE4e/?t=107.4&vd_source=2cfdc5cfdf42835fa63915cf5221cc18)

[![视频封面](https://github.com/JaggerYu-ArchAI/archai-revitmcp-dynamo/blob/main/.github/preview.png?raw=true)](https://www.bilibili.com/video/BV1s25i6mE4e/?t=107.4&vd_source=2cfdc5cfdf42835fa63915cf5221cc18)

---

## ✨ 核心功能

### 1. AI智能问答
- 自然语言交互，解答建筑设计相关问题
- 支持上下文理解，多轮对话
- 集成专业知识库

### 2. AI规范助手
- 建筑规范文档查询与解读
- 智能规范匹配与建议
- 实时规范合规性检查

### 3. AI辅助建模
- 基于文本描述自动生成Revit构件
- 参数化设计支持
- 智能几何生成

### 4. MCP工具集成
- Dynamo MCP（Machine Learning Compute Protocol）支持
- 原生适配DeepSeek大模型
- 支持AI24原生语言模型

---

## 🎨 Dynamo可视化界面

ArchAI提供直观的Dynamo节点界面，支持可视化输入输出：

| 节点类型 | 功能说明 |
|---------|---------|
| **AIChat** | AI对话交互节点，支持文本输入输出 |
| **MCPGeneration** | MCP模式下的AI生成节点 |
| **MarkdownViewer** | Markdown格式结果展示 |
| **SpecQuery** | 规范文档查询节点 |
| **SpecList** | 规范列表管理节点 |
| **RandomGeneration** | 随机生成辅助节点 |
| **McpToolWhitelist** | MCP工具白名单管理 |

---

## 📁 项目结构

```
ArchAI/
├── ArchAI_Samples/          # 示例文件
│   ├── AI 智能问答.dyn       # AI问答示例
│   ├── AI 规范助手.dyn       # 规范查询示例
│   ├── AI 辅助建模.dyn       # 辅助建模示例
│   └── AI 辅助建模MCP.dyn    # MCP模式示例
├── dyf/                      # Dynamo节点定义
│   ├── AIChat.dyf            # AI对话节点
│   ├── MCPGeneration.dyf     # MCP生成节点
│   ├── MarkdownViewer.dyf    # Markdown展示节点
│   ├── McpToolWhitelist.dyf  # MCP白名单节点
│   ├── RandomGeneration.dyf  # 随机生成节点
│   ├── SpecList.dyf          # 规范列表节点
│   └── SpecQuery.dyf         # 规范查询节点
├── revit_mcp_tools/          # Revit MCP工具
│   ├── config.py             # 配置管理
│   ├── main.py               # 主入口
│   ├── mcp_handler.py        # MCP处理器
│   └── revit_basic_tools.py  # Revit基础工具
├── specification/            # 规范文档
│   ├── assets/               # 规范文件
│   └── tools/                # 规范工具
└── extra/lib/                # 第三方依赖库
```

---

## 🚀 快速开始

### 安装要求
- Revit 2024
- Dynamo 2.17+

### 安装步骤

1. **下载项目**
   ```bash
   git clone https://github.com/JaggerYu-ArchAI/archai-revitmcp-dynamo.git
   ```

2. **配置API密钥**
   - 编辑 `ArchAI_Samples/api_key.txt` 文件
   - 填入您的 **DeepSeek API KEY**（默认使用DeepSeek大模型）

3. **使用Dynamo播放器打开**
   - 在Revit中打开Dynamo播放器
   - 选择 `ArchAI_Samples/` 目录下的示例文件（`.dyn`）

4. **运行示例**
   - 打开 `AI 智能问答.dyn` 示例
   - 输入问题，点击运行

---

## 🛠️ 技术栈

- **平台**: Autodesk Revit 2024 + Dynamo
- **语言**: Python 3.9
- **AI框架**: DeepSeek API（默认）/ OpenAI API
- **MCP**: Dynamo Machine Learning Compute Protocol

---

## 📦 发布 Release

### 如何创建 GitHub Release

1. **创建标签**
   ```bash
   git tag -a v1.0.0 -m "版本1.0.0发布"
   git push origin v1.0.0
   ```

2. **上传 Release**
   - 访问 GitHub 仓库页面
   - 点击 "Releases" -> "Draft a new release"
   - 选择刚才创建的标签
   - 添加发布说明
   - 上传打包好的项目文件（可选）
   - 点击 "Publish release"

### 打包项目
```bash
# 打包为 zip（排除 .git 和临时文件）
git archive --format=zip --prefix=ArchAI/ HEAD -o ArchAI_v1.0.0.zip
```

---

## 📜 许可证

MIT License

---

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

## 📞 联系

如有问题或建议，请通过以下方式联系：
- GitHub Issues: [提交问题](https://github.com/JaggerYu-ArchAI/archai-revitmcp-dynamo/issues)

---

*Built with ❤️ for BIM Community*
