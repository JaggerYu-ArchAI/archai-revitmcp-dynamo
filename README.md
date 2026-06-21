# ArchAI - 基于Dynamo的Revit AI设计助手

![ArchAI Logo](https://img.shields.io/badge/ArchAI-AI%20for%20BIM-blue)

> 基于Dynamo/Revit平台的AI设计助手，集成大语言模型能力，助力建筑信息模型智能化设计。

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
- Revit 2021+
- Dynamo 2.17+
- Python 3.9+

### 安装步骤

1. **下载项目**
   ```bash
   git clone https://github.com/JaggerYu-ArchAI/archai-revitmcp-dynamo.git
   ```

2. **配置API密钥**
   - 编辑 `ArchAI_Samples/api_key.txt` 文件
   - 添加您的AI服务API密钥

3. **加载到Dynamo**
   - 在Dynamo中打开任意示例文件（`.dyn`）
   - 或导入 `dyf/` 目录下的节点

4. **运行示例**
   - 打开 `AI 智能问答.dyn` 示例
   - 输入问题，点击运行

---

## 💡 使用示例

### AI智能问答
```
输入: "如何设计一个符合消防规范的疏散通道？"
输出: "根据GB50016-2014建筑设计防火规范，疏散通道宽度应满足..."
```

### AI辅助建模
```
输入: "生成一个10层办公楼的结构柱布局"
输出: Revit结构柱构件集合
```

---

## 🛠️ 技术栈

- **平台**: Autodesk Revit + Dynamo
- **语言**: Python 3.9
- **AI框架**: OpenAI API / DeepSeek API
- **MCP**: Dynamo Machine Learning Compute Protocol

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
