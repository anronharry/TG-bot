# Telegram AI Bot 部署指南

本文档提供了如何在本地测试环境和云端环境之间切换部署 Telegram AI Bot 的详细说明。

## 配置文件说明

项目提供了三种不同的配置文件，用于不同的部署场景：

1. **docker-compose-full.yml**: 使用云端服务 (Aiven PostgreSQL 和 Upstash Redis)
2. **docker-compose-local.yml**: 使用本地服务 (本地 PostgreSQL 和 Redis)
3. **docker-compose-auto.yml**: 根据环境变量自动选择使用本地或云端服务

## 环境变量设置

在使用任何配置文件之前，请先创建 `.env` 文件（基于 `env.example`）并设置必要的环境变量：

```bash
cp env.example .env
```

然后编辑 `.env` 文件，设置以下关键变量：

- `TELEGRAM_BOT_TOKEN`: 您的 Telegram Bot Token
- `TELEGRAM_ADMIN_IDS`: 管理员用户 ID 列表
- `ENCRYPTION_KEY`: 32 字符加密密钥

### 云端服务配置

如果使用 Aiven PostgreSQL 和 Upstash Redis，请设置：

```
# 环境选择
ENVIRONMENT=cloud

# Aiven PostgreSQL 配置
AIVEN_PG_HOST=your-aiven-postgres-host.aivencloud.com
AIVEN_PG_PORT=12345
AIVEN_PG_DATABASE=defaultdb
AIVEN_PG_USER=avnadmin
AIVEN_PG_PASSWORD=your-aiven-postgres-password

# Upstash Redis 配置
UPSTASH_REDIS_HOST=your-upstash-redis-host.upstash.io
UPSTASH_REDIS_PORT=12345
UPSTASH_REDIS_USER=default
UPSTASH_REDIS_PASSWORD=your-upstash-redis-password
```

### 本地测试配置

如果要使用本地服务进行测试，请设置：

```
# 环境选择
ENVIRONMENT=local

# 本地 PostgreSQL 配置
LOCAL_PG_HOST=postgres
LOCAL_PG_PORT=5432
LOCAL_PG_DATABASE=telegram_ai_bot
LOCAL_PG_USER=user
LOCAL_PG_PASSWORD=password

# 本地 Redis 配置
LOCAL_REDIS_HOST=redis
LOCAL_REDIS_PORT=6379
```

## 部署方法

### 方法 1: 使用云端服务 (Aiven PostgreSQL 和 Upstash Redis)

```bash
# 确保 ENVIRONMENT=cloud 在 .env 文件中
docker-compose -f docker-compose-full.yml up -d
```

### 方法 2: 使用本地服务进行测试

```bash
# 确保 ENVIRONMENT=local 在 .env 文件中
docker-compose -f docker-compose-local.yml up -d
```

### 方法 3: 使用自动切换配置

```bash
# 根据 ENVIRONMENT 环境变量自动选择
docker-compose -f docker-compose-auto.yml up -d

# 如果要明确使用本地服务，可以使用 profiles
docker-compose -f docker-compose-auto.yml --profile local up -d
```

## 管理工具访问

无论使用哪种部署方式，您都可以通过以下地址访问管理工具：

- **pgAdmin**: http://localhost:8080
  - 登录凭据: admin@example.com / admin
  - 连接到 PostgreSQL 数据库 (本地或 Aiven)

- **RedisInsight**: http://localhost:8001
  - 添加新连接以连接到 Redis 服务 (本地或 Upstash)

## 数据库管理

### 连接到 Aiven PostgreSQL

在 pgAdmin 中添加新服务器:
1. 主机: `your-aiven-postgres-host.aivencloud.com`
2. 端口: `12345` (您的 Aiven 端口)
3. 数据库: `defaultdb`
4. 用户名: `avnadmin`
5. 密码: 您的 Aiven 密码

### 连接到本地 PostgreSQL

在 pgAdmin 中添加新服务器:
1. 主机: `postgres` (如果从容器内连接) 或 `localhost` (如果从主机连接)
2. 端口: `5432`
3. 数据库: `telegram_ai_bot`
4. 用户名: `user`
5. 密码: `password`

## Redis 管理

### 连接到 Upstash Redis

在 RedisInsight 中添加新连接:
1. 主机: `your-upstash-redis-host.upstash.io`
2. 端口: 您的 Upstash 端口
3. 用户名: `default`
4. 密码: 您的 Upstash 密码

### 连接到本地 Redis

在 RedisInsight 中添加新连接:
1. 主机: `redis` (如果从容器内连接) 或 `localhost` (如果从主机连接)
2. 端口: `6379`
3. 无需用户名和密码

## 故障排除

如果遇到连接问题:

1. **检查环境变量**: 确保 `.env` 文件中的连接信息正确
2. **检查网络**: 确保您的防火墙允许必要的连接
3. **检查容器状态**: `docker-compose ps` 查看容器是否正常运行
4. **查看日志**: `docker-compose logs bot` 检查应用程序日志

## 在开发和生产环境之间切换

为了方便在开发和生产环境之间切换，您可以创建两个不同的 `.env` 文件:

```bash
# 创建开发环境配置
cp .env .env.dev
# 创建生产环境配置
cp .env .env.prod
```

然后，在启动服务时指定要使用的环境文件:

```bash
# 使用开发环境配置
docker-compose --env-file .env.dev -f docker-compose-auto.yml up -d

# 使用生产环境配置
docker-compose --env-file .env.prod -f docker-compose-auto.yml up -d
```

这样，您就可以轻松地在本地测试环境和云端生产环境之间切换，而无需每次都修改配置文件。
