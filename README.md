# APOS - 通用型 AI Agent

APOS 是一个强大的通用型 AI Agent 项目，能够帮助用户完成各种复杂任务。它采用现代化的前后端分离架构，支持工具调用、历史记录、多模态交互等功能。

## 🚀 项目特性

- **🤖 智能对话**: 基于大语言模型的智能对话系统
- **🔧 工具调用**: 支持多种内置工具和自定义 MCP 工具
- **📚 历史记录**: 完整的对话历史记录管理
- **🎨 现代界面**: 基于 React + Tailwind CSS 的现代化用户界面
- **🔄 实时交互**: 实时的前后端通信和状态更新
- **📱 响应式设计**: 支持桌面和移动设备
- **🌐 多模态支持**: 支持文本和图片的多模态交互

## 📁 项目结构

```
APOS/
├── backend/                 # 后端服务
│   ├── app.py              # 主应用入口
│   ├── config/             # 配置模块
│   │   └── settings.py     # 应用配置
│   ├── core/               # 核心模块
│   │   ├── agent.py        # Agent 核心逻辑
│   │   ├── api.py          # API 路由
│   │   ├── history_manager.py  # 历史记录管理
│   │   └── llm_client.py   # LLM 客户端
│   ├── tools/              # 工具系统
│   │   ├── base_tool.py    # 工具基类
│   │   ├── tool_manager.py # 工具管理器
│   │   ├── builtin/        # 内置工具
│   │   └── mcp/            # MCP 工具
│   ├── utils/              # 工具模块
│   │   └── logger.py       # 日志工具
│   ├── requirements.txt    # Python 依赖
│   ├── .env.example        # 环境变量示例
│   └── .env                # 环境变量配置
├── frontend/               # 前端应用
│   └── apos-frontend/      # React 应用
│       ├── src/            # 源代码
│       ├── public/         # 静态资源
│       └── package.json    # 前端依赖
├── test_api.py             # API 测试脚本
├── todo.md                 # 项目待办事项
└── README.md               # 项目说明文档
```

## 🛠️ 内置工具

APOS 提供了以下内置工具：

1. **web_search** - 网络搜索工具
2. **file_operations** - 文件操作工具
3. **calculator** - 数学计算工具
4. **weather** - 天气查询工具
5. **time_utils** - 时间处理工具

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Node.js 20+
- npm 或 pnpm

### 1. 克隆项目

```bash
git clone <repository-url>
cd APOS
```

### 2. 配置后端

```bash
cd backend

# 安装依赖
pip3 install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置你的 API 密钥和配置
```

### 3. 配置前端

```bash
cd frontend/apos-frontend

# 安装依赖
npm install
# 或使用 pnpm
pnpm install
```

### 4. 启动服务

#### 启动后端服务

```bash
cd backend
python3 app.py
```

后端服务将在 `http://localhost:8880` 启动

#### 启动前端服务

```bash
cd frontend/apos-frontend
npm run dev -- --host
# 或使用 pnpm
pnpm run dev --host
```

前端服务将在 `http://localhost:5173` 启动

### 5. 访问应用

打开浏览器访问 `http://localhost:5173` 即可使用 APOS。

## ⚙️ 配置说明

### 后端配置 (.env)

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_API_MODEL=gpt-3.5-turbo
DEBUG=True
LOG_LEVEL=INFO
MAX_HISTORY_LENGTH=100
```

### 配置参数说明

- `OPENAI_API_KEY`: OpenAI API 密钥
- `OPENAI_API_BASE`: API 基础地址
- `OPENAI_API_MODEL`: 使用的模型名称
- `DEBUG`: 是否开启调试模式
- `LOG_LEVEL`: 日志级别
- `MAX_HISTORY_LENGTH`: 最大历史记录长度

## 🔧 API 接口

### 健康检查

```http
GET /api/health
```

### 聊天接口

```http
POST /api/chat
Content-Type: application/json

{
  "message": "用户消息",
  "session_id": "会话ID"
}
```

### 获取工具列表

```http
GET /api/tools
```

### 获取历史记录

```http
GET /api/history/{session_id}
```

### 清除历史记录

```http
DELETE /api/clear/{session_id}
```

## 🧪 测试

运行 API 测试：

```bash
python3 test_api.py
```

测试脚本会自动测试所有 API 接口的功能。

## 🔌 扩展工具

### 添加内置工具

1. 在 `backend/tools/builtin/` 目录下创建新的工具文件
2. 继承 `BaseTool` 类并实现必要的方法
3. 在 `tool_manager.py` 中注册新工具

### 添加 MCP 工具

1. 在 `backend/tools/mcp/` 目录下创建 JSON 配置文件
2. 配置工具的名称、描述、参数和端点信息
3. 工具管理器会自动加载配置

## 📝 开发说明

### 工具调用流程

1. 用户发送消息到前端
2. 前端调用后端 `/api/chat` 接口
3. Agent 分析消息并决定是否需要调用工具
4. 如需调用工具，使用 XML 格式：
   ```xml
   <tool_call>
   {
     "tool": "工具名称",
     "parameters": {
       "参数名": "参数值"
     }
   }
   </tool_call>
   ```
5. 工具管理器执行工具并返回结果
6. Agent 根据结果继续处理或完成任务

### 日志系统

APOS 使用彩色日志系统，支持不同级别的日志输出：

- 🔵 DEBUG: 调试信息
- 🟢 INFO: 一般信息
- 🟡 WARNING: 警告信息
- 🔴 ERROR: 错误信息
- 🟣 CRITICAL: 严重错误

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

## 🙏 致谢

感谢所有为 APOS 项目做出贡献的开发者和用户。

---

**APOS** - 让 AI 助手更智能，让任务处理更简单！

