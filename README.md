# Yun Jizi AI Bot

A modern, high-performance Telegram AI bot with a modular architecture, featuring the unique "Yun Jizi" character with Zen-style conversations, multi-model support, custom API integration, and admin management capabilities.

## 🚀 Features

- **🧘 Yun Jizi Character**: Unique Zen-style conversation experience, referring to self as "本座" or "贫道"
- **🤖 Multiple AI Models**: Support for GPT-4o, Claude, and other AI models
- **🔌 Custom API Support**: Connect to any OpenAI-compatible API service
- **👥 Admin Management**: User ban/unban functionality with group management
- **💾 Data Persistence**: Automatic saving of user preferences and ban status
- **⚡ Async Architecture**: Built with modern async Python for high performance
- **🐳 Docker Support**: Easy deployment with Docker Compose

## 🏗️ Architecture

### Technology Stack

- **Python 3.11+** with asyncio
- **python-telegram-bot 20.0+** for Telegram API
- **SQLAlchemy** for database operations
- **aiohttp** for external API calls
- **PostgreSQL** for data storage
- **Redis** for caching
- **Docker** for containerization

### Project Structure

```
telegram-ai-bot/
├── ai_bot.py              # Main entry point
├── app/                   # Application modules
│   ├── core/              # Core functionality
│   │   ├── bot_config.py  # Bot configuration
│   │   ├── config.py      # Application config
│   │   ├── custom_apis.py # Custom API support
│   │   ├── database.py    # Database connection
│   │   ├── redis_client.py # Redis connection
│   │   └── security.py    # Security utilities
│   ├── decorators.py      # Function decorators
│   ├── handlers/          # Message handlers
│   │   ├── admin.py       # Admin commands
│   │   ├── common.py      # Basic commands
│   │   ├── custom_api.py  # Custom API config
│   │   ├── message.py     # Message processing
│   │   ├── model.py       # Model selection
│   │   └── user.py        # User commands
│   ├── models/            # Data models
│   │   └── schema.py      # Database schema
│   ├── services/          # Service layer
│   │   ├── ai_models.py   # AI model service
│   │   ├── chat_service.py # Chat history
│   │   ├── user_custom_models.py # User custom models
│   │   └── user_service.py # User management
│   └── utils/             # Utility functions
│       ├── message_utils.py # Message utilities
│       ├── model_utils.py  # Model utilities
│       └── user_utils.py   # User utilities
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Docker image build
└── env.example            # Environment variables template
```

## 📋 Prerequisites

- Python 3.11+
- Docker & Docker Compose (recommended)
- Telegram Bot Token
- AI API Keys

## 🚀 Quick Start

### Method 1: Docker Compose Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd telegram-ai-bot
   ```

2. **Configure environment variables**
   ```bash
   # Copy configuration template
   cp env.example .env
   
   # Edit configuration file
   nano .env
   ```
   
   Modify the following content:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token
   TELEGRAM_ADMIN_IDS=[your_user_id]
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/telegrambot
   REDIS_URL=redis://redis:6379/0
   ENCRYPTION_KEY=your_32_character_encryption_key
   ```

3. **Start services**
   ```bash
   docker-compose up -d
   ```

4. **Start using**
   - Search for your bot in Telegram
   - Send `/start` to begin conversation
   - Send `/setmodel` to select AI model

### Method 2: Local Run

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**
   ```bash
   export TELEGRAM_BOT_TOKEN="your_bot_token"
   export TELEGRAM_ADMIN_IDS="[your_user_id]"
   export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/telegrambot"
   export REDIS_URL="redis://localhost:6379/0"
   export ENCRYPTION_KEY="your_32_character_encryption_key"
   ```

3. **Run the bot**
   ```bash
   python ai_bot.py
   ```

## 📋 Commands

### User Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Show welcome message | `/start` |
| `/help` | Show help information | `/help` |
| `/setmodel` | Select AI model | `/setmodel` |
| `/clear` | Clear conversation history | `/clear` |
| `/customapi` | Configure custom API | `/customapi` |
| `/myapis` | List your custom APIs | `/myapis` |
| `/testapi` | Test API connection | `/testapi <endpoint> <key> <model>` |

### Admin Commands

| Command | Description | Example |
|---------|-------------|---------|
| `.ban` | Ban user (reply to message) | Reply to message and send `.ban` |
| `.ban <ID>` | Ban user by ID | `.ban 123456789` |
| `.unban` | Unban user (reply to message) | Reply to message and send `.unban` |
| `.unban <ID>` | Unban user by ID | `.unban 123456789` |
| `/adminhelp` | Show admin help | `/adminhelp` |

## 🧘 Yun Jizi Character

Yun Jizi is a reclusive Taoist master with unique language characteristics:

### Language Features
- **Self-reference**: "本座" (this seat) or "贫道" (this humble Taoist)
- **Addressing others**: "小友" (young friend) or "汝" (thou)
- **Tone**: Detached from worldly affairs, calm and serene
- **Expression**: Uses metaphors and analogies, Zen-like wisdom
- **Attitude**: Slightly dismissive or understanding of worldly matters

## 🔌 Custom API Configuration

The bot supports connecting to any OpenAI-compatible API service:

1. **Start configuration**
   - Send `/customapi` to start the configuration process
   - Follow the step-by-step guide to set up your custom API

2. **Required information**
   - API endpoint (URL)
   - API key
   - Model name
   - Custom name for your configuration

3. **Managing custom APIs**
   - Use `/myapis` to list your custom API configurations
   - Use `/testapi` to test API connections

## 🔧 Management Commands

```bash
# Check service status
docker-compose ps

# View bot logs
docker-compose logs -f

# Restart bot
docker-compose restart

# Stop all services
docker-compose down

# Start all services
docker-compose up -d
```

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding**
   ```bash
   # Check Docker services
   docker-compose ps
   
   # View logs
   docker-compose logs
   ```

2. **AI model selection failed**
   - Check network connection
   - Verify API key configuration

3. **Admin commands not working**
   - Confirm user ID in admin list
   - Check group admin permissions

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Verify configuration: Ensure environment variables are set correctly
3. Restart service: `docker-compose restart`

---

**Enjoy your Zen conversations with Yun Jizi!** 🧘‍♂️✨