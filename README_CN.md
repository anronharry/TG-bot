# 云机子AI机器人

一个基于模块化架构的现代化Telegram AI机器人，具备云机子角色设定、多模型支持、自定义API集成和管理员功能等特色。

## 🚀 主要特性

- **🧘 云机子角色**：独特的禅意对话体验，自称"本座"或"贫道"
- **🤖 多AI模型支持**：支持GPT-4o、Claude等多种AI模型
- **🔌 自定义API支持**：连接任何兼容OpenAI的API服务
- **👥 管理员功能**：支持封禁/解封用户，群组管理
- **💾 数据持久化**：用户选择和封禁状态自动保存
- **⚡ 异步高性能**：基于asyncio的全异步架构
- **🐳 Docker部署**：一键启动，简单易用

## 🏗️ 架构设计

### 技术栈

- **Python 3.11+** 配合 asyncio
- **python-telegram-bot 20.0+** 用于Telegram API交互
- **SQLAlchemy** 用于数据库操作
- **aiohttp** 用于外部API调用
- **PostgreSQL** 用于数据存储
- **Redis** 用于缓存
- **Docker** 用于容器化部署

### 项目结构

```
telegram-ai-bot/
├── ai_bot.py              # 主入口文件
├── app/                   # 应用模块
│   ├── core/              # 核心功能
│   │   ├── bot_config.py  # 机器人配置
│   │   ├── config.py      # 应用配置
│   │   ├── custom_apis.py # 自定义API支持
│   │   ├── database.py    # 数据库连接
│   │   ├── redis_client.py # Redis连接
│   │   └── security.py    # 安全工具
│   ├── decorators.py      # 函数装饰器
│   ├── handlers/          # 消息处理器
│   │   ├── admin.py       # 管理员命令
│   │   ├── common.py      # 基本命令
│   │   ├── custom_api.py  # 自定义API配置
│   │   ├── message.py     # 消息处理
│   │   ├── model.py       # 模型选择
│   │   └── user.py        # 用户命令
│   ├── models/            # 数据模型
│   │   └── schema.py      # 数据库模式
│   ├── services/          # 服务层
│   │   ├── ai_models.py   # AI模型服务
│   │   ├── chat_service.py # 聊天历史
│   │   ├── user_custom_models.py # 用户自定义模型
│   │   └── user_service.py # 用户管理
│   └── utils/             # 工具函数
│       ├── message_utils.py # 消息工具
│       ├── model_utils.py  # 模型工具
│       └── user_utils.py   # 用户工具
├── docker-compose.yml     # Docker配置
├── Dockerfile             # Docker镜像构建
└── env.example            # 环境变量模板
```

## 📋 环境要求

- Python 3.11+
- Docker & Docker Compose（推荐）
- Telegram Bot Token
- AI API密钥

## 🚀 快速开始

### 方法一：Docker Compose部署（推荐）

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd telegram-ai-bot
   ```

2. **配置环境变量**
   ```bash
   # 复制配置模板
   cp env.example .env
   
   # 编辑配置文件
   nano .env
   ```
   
   修改以下内容：
   ```env
   TELEGRAM_BOT_TOKEN=你的机器人Token
   TELEGRAM_ADMIN_IDS=[你的用户ID]
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/telegrambot
   REDIS_URL=redis://redis:6379/0
   ENCRYPTION_KEY=你的32字符加密密钥
   ```

3. **启动服务**
   ```bash
   docker-compose up -d
   ```

4. **开始使用**
   - 在Telegram中搜索你的机器人
   - 发送 `/start` 开始对话
   - 发送 `/setmodel` 选择AI模型

### 方法二：本地运行

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   export TELEGRAM_BOT_TOKEN="你的机器人Token"
   export TELEGRAM_ADMIN_IDS="[你的用户ID]"
   export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/telegrambot"
   export REDIS_URL="redis://localhost:6379/0"
   export ENCRYPTION_KEY="你的32字符加密密钥"
   ```

3. **运行机器人**
   ```bash
   python ai_bot.py
   ```

## 📋 命令列表

### 用户命令

| 命令 | 描述 | 示例 |
|------|------|------|
| `/start` | 显示欢迎信息 | `/start` |
| `/help` | 显示帮助信息 | `/help` |
| `/setmodel` | 选择AI模型 | `/setmodel` |
| `/clear` | 清除对话历史 | `/clear` |
| `/customapi` | 配置自定义API | `/customapi` |
| `/myapis` | 列出你的自定义API | `/myapis` |
| `/testapi` | 测试API连接 | `/testapi <端点> <密钥> <模型>` |

### 管理员命令

| 命令 | 描述 | 示例 |
|------|------|------|
| `.ban` | 封禁用户（引用消息） | 引用消息后发送 `.ban` |
| `.ban <ID>` | 通过ID封禁用户 | `.ban 123456789` |
| `.unban` | 解封用户（引用消息） | 引用消息后发送 `.unban` |
| `.unban <ID>` | 通过ID解封用户 | `.unban 123456789` |
| `/adminhelp` | 显示管理员帮助 | `/adminhelp` |

## 🧘 云机子角色设定

云机子是一位避世清修的得道高人，具有独特的语言风格：

### 语言特点
- **自称**："本座"或"贫道"
- **称呼他人**："小友"或"汝"
- **语气**：超然物外，平静无波
- **表达**：多用比喻与譬如，语带禅意与玄机
- **态度**：于凡尘俗事略示不屑或了然

## 🔌 自定义API配置

机器人支持连接任何兼容OpenAI的API服务：

1. **开始配置**
   - 发送 `/customapi` 开始配置过程
   - 按照步骤指引设置你的自定义API

2. **所需信息**
   - API端点（URL）
   - API密钥
   - 模型名称
   - 自定义配置名称

3. **管理自定义API**
   - 使用 `/myapis` 列出你的自定义API配置
   - 使用 `/testapi` 测试API连接

## 🔧 管理命令

```bash
# 查看服务状态
docker-compose ps

# 查看机器人日志
docker-compose logs -f

# 重启机器人
docker-compose restart

# 停止所有服务
docker-compose down

# 启动所有服务
docker-compose up -d
```

## 🔍 故障排除

### 常见问题

1. **机器人无响应**
   ```bash
   # 检查Docker服务
   docker-compose ps
   
   # 查看日志
   docker-compose logs
   ```

2. **AI模型选择失败**
   - 检查网络连接
   - 确认API密钥配置

3. **管理员命令无效**
   - 确认用户ID在管理员列表
   - 检查群组管理员权限

## 📞 支持

如有问题，请：
1. 查看日志：`docker-compose logs`
2. 检查配置：确认环境变量设置正确
3. 重启服务：`docker-compose restart`

---

**享受与云机子的禅意对话吧！** 🧘‍♂️✨