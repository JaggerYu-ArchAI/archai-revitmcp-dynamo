
# ArchAI - Revit AI Design Assistant for Dynamo

![ArchAI Logo](https://img.shields.io/badge/ArchAI-AI%20for%20BIM-blue)

> An AI-powered design assistant for Revit, integrated with large language models to enhance BIM workflows.

[![中文](https://img.shields.io/badge/中文-README-blue)](README_zh.md)

---

## 📖 Introduction

Based on Dynamo/Revit platform, ArchAI is an AI design assistant that integrates large language model capabilities to enhance Building Information Modeling (BIM) workflows.

---

## 🎬 Demo Video

[![ArchAI Demo Video](https://img.shields.io/badge/Bilibili-Demo%20Video-orange)](https://www.bilibili.com/video/BV1s25i6mE4e/?t=107.4&vd_source=2cfdc5cfdf42835fa63915cf5221cc18)

[![Video Cover](https://github.com/JaggerYu-ArchAI/archai-revitmcp-dynamo/blob/main/.github/preview.png?raw=true)](https://www.bilibili.com/video/BV1s25i6mE4e/?t=107.4&vd_source=2cfdc5cfdf42835fa63915cf5221cc18)

---

## ✨ Features

### 1. AI Chat
- Natural language interaction for architectural design questions
- Context-aware multi-turn conversations
- Integrated professional knowledge base

### 2. Code Assistant
- Building code document query and interpretation
- Intelligent code matching and suggestions
- Real-time code compliance checking

### 3. AI-Assisted Modeling
- Automatic Revit component generation from text descriptions
- Parametric design support
- Intelligent geometry generation

### 4. MCP Integration
- Dynamo Machine Learning Compute Protocol support
- Native DeepSeek large model support
- AI24 native language model support

---

## 🎨 Dynamo Visual Interface

ArchAI provides an intuitive Dynamo node interface with visual input/output:

| Node Type | Description |
|---------|---------|
| **AIChat** | AI chat interaction node with text input/output |
| **MCPGeneration** | AI generation node in MCP mode |
| **MarkdownViewer** | Markdown format result display |
| **SpecQuery** | Specification document query node |
| **SpecList** | Specification list management node |
| **RandomGeneration** | Random generation helper node |
| **McpToolWhitelist** | MCP tool whitelist management |

---

## 📁 Project Structure

```
ArchAI/
├── ArchAI_Samples/          # Sample files
│   ├── AI 智能问答.dyn       # AI chat sample
│   ├── AI 规范助手.dyn       # Code assistant sample
│   ├── AI 辅助建模.dyn       # AI modeling sample
│   └── AI 辅助建模MCP.dyn    # MCP mode sample
├── dyf/                      # Dynamo node definitions
│   ├── AIChat.dyf            # AI chat node
│   ├── MCPGeneration.dyf     # MCP generation node
│   ├── MarkdownViewer.dyf    # Markdown viewer node
│   ├── McpToolWhitelist.dyf  # MCP whitelist node
│   ├── RandomGeneration.dyf  # Random generation node
│   ├── SpecList.dyf          # Spec list node
│   └── SpecQuery.dyf         # Spec query node
├── revit_mcp_tools/          # Revit MCP tools
│   ├── config.py             # Configuration management
│   ├── main.py               # Main entry
│   ├── mcp_handler.py        # MCP handler
│   └── revit_basic_tools.py  # Revit basic tools
├── specification/            # Specification documents
│   ├── assets/               # Specification files
│   └── tools/                # Specification tools
└── extra/lib/                # Third-party libraries
```

---

## 🚀 Quick Start

### Requirements
- Revit 2024
- Dynamo 2.17+

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/JaggerYu-ArchAI/archai-revitmcp-dynamo.git
   ```

2. **Configure API Key**
   - Edit `ArchAI_Samples/api_key.txt` file
   - Enter your **DeepSeek API KEY** (DeepSeek is the default model)

3. **Open with Dynamo Player**
   - Open Dynamo Player in Revit
   - Select sample files from `ArchAI_Samples/` directory

4. **Run Samples**
   - Open `AI 智能问答.dyn` sample
   - Input questions and click run

---

## 🛠️ Tech Stack

- **Platform**: Autodesk Revit 2024 + Dynamo
- **Language**: Python 3.9
- **AI Framework**: DeepSeek API (default) / OpenAI API
- **MCP**: Dynamo Machine Learning Compute Protocol

---

## � License

MIT License

---

## 🤝 Contributing

Welcome to submit Issues and Pull Requests!

---

## 📞 Contact

For questions or suggestions, please contact:
- GitHub Issues: [Submit Issue](https://github.com/JaggerYu-ArchAI/archai-revitmcp-dynamo/issues)

---

*Built with ❤️ for BIM Community*
