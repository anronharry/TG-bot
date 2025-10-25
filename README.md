# 云机子AI机器人

一个基于模块化架构的现代化Telegram AI机器人，具备云机子角色设定、多模型支持、自定义API集成和管理员功能等特色。

[English Version](#english-version)

## 🚀 主要特性

- **🧘 云机子角色**：独特的禅意对话体验，自称"本座"或"贫道"
- **🤖 多AI模型支持**：支持GPT-4o、Claude等多种AI模型
- **🔌 自定义API支持**：连接任何兼容OpenAI的API服务
- **👥 管理员功能**：支持封禁/解封用户，群组管理
- **💾 数据持久化**：用户选择和封禁状态自动保存
- **⚡ 异步高性能**：基于asyncio的全异步架构
- **🐳 灵活部署**：支持本地测试和云服务部署

## 🏗️ 架构设计

### 技术栈

- **Python 3.11+** 配合 asyncio
- **python-telegram-bot 20.0+** 用于Telegram API交互
- **SQLAlchemy** 用于数据库操作
- **aiohttp** 用于外部API调用
- **PostgreSQL** 用于数据存储 (支持本地或Aiven云服务)
- **Redis** 用于缓存 (支持本地或Upstash云服务)
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
│   ├── models/            # 数据模型
│   ├── services/          # 服务层
│   └── utils/             # 工具函数
├── docker-compose-auto.yml  # 智能切换配置
├── docker-compose-full.yml  # 云端部署配置
├── docker-compose-local.yml # 本地测试配置
├── docker-compose.yml     # 简化版配置
├── Dockerfile             # Docker镜像构建
└── env.example            # 环境变量模板
```

## 📋 环境要求

- Python 3.11+
- Docker & Docker Compose（推荐）
- Telegram Bot Token
- AI API密钥
- 可选：Aiven PostgreSQL 和 Upstash Redis 账户

## 🚀 部署选项

本项目提供多种部署方式，可根据需求选择：

### 1. 本地测试部署

适合开发和测试，使用本地PostgreSQL和Redis服务。

```bash
# 复制配置模板
cp env.example .env

# 编辑配置文件，设置ENVIRONMENT=local
nano .env

# 启动本地测试环境
docker-compose -f docker-compose-local.yml up -d
```

### 2. 云服务部署

适合生产环境，使用Aiven PostgreSQL和Upstash Redis云服务。

```bash
# 复制配置模板
cp env.example .env

# 编辑配置文件，设置ENVIRONMENT=cloud并填写云服务连接信息
nano .env

# 启动云服务环境
docker-compose -f docker-compose-full.yml up -d
```

### 3. 智能切换部署

根据环境变量自动选择使用本地服务或云服务。

```bash
# 复制配置模板
cp env.example .env

# 编辑配置文件，设置ENVIRONMENT=local或cloud
nano .env

# 启动自动切换环境
docker-compose -f docker-compose-auto.yml up -d

# 如果要明确使用本地服务，可以使用profiles
docker-compose -f docker-compose-auto.yml --profile local up -d
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

## 🌐 数据库配置

### 本地PostgreSQL

默认配置（在docker-compose-local.yml中）：
```
主机：postgres
端口：5432
数据库：telegram_ai_bot
用户名：user
密码：password
```

### Aiven PostgreSQL

在.env文件中配置：
```
AIVEN_PG_HOST=your-aiven-postgres-host.aivencloud.com
AIVEN_PG_PORT=12345
AIVEN_PG_DATABASE=defaultdb
AIVEN_PG_USER=avnadmin
AIVEN_PG_PASSWORD=your-aiven-postgres-password
```

## 🔄 缓存配置

### 本地Redis

默认配置（在docker-compose-local.yml中）：
```
主机：redis
端口：6379
```

### Upstash Redis

在.env文件中配置：
```
UPSTASH_REDIS_HOST=your-upstash-redis-host.upstash.io
UPSTASH_REDIS_PORT=12345
UPSTASH_REDIS_USER=default
UPSTASH_REDIS_PASSWORD=your-upstash-redis-password
```

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

4. **数据库连接问题**
   - 本地部署：检查PostgreSQL容器是否正常运行
   - 云服务部署：检查Aiven连接信息是否正确

5. **Redis连接问题**
   - 本地部署：检查Redis容器是否正常运行
   - 云服务部署：检查Upstash连接信息是否正确

## 📞 支持

如有问题，请：
1. 查看日志：`docker-compose logs`
2. 检查配置：确认环境变量设置正确
3. 重启服务：`docker-compose restart`

---

**享受与云机子的禅意对话吧！** 🧘‍♂️✨

---

<a name="english-version"></a>
# Yun Jizi AI Bot (English Version)

A modern, high-performance Telegram AI bot with a modular architecture, featuring the unique "Yun Jizi" character with Zen-style conversations, multi-model support, custom API integration, and admin management capabilities.

## 🚀 Features

- **🧘 Yun Jizi Character**: Unique Zen-style conversation experience, referring to self as "本座" or "贫道"
- **🤖 Multiple AI Models**: Support for GPT-4o, Claude, and other AI models
- **🔌 Custom API Support**: Connect to any OpenAI-compatible API service
- **👥 Admin Management**: User ban/unban functionality with group management
- **💾 Data Persistence**: Automatic saving of user preferences and ban status
- **⚡ Async Architecture**: Built with modern async Python for high performance
- **🐳 Flexible Deployment**: Support for local testing and cloud service deployment

## 🏗️ Architecture

### Technology Stack

- **Python 3.11+** with asyncio
- **python-telegram-bot 20.0+** for Telegram API
- **SQLAlchemy** for database operations
- **aiohttp** for external API calls
- **PostgreSQL** for data storage (local or Aiven cloud service)
- **Redis** for caching (local or Upstash cloud service)
- **Docker** for containerization

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- Telegram Bot Token
- AI API Keys
- Optional: Aiven PostgreSQL and Upstash Redis accounts

## 🚀 Deployment Options

This project offers multiple deployment options:

### 1. Local Testing Deployment

Ideal for development and testing, using local PostgreSQL and Redis services.

```bash
# Copy configuration template
cp env.example .env

# Edit configuration file, set ENVIRONMENT=local
nano .env

# Start local testing environment
docker-compose -f docker-compose-local.yml up -d
```

### 2. Cloud Service Deployment

Ideal for production, using Aiven PostgreSQL and Upstash Redis cloud services.

```bash
# Copy configuration template
cp env.example .env

# Edit configuration file, set ENVIRONMENT=cloud and fill cloud service connection info
nano .env

# Start cloud service environment
docker-compose -f docker-compose-full.yml up -d
```

### 3. Auto-switching Deployment

Automatically selects local or cloud services based on environment variables.

```bash
# Copy configuration template
cp env.example .env

# Edit configuration file, set ENVIRONMENT=local or cloud
nano .env

# Start auto-switching environment
docker-compose -f docker-compose-auto.yml up -d

# If you want to explicitly use local services, you can use profiles
docker-compose -f docker-compose-auto.yml --profile local up -d
```

## 📋 Commands

Please refer to the Chinese section above for the complete list of user and admin commands.

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Verify configuration: Ensure environment variables are set correctly
3. Restart service: `docker-compose restart`

---

**Enjoy your Zen conversations with Yun Jizi!** 🧘‍♂️✨