# Agent-Camel V2

基于官方 CAMEL-AI 框架的智能Agent应用。

## 项目结构

```
agent-camel-v2/
├── README.md
├── requirements.txt
├── .env
├── main.py
├── config/
│   ├── __init__.py
│   └── settings.py
├── agents/
│   ├── __init__.py
│   ├── base.py
│   ├── coordinator.py
│   ├── model_provider.py
│   └── roles/
├── tools/
│   ├── __init__.py
│   └── library.py
├── memory/
│   ├── __init__.py
│   └── manager.py
└── examples/
    ├── __init__.py
    ├── travel_planner.py
    └── camel_travel_planner.py
```

## 安装依赖

```bash
pip install -r requirements.txt
```

## 环境配置

项目使用 `.env` 文件来管理环境变量。请根据需要修改 `.env` 文件中的配置项：

```env
# OpenAI Configuration
OPENAI_API_KEY=sk-...               # 你的OpenAI API密钥
OPENAI_BASE_URL=                    # 可选，OpenAI API的基础URL（用于代理或本地部署）

# Ollama Configuration (for local deployment)
OLLAMA_BASE_URL=http://localhost:11434  # Ollama服务地址
OLLAMA_MODEL_NAME=llama2            # Ollama模型名称

# 其他配置...
```

### 使用本地Ollama模型

要使用本地部署的Ollama模型，请确保：

1. 已安装并运行Ollama服务
2. 在 `.env` 文件中配置 `OLLAMA_BASE_URL`（默认为 http://localhost:11434）
3. 拉取所需的模型，例如：`ollama pull llama2`

### 使用OpenAI兼容API

如果使用与OpenAI兼容的API（如本地部署的模型服务），可以通过设置 `OPENAI_BASE_URL` 来配置：

```env
OPENAI_API_KEY=sk-...               # API密钥（如果需要）
OPENAI_BASE_URL=http://localhost:8000/v1  # API服务地址
```

## 运行应用

```bash
# 交互式运行
python main.py

# 直接传入参数运行
python main.py "我想在10月去日本旅行，预算5000美元"
```

## 项目组件说明

本项目基于官方的 [CAMEL-AI](https://github.com/camel-ai/camel) 框架构建，该框架专注于通过角色扮演和对话促进大语言模型的心智探索，适用于构建复杂的多智能体协作系统。

### 配置模块 (config/)
存储应用配置，包括API密钥、数据库连接等设置。

### 智能体模块 (agents/)
包含基础智能体类和任务协调器：
- `base.py`: 基础智能体抽象类
- `coordinator.py`: 任务协调器，负责分配任务和管理智能体协作
- `model_provider.py`: 模型提供者，支持多种模型服务（OpenAI、Ollama等）

### 工具模块 (tools/)
包含工具库，为智能体提供外部功能调用能力。

### 内存模块 (memory/)
包含内存管理器，负责存储和检索会话上下文及历史记录。

### 示例模块 (examples/)
包含应用示例：
- `travel_planner.py`: 原始实现的旅行规划助手示例
- `camel_travel_planner.py`: 基于官方CAMEL-AI框架的旅行规划助手示例

## 支持的模型服务

1. **OpenAI**: 支持GPT-3.5、GPT-4等模型
2. **Ollama**: 支持本地部署的大模型（如Llama系列）

通过配置环境变量，可以轻松切换不同的模型服务提供商。

## CAMEL-AI 框架优势

CAMEL-AI框架提供了以下优势：

1. **多智能体协作**: 支持多个智能体之间的协作与通信
2. **角色扮演**: 智能体可以扮演不同角色以完成复杂任务
3. **任务分解**: 能够将复杂任务分解为子任务并分配给合适的智能体
4. **上下文管理**: 自动管理对话上下文和历史记录
5. **工具集成**: 支持集成外部工具和API